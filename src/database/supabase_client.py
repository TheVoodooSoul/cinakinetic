import os
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import streamlit as st
from datetime import datetime

class SupabaseClient:
    """Supabase client for CinaKinetic.com"""
    
    def __init__(self):
        # Get credentials from environment or Streamlit secrets
        supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            raise ValueError("Supabase credentials not found")
        
        self.client: Client = create_client(supabase_url, supabase_anon_key)
    
    # User Profile Management
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID"""
        try:
            result = self.client.table('user_profiles').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error fetching user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """Update user profile"""
        try:
            result = self.client.table('user_profiles').update(updates).eq('id', user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating profile: {e}")
            return False
    
    async def get_user_credits(self, user_id: str) -> int:
        """Get user's current credit balance"""
        try:
            result = self.client.table('user_profiles').select('credits').eq('id', user_id).execute()
            return result.data[0]['credits'] if result.data else 0
        except Exception:
            return 0
    
    async def deduct_credits(self, user_id: str, amount: int, description: str, generation_id: Optional[str] = None) -> bool:
        """Deduct credits from user account"""
        try:
            # Create credit transaction
            transaction_data = {
                'user_id': user_id,
                'type': 'usage',
                'amount': -amount,  # Negative for deduction
                'description': description,
                'generation_id': generation_id
            }
            
            result = self.client.table('credit_transactions').insert(transaction_data).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deducting credits: {e}")
            return False
    
    async def add_credits(self, user_id: str, amount: int, description: str, stripe_payment_id: Optional[str] = None) -> bool:
        """Add credits to user account"""
        try:
            transaction_data = {
                'user_id': user_id,
                'type': 'purchase',
                'amount': amount,
                'description': description,
                'stripe_payment_id': stripe_payment_id
            }
            
            result = self.client.table('credit_transactions').insert(transaction_data).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error adding credits: {e}")
            return False
    
    # Storyboard Management
    async def save_storyboard(self, storyboard: Dict) -> Optional[Dict]:
        """Save storyboard to database"""
        try:
            if 'id' in storyboard:
                # Update existing
                result = self.client.table('storyboards').update(storyboard).eq('id', storyboard['id']).execute()
            else:
                # Create new
                result = self.client.table('storyboards').insert(storyboard).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error saving storyboard: {e}")
            return None
    
    async def get_user_storyboards(self, user_id: str) -> List[Dict]:
        """Get all storyboards for a user"""
        try:
            result = self.client.table('storyboards').select('*').eq('user_id', user_id).order('updated_at', desc=True).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching storyboards: {e}")
            return []
    
    async def get_storyboard(self, storyboard_id: str) -> Optional[Dict]:
        """Get specific storyboard"""
        try:
            result = self.client.table('storyboards').select('*').eq('id', storyboard_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error fetching storyboard: {e}")
            return None
    
    async def delete_storyboard(self, storyboard_id: str) -> bool:
        """Delete storyboard"""
        try:
            result = self.client.table('storyboards').delete().eq('id', storyboard_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting storyboard: {e}")
            return False
    
    # LoRA Model Management
    async def save_lora_model(self, lora_data: Dict) -> Optional[Dict]:
        """Save LoRA model information"""
        try:
            result = self.client.table('lora_models').insert(lora_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error saving LoRA model: {e}")
            return None
    
    async def get_user_loras(self, user_id: str) -> List[Dict]:
        """Get all LoRA models for a user"""
        try:
            result = self.client.table('lora_models').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching LoRA models: {e}")
            return []
    
    async def get_public_loras(self, lora_type: Optional[str] = None) -> List[Dict]:
        """Get public LoRA models"""
        try:
            query = self.client.table('lora_models').select('*').eq('is_public', True).eq('status', 'completed')
            
            if lora_type:
                query = query.eq('type', lora_type)
            
            result = query.order('usage_count', desc=True).limit(50).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching public LoRAs: {e}")
            return []
    
    async def update_lora_status(self, lora_id: str, status: str, file_url: Optional[str] = None) -> bool:
        """Update LoRA training status"""
        try:
            updates = {'status': status}
            if file_url:
                updates['file_url'] = file_url
            
            result = self.client.table('lora_models').update(updates).eq('id', lora_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating LoRA status: {e}")
            return False
    
    async def increment_lora_usage(self, lora_id: str) -> bool:
        """Increment LoRA usage count"""
        try:
            # Use RPC function for atomic increment
            result = self.client.rpc('increment_lora_usage', {'lora_id': lora_id}).execute()
            return True
        except Exception:
            return False
    
    # Character Management
    async def save_character(self, character_data: Dict) -> Optional[Dict]:
        """Save character information"""
        try:
            if 'id' in character_data:
                result = self.client.table('characters').update(character_data).eq('id', character_data['id']).execute()
            else:
                result = self.client.table('characters').insert(character_data).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error saving character: {e}")
            return None
    
    async def get_user_characters(self, user_id: str) -> List[Dict]:
        """Get all characters for a user"""
        try:
            result = self.client.table('characters').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching characters: {e}")
            return []
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character"""
        try:
            result = self.client.table('characters').delete().eq('id', character_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting character: {e}")
            return False
    
    # Generation History
    async def save_generation(self, generation_data: Dict) -> Optional[Dict]:
        """Save generation record"""
        try:
            result = self.client.table('generations').insert(generation_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error saving generation: {e}")
            return None
    
    async def get_user_generations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's generation history"""
        try:
            result = self.client.table('generations').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching generations: {e}")
            return []
    
    async def get_generation_stats(self, user_id: str) -> Dict:
        """Get user's generation statistics"""
        try:
            # Get total generations
            total_result = self.client.table('generations').select('id', count='exact').eq('user_id', user_id).execute()
            total_generations = total_result.count
            
            # Get credits used this month
            current_month = datetime.now().strftime('%Y-%m')
            credits_result = self.client.table('credit_transactions').select('amount').eq('user_id', user_id).eq('type', 'usage').gte('created_at', f'{current_month}-01').execute()
            credits_used = sum(-t['amount'] for t in credits_result.data)  # Convert negative to positive
            
            # Get success rate
            success_result = self.client.table('generations').select('success').eq('user_id', user_id).execute()
            success_rate = sum(1 for g in success_result.data if g['success']) / len(success_result.data) if success_result.data else 0
            
            return {
                'total_generations': total_generations or 0,
                'credits_used_this_month': credits_used,
                'success_rate': success_rate * 100
            }
        except Exception as e:
            st.error(f"Error fetching stats: {e}")
            return {'total_generations': 0, 'credits_used_this_month': 0, 'success_rate': 0}
    
    # Subscription Management
    async def create_subscription(self, subscription_data: Dict) -> Optional[Dict]:
        """Create subscription record"""
        try:
            result = self.client.table('subscriptions').insert(subscription_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error creating subscription: {e}")
            return None
    
    async def update_subscription(self, user_id: str, updates: Dict) -> bool:
        """Update subscription"""
        try:
            result = self.client.table('subscriptions').update(updates).eq('user_id', user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating subscription: {e}")
            return False
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's active subscription"""
        try:
            result = self.client.table('subscriptions').select('*').eq('user_id', user_id).eq('status', 'active').execute()
            return result.data[0] if result.data else None
        except Exception as e:
            st.error(f"Error fetching subscription: {e}")
            return None
    
    # Analytics (Admin/Service role only)
    async def get_platform_stats(self) -> Dict:
        """Get platform-wide statistics"""
        try:
            # This would require service role key for admin access
            service_client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_SERVICE_KEY")
            )
            
            # Total users
            users_result = service_client.table('user_profiles').select('id', count='exact').execute()
            
            # Total generations today
            today = datetime.now().strftime('%Y-%m-%d')
            generations_result = service_client.table('generations').select('id', count='exact').gte('created_at', today).execute()
            
            # Revenue this month
            current_month = datetime.now().strftime('%Y-%m')
            revenue_result = service_client.table('credit_transactions').select('amount').eq('type', 'purchase').gte('created_at', f'{current_month}-01').execute()
            revenue = sum(t['amount'] * 0.05 for t in revenue_result.data)  # Assuming $0.05 per credit
            
            return {
                'total_users': users_result.count or 0,
                'generations_today': generations_result.count or 0,
                'revenue_this_month': revenue
            }
        except Exception as e:
            return {'total_users': 0, 'generations_today': 0, 'revenue_this_month': 0}
    
    # File Storage (Supabase Storage)
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes) -> Optional[str]:
        """Upload file to Supabase Storage"""
        try:
            result = self.client.storage.from_(bucket).upload(file_path, file_data)
            
            if result.error:
                st.error(f"Upload error: {result.error}")
                return None
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            st.error(f"File upload error: {e}")
            return None
    
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from Supabase Storage"""
        try:
            result = self.client.storage.from_(bucket).remove([file_path])
            return not result.error
        except Exception:
            return False
    
    # Real-time subscriptions
    def subscribe_to_generations(self, user_id: str, callback):
        """Subscribe to real-time generation updates"""
        try:
            return self.client.table('generations').on('INSERT', callback).filter('user_id', 'eq', user_id).subscribe()
        except Exception as e:
            st.error(f"Subscription error: {e}")
            return None

# Global instance
supabase_client = SupabaseClient()