import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..workflows.workflow_templates import WorkflowType, ACTION_SCENE_TEMPLATES

@dataclass
class PricingTier:
    name: str
    price_per_credit: float
    credits_included: int
    monthly_price: float
    features: List[str]
    max_resolution: str
    video_enabled: bool
    batch_size: int

@dataclass
class UsageRecord:
    timestamp: datetime
    workflow_type: str
    credits_used: int
    resolution: str
    generation_time: float
    success: bool

class PricingManager:
    """Manage pricing, credits, and usage tracking"""
    
    def __init__(self):
        self.pricing_tiers = {
            "starter": PricingTier(
                name="Starter",
                price_per_credit=0.05,
                credits_included=100,
                monthly_price=5.00,
                features=[
                    "Basic image generation",
                    "Sketch-to-image",
                    "Standard resolution (768x768)",
                    "Community support"
                ],
                max_resolution="768x768",
                video_enabled=False,
                batch_size=1
            ),
            
            "pro": PricingTier(
                name="Pro",
                price_per_credit=0.03,
                credits_included=500,
                monthly_price=15.00,
                features=[
                    "High-res generation (1024x1024)",
                    "Image-to-video sequences",
                    "ControlNet support",
                    "Batch processing (4x)",
                    "Priority queue",
                    "Email support"
                ],
                max_resolution="1024x1024", 
                video_enabled=True,
                batch_size=4
            ),
            
            "studio": PricingTier(
                name="Studio",
                price_per_credit=0.02,
                credits_included=2000,
                monthly_price=40.00,
                features=[
                    "Ultra-res generation (1536x1536+)",
                    "Full video suite (t2v, i2v, v2v)",
                    "Multi-ControlNet",
                    "Batch processing (8x)",
                    "Custom workflows",
                    "Priority support",
                    "Commercial license"
                ],
                max_resolution="2048x1536",
                video_enabled=True,
                batch_size=8
            ),
            
            "enterprise": PricingTier(
                name="Enterprise", 
                price_per_credit=0.01,
                credits_included=10000,
                monthly_price=150.00,
                features=[
                    "Unlimited resolution",
                    "Dedicated RTX 6000 instances",
                    "Custom model training",
                    "API access",
                    "White-label options",
                    "24/7 support",
                    "SLA guarantee"
                ],
                max_resolution="unlimited",
                video_enabled=True,
                batch_size=16
            )
        }
        
        # Credit costs by workflow type
        self.credit_costs = {
            WorkflowType.IMAGE_GENERATION: {
                "768x768": 1,
                "1024x1024": 2,
                "1536x1536": 4,
                "2048x1536": 6
            },
            WorkflowType.SKETCH_TO_IMAGE: {
                "768x768": 1,
                "1024x1024": 2,
                "1536x1536": 4
            },
            WorkflowType.TEXT_TO_VIDEO: {
                "768x768": 8,
                "1024x576": 10,
                "1024x1024": 12
            },
            WorkflowType.IMAGE_TO_VIDEO: {
                "768x768": 6,
                "1024x576": 8,
                "1024x1024": 10
            },
            WorkflowType.VIDEO_TO_VIDEO: {
                "768x768": 10,
                "1024x576": 12,
                "1024x1024": 15
            },
            WorkflowType.BATCH_GENERATION: {
                "multiply_by_batch_size": True
            }
        }
    
    def calculate_credits_needed(
        self, 
        workflow_type: WorkflowType,
        resolution: str,
        batch_size: int = 1
    ) -> int:
        """Calculate credits needed for a generation"""
        
        base_cost = self.credit_costs.get(workflow_type, {}).get(resolution, 1)
        
        if workflow_type == WorkflowType.BATCH_GENERATION:
            base_cost = self.credit_costs[WorkflowType.IMAGE_GENERATION].get(resolution, 1)
            return base_cost * batch_size
        
        return base_cost
    
    def get_user_tier(self, user_id: str) -> str:
        """Get user's current pricing tier"""
        # Would fetch from database
        return st.session_state.get('user_tier', 'starter')
    
    def get_user_credits(self, user_id: str) -> int:
        """Get user's remaining credits"""
        # Would fetch from database
        return st.session_state.get('user_credits', 0)
    
    def can_afford_generation(
        self,
        user_id: str, 
        workflow_type: WorkflowType,
        resolution: str,
        batch_size: int = 1
    ) -> bool:
        """Check if user can afford generation"""
        
        credits_needed = self.calculate_credits_needed(workflow_type, resolution, batch_size)
        user_credits = self.get_user_credits(user_id)
        
        return user_credits >= credits_needed
    
    def deduct_credits(
        self,
        user_id: str,
        workflow_type: WorkflowType, 
        resolution: str,
        batch_size: int = 1,
        success: bool = True
    ) -> bool:
        """Deduct credits for generation (only if successful)"""
        
        if not success:
            return True  # No charge for failed generations
        
        credits_needed = self.calculate_credits_needed(workflow_type, resolution, batch_size)
        user_credits = self.get_user_credits(user_id)
        
        if user_credits >= credits_needed:
            new_credits = user_credits - credits_needed
            st.session_state['user_credits'] = new_credits
            
            # Log usage
            self._log_usage(user_id, workflow_type, credits_needed, resolution, success)
            
            return True
        
        return False
    
    def _log_usage(
        self,
        user_id: str,
        workflow_type: WorkflowType,
        credits_used: int,
        resolution: str,
        success: bool
    ):
        """Log usage for analytics"""
        
        if 'usage_history' not in st.session_state:
            st.session_state['usage_history'] = []
        
        usage = UsageRecord(
            timestamp=datetime.now(),
            workflow_type=workflow_type.value,
            credits_used=credits_used,
            resolution=resolution,
            generation_time=0.0,  # Would be filled by actual generation
            success=success
        )
        
        st.session_state['usage_history'].append(usage)

