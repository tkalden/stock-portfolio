import logging
import utilities.bigQuery as bigQuery
import uuid
import utilities.constant as constant
from flask import flash

logging.basicConfig(level = logging.INFO)
constant = constant.load_constant()
table_names = constant["table_names"]

class UserCRUD():
    def get_user_by_email(self,email):
        return bigQuery.get_user_by_id(email)

    def save_user_data(self,email,name,password):
        uid = uuid.uuid4()
        rows_to_insert = [
        {u"email": email, u"name": name, u"password": password, u"id": uid.hex}]
        bigQuery.insert_rows(table_names["user"],rows_to_insert)
    
    def subscribe(self,email):
        rows_to_insert = [
        {u"email": email}]
        bigQuery.insert_rows(table_names["subscription"],rows_to_insert)
    
    def get_subscription_by_id(self,email):
        return bigQuery.get_subscription_by_id(email)
    
    def subscribe(self,subscribe_email):
        if  self.get_subscription_by_id(subscribe_email).empty:
            self.subscribe(subscribe_email)
            flash('Thanks for the subscription','success')
        else:
            flash('This email is already subscribed.','warning')

    



    