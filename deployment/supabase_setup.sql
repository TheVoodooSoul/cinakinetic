-- CinaKinetic.com Database Schema for Supabase

-- Enable Row Level Security
ALTER DATABASE postgres SET row_security = on;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    tier TEXT DEFAULT 'starter' CHECK (tier IN ('starter', 'pro', 'studio', 'enterprise')),
    credits INTEGER DEFAULT 100,
    total_generations INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Storyboards table
CREATE TABLE public.storyboards (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    nodes JSONB DEFAULT '[]',
    connections JSONB DEFAULT '[]',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- LoRA models table
CREATE TABLE public.lora_models (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    trigger_word TEXT NOT NULL,
    type TEXT CHECK (type IN ('character', 'fighting_style', 'action_pose', 'scene_style')),
    description TEXT,
    training_images_count INTEGER,
    file_url TEXT,
    file_size_mb DECIMAL,
    status TEXT DEFAULT 'training' CHECK (status IN ('pending', 'training', 'completed', 'error')),
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL DEFAULT 0.0,
    is_public BOOLEAN DEFAULT FALSE,
    training_config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Characters table
CREATE TABLE public.characters (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    fighting_style TEXT,
    signature_moves TEXT,
    reference_image_url TEXT,
    lora_model_id UUID REFERENCES public.lora_models(id),
    scenes_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generation history table
CREATE TABLE public.generations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    storyboard_id UUID REFERENCES public.storyboards(id) ON DELETE SET NULL,
    workflow_type TEXT NOT NULL,
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    parameters JSONB,
    loras_used JSONB,
    credits_used INTEGER NOT NULL,
    generation_time_seconds DECIMAL,
    output_url TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Credit transactions table
CREATE TABLE public.credit_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    type TEXT CHECK (type IN ('purchase', 'usage', 'refund', 'bonus')),
    amount INTEGER NOT NULL, -- Positive for credits added, negative for credits used
    description TEXT,
    stripe_payment_id TEXT,
    generation_id UUID REFERENCES public.generations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE public.subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT UNIQUE,
    tier TEXT NOT NULL,
    status TEXT CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX idx_storyboards_user_id ON public.storyboards(user_id);
CREATE INDEX idx_storyboards_created_at ON public.storyboards(created_at);
CREATE INDEX idx_lora_models_user_id ON public.lora_models(user_id);
CREATE INDEX idx_lora_models_type ON public.lora_models(type);
CREATE INDEX idx_lora_models_status ON public.lora_models(status);
CREATE INDEX idx_characters_user_id ON public.characters(user_id);
CREATE INDEX idx_generations_user_id ON public.generations(user_id);
CREATE INDEX idx_generations_created_at ON public.generations(created_at);
CREATE INDEX idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_id ON public.subscriptions(stripe_subscription_id);

-- Row Level Security Policies

-- User profiles: Users can only see and edit their own profile
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Storyboards: Users can only access their own storyboards (unless public)
ALTER TABLE public.storyboards ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own storyboards" ON public.storyboards
    FOR SELECT USING (auth.uid() = user_id OR is_public = true);
CREATE POLICY "Users can create storyboards" ON public.storyboards
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own storyboards" ON public.storyboards
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own storyboards" ON public.storyboards
    FOR DELETE USING (auth.uid() = user_id);

-- LoRA models: Users can only access their own LoRAs (unless public)
ALTER TABLE public.lora_models ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view accessible loras" ON public.lora_models
    FOR SELECT USING (auth.uid() = user_id OR is_public = true);
CREATE POLICY "Users can create loras" ON public.lora_models
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own loras" ON public.lora_models
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own loras" ON public.lora_models
    FOR DELETE USING (auth.uid() = user_id);

-- Characters: Users can only access their own characters
ALTER TABLE public.characters ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own characters" ON public.characters
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create characters" ON public.characters
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own characters" ON public.characters
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own characters" ON public.characters
    FOR DELETE USING (auth.uid() = user_id);

-- Generations: Users can only see their own generations
ALTER TABLE public.generations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own generations" ON public.generations
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create generations" ON public.generations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Credit transactions: Users can only see their own transactions
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own transactions" ON public.credit_transactions
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create transactions" ON public.credit_transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Subscriptions: Users can only see their own subscriptions
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own subscriptions" ON public.subscriptions
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own subscriptions" ON public.subscriptions
    FOR UPDATE USING (auth.uid() = user_id);

-- Functions

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
    );
    
    -- Add welcome credits
    INSERT INTO public.credit_transactions (user_id, type, amount, description)
    VALUES (NEW.id, 'bonus', 100, 'Welcome bonus credits');
    
    RETURN NEW;
END;
$$;

-- Trigger for new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update user credits after transaction
CREATE OR REPLACE FUNCTION public.update_user_credits()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    UPDATE public.user_profiles
    SET credits = credits + NEW.amount
    WHERE id = NEW.user_id;
    
    RETURN NEW;
END;
$$;

-- Trigger to update credits after transaction
DROP TRIGGER IF EXISTS on_credit_transaction ON public.credit_transactions;
CREATE TRIGGER on_credit_transaction
    AFTER INSERT ON public.credit_transactions
    FOR EACH ROW EXECUTE FUNCTION public.update_user_credits();

-- Function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_storyboards_updated_at
    BEFORE UPDATE ON public.storyboards
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_lora_models_updated_at
    BEFORE UPDATE ON public.lora_models
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_characters_updated_at
    BEFORE UPDATE ON public.characters
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Views for analytics (accessible by service role only)

-- Daily usage statistics
CREATE OR REPLACE VIEW public.daily_usage_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_generations,
    SUM(credits_used) as total_credits_used,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(generation_time_seconds) as avg_generation_time,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
FROM public.generations
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- User tier distribution
CREATE OR REPLACE VIEW public.user_tier_stats AS
SELECT 
    tier,
    COUNT(*) as user_count,
    AVG(credits) as avg_credits,
    SUM(total_generations) as total_generations
FROM public.user_profiles
GROUP BY tier;

-- Popular LoRA models
CREATE OR REPLACE VIEW public.popular_loras AS
SELECT 
    l.name,
    l.type,
    l.trigger_word,
    l.usage_count,
    l.rating,
    u.full_name as creator_name
FROM public.lora_models l
JOIN public.user_profiles u ON l.user_id = u.id
WHERE l.is_public = true
ORDER BY l.usage_count DESC, l.rating DESC
LIMIT 50;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;