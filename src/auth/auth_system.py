import streamlit as st
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str
    tier: str
    credits: int
    created_at: datetime
    last_login: datetime
    is_active: bool = True

class AuthSystem:
    """Production authentication system"""
    
    def __init__(self):
        self.jwt_secret = st.secrets.get("JWT_SECRET", "your-secret-key")
        self.api_base = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    
    def create_auth_interface(self):
        """Create authentication interface"""
        
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if not st.session_state.authenticated:
            self.show_login_page()
            return False
        
        return True
    
    def show_login_page(self):
        """Show login/signup page"""
        
        st.title("🎬 Cinema Action Scene Generator")
        st.write("Create professional action sequences with AI")
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            self.show_login_form()
        
        with tab2:
            self.show_signup_form()
        
        # Demo section
        with st.expander("🎮 Try Demo", expanded=True):
            st.write("**See what you can create:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.image("https://via.placeholder.com/300x200/333/FFF?text=Fight+Scene", caption="Epic Fight Scenes")
            
            with col2:
                st.image("https://via.placeholder.com/300x200/333/FFF?text=Car+Chase", caption="High-Speed Chases")
            
            with col3:
                st.image("https://via.placeholder.com/300x200/333/FFF?text=Explosion", caption="Cinematic Explosions")
            
            if st.button("🎬 Start Free Trial", type="primary"):
                self.start_demo_mode()
    
    def show_login_form(self):
        """Show login form"""
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me")
            
            submitted = st.form_submit_button("🔑 Login", type="primary")
            
            if submitted:
                if self.authenticate_user(email, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        # Forgot password
        if st.button("Forgot Password?"):
            self.show_password_reset(email if 'email' in locals() else "")
    
    def show_signup_form(self):
        """Show signup form"""
        
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
            
            with col2:
                last_name = st.text_input("Last Name")
                confirm_email = st.text_input("Confirm Email")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            # Plan selection
            plan = st.selectbox(
                "Choose Plan",
                ["Starter (Free)", "Pro ($15/month)", "Studio ($40/month)"]
            )
            
            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            marketing = st.checkbox("Send me updates about new features")
            
            submitted = st.form_submit_button("🚀 Create Account", type="primary")
            
            if submitted:
                if self.validate_signup(first_name, last_name, email, confirm_email, password, confirm_password, terms):
                    if self.create_account(first_name, last_name, email, password, plan):
                        st.success("✅ Account created! Please check your email to verify.")
                        st.balloons()
                    else:
                        st.error("❌ Account creation failed")
    
    def authenticate_user(self, email: str, password: str) -> bool:
        """Authenticate user with backend"""
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Store user session
                st.session_state.authenticated = True
                st.session_state.user = User(
                    id=user_data["id"],
                    email=user_data["email"],
                    name=user_data["name"],
                    tier=user_data["tier"],
                    credits=user_data["credits"],
                    created_at=datetime.fromisoformat(user_data["created_at"]),
                    last_login=datetime.now()
                )
                
                # Store JWT token
                st.session_state.jwt_token = user_data["token"]
                
                return True
                
        except Exception as e:
            st.error(f"Login error: {e}")
        
        return False
    
    def validate_signup(self, first_name: str, last_name: str, email: str, 
                       confirm_email: str, password: str, confirm_password: str, 
                       terms: bool) -> bool:
        """Validate signup form"""
        
        errors = []
        
        if not first_name or not last_name:
            errors.append("Name fields are required")
        
        if not email or "@" not in email:
            errors.append("Valid email is required")
        
        if email != confirm_email:
            errors.append("Email addresses don't match")
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if password != confirm_password:
            errors.append("Passwords don't match")
        
        if not terms:
            errors.append("You must agree to the Terms of Service")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
            return False
        
        return True
    
    def create_account(self, first_name: str, last_name: str, email: str, 
                      password: str, plan: str) -> bool:
        """Create new user account"""
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/signup",
                json={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": password,
                    "plan": plan.split(" ")[0].lower()  # Extract plan name
                }
            )
            
            return response.status_code == 201
            
        except Exception as e:
            st.error(f"Signup error: {e}")
            return False
    
    def start_demo_mode(self):
        """Start demo mode with limited features"""
        
        st.session_state.authenticated = True
        st.session_state.demo_mode = True
        st.session_state.user = User(
            id="demo",
            email="demo@example.com",
            name="Demo User",
            tier="demo",
            credits=10,  # Limited demo credits
            created_at=datetime.now(),
            last_login=datetime.now()
        )
        
        st.rerun()
    
    def show_password_reset(self, email: str):
        """Show password reset form"""
        
        st.subheader("🔄 Reset Password")
        
        reset_email = st.text_input("Enter your email", value=email)
        
        if st.button("Send Reset Link"):
            if self.send_password_reset(reset_email):
                st.success("✅ Password reset link sent to your email")
            else:
                st.error("❌ Email not found")
    
    def send_password_reset(self, email: str) -> bool:
        """Send password reset email"""
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/reset-password",
                json={"email": email}
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def logout(self):
        """Logout user"""
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.rerun()
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        
        if st.session_state.get('authenticated') and 'user' in st.session_state:
            return st.session_state.user
        
        return None
    
    def require_auth(self, func):
        """Decorator to require authentication"""
        
        def wrapper(*args, **kwargs):
            if not self.create_auth_interface():
                return
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def require_tier(self, required_tier: str):
        """Decorator to require specific tier"""
        
        tier_levels = {"demo": 0, "starter": 1, "pro": 2, "studio": 3, "enterprise": 4}
        
        def decorator(func):
            def wrapper(*args, **kwargs):
                user = self.get_current_user()
                
                if not user:
                    st.error("❌ Authentication required")
                    return
                
                user_level = tier_levels.get(user.tier, 0)
                required_level = tier_levels.get(required_tier, 4)
                
                if user_level < required_level:
                    st.error(f"❌ {required_tier.title()} plan required for this feature")
                    self.show_upgrade_prompt(required_tier)
                    return
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def show_upgrade_prompt(self, required_tier: str):
        """Show upgrade prompt for insufficient tier"""
        
        st.warning(f"🔒 This feature requires {required_tier.title()} plan")
        
        if st.button(f"🚀 Upgrade to {required_tier.title()}"):
            self.show_upgrade_page(required_tier)
    
    def show_upgrade_page(self, target_tier: str):
        """Show upgrade/billing page"""
        
        st.subheader(f"🚀 Upgrade to {target_tier.title()}")
        
        # Would integrate with Stripe for payments
        st.info("Upgrade functionality would integrate with Stripe here")
    
    def create_user_sidebar(self):
        """Create user info sidebar"""
        
        user = self.get_current_user()
        
        if user:
            with st.sidebar:
                st.markdown("---")
                st.subheader(f"👤 {user.name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Plan", user.tier.title())
                with col2:
                    st.metric("Credits", user.credits)
                
                if st.button("⚙️ Account Settings"):
                    self.show_account_settings()
                
                if st.button("🚪 Logout"):
                    self.logout()
    
    def show_account_settings(self):
        """Show account settings page"""
        
        st.subheader("⚙️ Account Settings")
        
        user = self.get_current_user()
        
        # Profile settings
        with st.expander("👤 Profile", expanded=True):
            new_name = st.text_input("Name", value=user.name)
            new_email = st.text_input("Email", value=user.email)
            
            if st.button("💾 Save Profile"):
                self.update_profile(new_name, new_email)
        
        # Billing settings
        with st.expander("💳 Billing"):
            st.write(f"Current Plan: **{user.tier.title()}**")
            st.write(f"Credits Remaining: **{user.credits}**")
            
            if st.button("🛒 Buy More Credits"):
                self.show_credit_purchase()
            
            if st.button("📋 View Usage History"):
                self.show_usage_history()
        
        # Security settings
        with st.expander("🔒 Security"):
            if st.button("🔄 Change Password"):
                self.show_change_password()
            
            if st.button("📱 Two-Factor Authentication"):
                st.info("2FA setup coming soon")
    
    def update_profile(self, name: str, email: str):
        """Update user profile"""
        
        try:
            user = self.get_current_user()
            
            response = requests.put(
                f"{self.api_base}/auth/profile",
                json={"name": name, "email": email},
                headers={"Authorization": f"Bearer {st.session_state.jwt_token}"}
            )
            
            if response.status_code == 200:
                # Update session
                user.name = name
                user.email = email
                st.success("✅ Profile updated!")
            else:
                st.error("❌ Update failed")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    def show_credit_purchase(self):
        """Show credit purchase interface"""
        
        st.subheader("🛒 Purchase Credits")
        
        # Credit packages
        packages = [
            {"credits": 100, "price": 5.00, "popular": False},
            {"credits": 500, "price": 20.00, "popular": True},
            {"credits": 1000, "price": 35.00, "popular": False},
            {"credits": 2500, "price": 75.00, "popular": False}
        ]
        
        for package in packages:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                popular_text = " 🔥 Popular" if package["popular"] else ""
                st.write(f"**{package['credits']} Credits{popular_text}**")
            
            with col2:
                st.write(f"${package['price']:.2f}")
            
            with col3:
                if st.button(f"Buy", key=f"buy_{package['credits']}"):
                    self.process_payment(package)
    
    def process_payment(self, package: Dict[str, Any]):
        """Process credit purchase (would integrate with Stripe)"""
        
        st.info("💳 Payment processing would integrate with Stripe here")
        
        # Simulate successful payment
        user = self.get_current_user()
        user.credits += package["credits"]
        
        st.success(f"✅ Successfully purchased {package['credits']} credits!")
        st.balloons()
    
    def show_usage_history(self):
        """Show user's generation history"""
        
        st.subheader("📊 Usage History")
        
        # Mock usage data
        import pandas as pd
        
        usage_data = [
            {"Date": "2024-01-15", "Type": "Image Generation", "Credits": 2, "Success": True},
            {"Date": "2024-01-15", "Type": "LoRA Training", "Credits": 75, "Success": True},
            {"Date": "2024-01-14", "Type": "Video Generation", "Credits": 8, "Success": True},
            {"Date": "2024-01-14", "Type": "Batch Generation", "Credits": 6, "Success": True}
        ]
        
        df = pd.DataFrame(usage_data)
        st.dataframe(df, use_container_width=True)
        
        # Usage analytics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Generations", len(df))
        with col2:
            st.metric("Credits Used", df["Credits"].sum())
        with col3:
            st.metric("Success Rate", f"{df['Success'].mean()*100:.1f}%")
    
    def show_change_password(self):
        """Show change password form"""
        
        st.subheader("🔄 Change Password")
        
        with st.form("change_password"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submitted = st.form_submit_button("🔄 Change Password")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("❌ New passwords don't match")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    if self.change_password(current_password, new_password):
                        st.success("✅ Password changed successfully!")
                    else:
                        st.error("❌ Current password is incorrect")
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change user password"""
        
        try:
            response = requests.put(
                f"{self.api_base}/auth/change-password",
                json={
                    "current_password": current_password,
                    "new_password": new_password
                },
                headers={"Authorization": f"Bearer {st.session_state.jwt_token}"}
            )
            
            return response.status_code == 200
            
        except Exception:
            return False