def create_pricing_interface():
    """Create pricing and billing interface"""
    
    st.title("💳 Pricing & Billing")
    
    pricing_manager = PricingManager()
    
    # Current plan status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_tier = pricing_manager.get_user_tier("user123")  # Would be actual user ID
        st.metric("Current Plan", current_tier.title())
    
    with col2:
        current_credits = pricing_manager.get_user_credits("user123")
        st.metric("Credits Remaining", current_credits)
    
    with col3:
        # Calculate usage this month
        usage_history = st.session_state.get('usage_history', [])
        month_usage = sum(u.credits_used for u in usage_history if u.timestamp.month == datetime.now().month)
        st.metric("Used This Month", month_usage)
    
    # Pricing tiers
    st.subheader("🎯 Pricing Plans")
    
    cols = st.columns(len(pricing_manager.pricing_tiers))
    
    for i, (tier_id, tier) in enumerate(pricing_manager.pricing_tiers.items()):
        with cols[i]:
            # Highlight current tier
            if tier_id == current_tier:
                st.markdown(f"### 🌟 {tier.name} (Current)")
            else:
                st.markdown(f"### {tier.name}")
            
            st.markdown(f"**${tier.monthly_price}/month**")
            st.markdown(f"*{tier.credits_included} credits included*")
            st.markdown(f"*${tier.price_per_credit:.3f} per additional credit*")
            
            st.markdown("**Features:**")
            for feature in tier.features:
                st.markdown(f"• {feature}")
            
            st.markdown(f"**Max Resolution:** {tier.max_resolution}")
            st.markdown(f"**Video Generation:** {'✅' if tier.video_enabled else '❌'}")
            st.markdown(f"**Batch Size:** {tier.batch_size}x")
            
            if tier_id != current_tier:
                if st.button(f"Upgrade to {tier.name}", key=f"upgrade_{tier_id}"):
                    upgrade_plan(tier_id, tier)
    
    # Credit costs calculator
    st.subheader("💰 Credit Cost Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        calc_workflow = st.selectbox(
            "Workflow Type",
            [
                "Image Generation",
                "Sketch to Image", 
                "Text to Video",
                "Image to Video",
                "Video to Video"
            ]
        )
    
    with col2:
        calc_resolution = st.selectbox(
            "Resolution",
            ["768x768", "1024x1024", "1536x1536", "2048x1536"]
        )
    
    with col3:
        calc_batch = st.number_input("Batch Size", 1, 8, 1)
    
    # Map UI names to enum
    workflow_mapping = {
        "Image Generation": WorkflowType.IMAGE_GENERATION,
        "Sketch to Image": WorkflowType.SKETCH_TO_IMAGE,
        "Text to Video": WorkflowType.TEXT_TO_VIDEO,
        "Image to Video": WorkflowType.IMAGE_TO_VIDEO,
        "Video to Video": WorkflowType.VIDEO_TO_VIDEO
    }
    
    calc_type = workflow_mapping[calc_workflow]
    credits_needed = pricing_manager.calculate_credits_needed(calc_type, calc_resolution, calc_batch)
    
    st.info(f"💡 This generation will cost **{credits_needed} credits**")
    
    if current_credits >= credits_needed:
        st.success("✅ You have enough credits for this generation")
    else:
        credits_short = credits_needed - current_credits
        st.error(f"❌ You need {credits_short} more credits")
        
        if st.button("🛒 Buy More Credits"):
            show_credit_purchase_dialog(credits_short)
    
    # Usage analytics
    st.subheader("📊 Usage Analytics")
    
    if usage_history:
        # Usage over time
        import pandas as pd
        
        df = pd.DataFrame([
            {
                "Date": u.timestamp.date(),
                "Workflow": u.workflow_type,
                "Credits": u.credits_used,
                "Resolution": u.resolution,
                "Success": u.success
            }
            for u in usage_history
        ])
        
        # Daily usage chart
        daily_usage = df.groupby("Date")["Credits"].sum()
        st.line_chart(daily_usage)
        
        # Usage by workflow type
        workflow_usage = df.groupby("Workflow")["Credits"].sum()
        st.bar_chart(workflow_usage)
        
        # Recent generations
        st.subheader("🕒 Recent Generations")
        recent = sorted(usage_history, key=lambda x: x.timestamp, reverse=True)[:10]
        
        for usage in recent:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(usage.timestamp.strftime("%m/%d %H:%M"))
            with col2:
                st.write(usage.workflow_type.replace("_", " ").title())
            with col3:
                st.write(f"{usage.credits_used} credits")
            with col4:
                st.write("✅" if usage.success else "❌")
    
    else:
        st.info("No usage history yet. Start generating to see analytics!")

