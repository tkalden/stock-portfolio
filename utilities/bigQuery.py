from google.cloud import bigquery
import logging
logging.basicConfig(level=logging.INFO)


client = bigquery.Client()

def write_to_bigquery(df,table_id):
    logging.info('Saving data')
    client.load_table_from_dataframe(df, table_id)


def get_stock_data(index, sector):
    logging.info( 'Getting Stock data for Sector %s  and Index  %s ', sector, index)
    query_parameters = [bigquery.ScalarQueryParameter("index", "STRING", index),
    bigquery.ScalarQueryParameter("sector", "STRING", sector)] 
    return run_query(get_query(index,sector),query_parameters)

def run_query(query,query_parameters):
    job_config = bigquery.QueryJobConfig(
            query_parameters= query_parameters
        )
    query_job = client.query(query, job_config=job_config)
    return query_job.to_dataframe()

def get_average_metric_by_sector(sector):
    logging.info( 'Getting Average metric data for Sector %s', sector)      
    query = """
            SELECT *
            FROM  `stockdataextractor.stock.average-metric`
            WHERE
            Sector = @sector 
             """
    query_parameters = [bigquery.ScalarQueryParameter("sector", "STRING", sector)]
    return run_query(query,query_parameters)

def get_portfolios_by_user_id(user_id):
    query = """
    SELECT * FROM `stockdataextractor.stock.portfolio-table` t
    WHERE t.user_id = @user_id
     """
    query_parameters = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    return run_query(query,query_parameters)

def get_user_by_id_and_pw(user_id,password):
    query = """
    SELECT * FROM `stockdataextractor.stock.user-table` t
    WHERE t.user_id = @user_id
    AND t.password = @password
     """
    query_parameters = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id),bigquery.ScalarQueryParameter("password", "STRING", password)]
    return run_query(query,query_parameters)

def get_subscription_by_id(email):
    query = """
    SELECT * FROM `stockdataextractor.stock.subscription-table` t
    WHERE t.email = @email
     """
    query_parameters = [bigquery.ScalarQueryParameter("email", "STRING", email)]
    return run_query(query,query_parameters)

def get_user_by_id(email):
    query = """
    SELECT * FROM `stockdataextractor.stock.user-table` t
    WHERE t.email = @email
     """
    query_parameters = [bigquery.ScalarQueryParameter("email", "STRING", email)]
    return run_query(query,query_parameters)

def get_portfolio_by_id(portfolio_id):
    query = """
    SELECT * FROM `stockdataextractor.stock.portfolio-table` t
    WHERE t.portfolio_id = @portfolio_id
     """
    query_parameters = [bigquery.ScalarQueryParameter("portfolio_id", "STRING", portfolio_id)]
    return run_query(query,query_parameters)
 
def get_average_metric():
    query = """
            SELECT *
            FROM  `stockdataextractor.stock.average-metric` 
             """
    return run_query(query,query_parameters = [])

def get_annual_return():
    query = """
            SELECT *  FROM `stockdataextractor.stock.annual-return` 
             """
    return run_query(query,query_parameters = [])

def get_query(index,sector):
    query = ""
    if sector == 'Any' and index != 'Any':
        query = """
            SELECT *
            FROM  `stockdataextractor.stock.screen-data`
            WHERE
            Index = @index 
            ORDER BY Ticker DESC
            LIMIT 1000 """
    else:
       query = """
            SELECT *
            FROM  `stockdataextractor.stock.screen-data`
            WHERE
            Index = @index AND
            Sector = @sector
            ORDER BY Ticker DESC
            LIMIT 1000 """
    return query

def insert_rows(table_id,rows_to_insert):
    table = client.get_table(table_id)
    errors = client.insert_rows_json(table, rows_to_insert)  # Make an API request.
    if errors == []:
        logging.debug("New rows have been added.")
    else:
        logging.error("Encountered errors while inserting rows: {}".format(errors))