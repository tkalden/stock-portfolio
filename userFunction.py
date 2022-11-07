import logging
import bigQuery
import uuid

logging.basicConfig(level = logging.INFO)

class UserCRUD():
    def get_user_by_email(email):
        return bigQuery.get_user_by_id(email)

    def save_user_data(email,name,password):
        uid = uuid.uuid4()
        rows_to_insert = [
        {u"email": email, u"name": name, u"password": password, u"id": uid.hex}]
        bigQuery.insert_rows('stockdataextractor.stock.user-table',rows_to_insert)

    