def upgrade_plan(tier_id: str, tier: PricingTier):
    """Handle plan upgrade"""
    
    st.success(f"✅ Upgraded to {tier.name} plan!")
    st.session_state['user_tier'] = tier_id
    st.session_state['user_credits'] = st.session_state.get('user_credits', 0) + tier.credits_included
    st.rerun()

def show_credit_purchase_dialog(credits_needed: int):
    """Show credit purchase options"""
    
    st.subheader("🛒 Purchase Credits")
    
    credit_packages = [
        {"credits": 100, "price": 4.00, "bonus": 0},
        {"credits": 500, "price": 18.00, "bonus": 50}, 
        {"credits": 1000, "price": 32.00, "bonus": 150},
        {"credits": 2500, "price": 70.00, "bonus": 500}
    ]
    
    for package in credit_packages:
        total_credits = package["credits"] + package["bonus"]
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            bonus_text = f" + {package['bonus']} bonus" if package["bonus"] > 0 else ""
            st.write(f"**{package['credits']} credits{bonus_text}** = {total_credits} total")
        
        with col2:
            st.write(f"${package['price']:.2f}")
        
        with col3:
            if st.button(f"Buy", key=f"buy_{package['credits']}"):
                purchase_credits(total_credits, package['price'])

def purchase_credits(credits: int, price: float):
    """Handle credit purchase"""
    
    # Simulate payment processing
    with st.spinner("Processing payment..."):
        time.sleep(2)
    
    # Add credits to account
    current_credits = st.session_state.get('user_credits', 0)
    st.session_state['user_credits'] = current_credits + credits
    
    st.success(f"✅ Successfully purchased {credits} credits for ${price:.2f}!")
    st.balloons()
    st.rerun()

def check_generation_permissions(
    workflow_type: WorkflowType,
    resolution: str,
    batch_size: int = 1
) -> Dict[str, any]:
    """Check if user can perform generation"""
    
    pricing_manager = PricingManager()
    user_id = "user123"  # Would be actual user ID
    user_tier = pricing_manager.get_user_tier(user_id)
    tier_info = pricing_manager.pricing_tiers[user_tier]
    
    # Check tier limits
    max_res_check = resolution_check(resolution, tier_info.max_resolution)
    video_check = not (workflow_type in [WorkflowType.TEXT_TO_VIDEO, WorkflowType.IMAGE_TO_VIDEO, WorkflowType.VIDEO_TO_VIDEO] and not tier_info.video_enabled)
    batch_check = batch_size <= tier_info.batch_size
    credits_check = pricing_manager.can_afford_generation(user_id, workflow_type, resolution, batch_size)
    
    return {
        "allowed": all([max_res_check, video_check, batch_check, credits_check]),
        "resolution_ok": max_res_check,
        "video_ok": video_check,
        "batch_ok": batch_check, 
        "credits_ok": credits_check,
        "credits_needed": pricing_manager.calculate_credits_needed(workflow_type, resolution, batch_size),
        "tier": user_tier
    }

def resolution_check(requested: str, max_allowed: str) -> bool:
    """Check if resolution is within tier limits"""
    
    if max_allowed == "unlimited":
        return True
    
    res_map = {
        "768x768": 1,
        "1024x1024": 2,
        "1536x1536": 3,
        "2048x1536": 4
    }
    
    return res_map.get(requested, 0) <= res_map.get(max_allowed, 0)