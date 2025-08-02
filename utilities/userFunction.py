import logging
import uuid
from flask import flash
import utilities.constant as constant
import utilities.redis as redis
from utilities.redis_data import redis_manager
import pandas as pd

logging.basicConfig(level = logging.INFO)
constant = constant.load_constant()
table_names = constant["table_names"]

class UserCRUD():
    def get_user_by_email(self, email):
        """Get user by email using Redis"""
        user_data = redis_manager.get_user_by_email(email)
        if user_data:
            # Create a simple object with the expected attributes
            class UserData:
                def __init__(self, data):
                    self.email = data.get('email', '')
                    self.name = data.get('name', '')
                    self.password = data.get('password', '')
                    self.id = data.get('id', '')
            
            return UserData(user_data)
        return None

    def get_user_by_id(self, user_id):
        """Get user by user_id using Redis"""
        user_data = redis_manager.get_user_by_id(user_id)
        if user_data:
            # Create a simple object with the expected attributes
            class UserData:
                def __init__(self, data):
                    self.email = data.get('email', '')
                    self.name = data.get('name', '')
                    self.password = data.get('password', '')
                    self.id = data.get('id', '')
            
            return UserData(user_data)
        return None

    def save_user_data(self, email, name, password):
        """Save user data to Redis"""
        try:
            return redis_manager.save_user(email, name, password)
        except Exception as e:
            logging.error(f"Error saving user data: {e}")
            return False

    def subscribe(self, email):
        """Subscribe user to newsletter"""
        try:
            if not self.get_subscription_by_id(email).empty:
                flash('This email is already subscribed.', 'warning')
                return False
            
            success = redis_manager.save_subscription(email)
            if success:
                flash('Thanks for the subscription', 'success')
            else:
                flash('Failed to subscribe. Please try again.', 'error')
            return success
        except Exception as e:
            logging.error(f"Error in subscribe: {e}")
            flash('Subscription failed. Please try again.', 'error')
            return False
    
    def get_subscription_by_id(self, email):
        """Get subscription by email"""
        try:
            subscription = redis_manager.get_subscription_by_email(email)
            if subscription:
                return pd.DataFrame([subscription])
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error getting subscription: {e}")
            return pd.DataFrame()
    



    