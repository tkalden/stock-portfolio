from google.oauth2 import service_account
from google.cloud import bigquery
import logging
logging.basicConfig(level=logging.INFO)
credentials = service_account.Credentials.from_service_account_file(
    'stockdataextractor.json')

project_id = 'stockdataextractor'
client = bigquery.Client(credentials=credentials, project=project_id)


def get_stock_data(index, sector):
    logging.info( 'Getting Stock data for Sector %s  and Index  %s ', sector, index)
    query = """
        SELECT *
        FROM  `stockdataextractor.stock.screen-data` 
        WHERE
        Sector = @sector 
        AND Index = @index
        ORDER BY Ticker DESC
        LIMIT 1000 """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("sector", "STRING", sector),
            bigquery.ScalarQueryParameter("index", "STRING", index),
        ]
    )

    # Make an API request.
    query_job = client.query(query, job_config=job_config)
    return query_job.to_dataframe()  # Wait for the job to complete.
