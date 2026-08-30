from dotenv import load_dotenv, find_dotenv
import os
from src.utils.functions import search_api, load_raw_data, transform_carts, transform_users
from src.utils.schemas import CARTS, PRODUCTS, USERS
import logging
import argparse

# Set environment
load_dotenv(find_dotenv())
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set variables
api_url = os.getenv("API_URL")
raw_folder = os.getenv("RAW_FOLDER")

logging.info('Listing resources...')
RESOURCES = {
    'products': {
        'schema': PRODUCTS,
        'transform': None,
    },
    'carts': {
        'schema': CARTS,
        'transform': transform_carts,
    },
    'users': {
        'schema': USERS,
        'transform': transform_users,
    },
}

# Set parser for CLI execution
parser = argparse.ArgumentParser(description='Ingest data from Fake Store API')
parser.add_argument(
    '--resource',
    choices= list(RESOURCES.keys()) + ['all'],
    required=True,
    help='Which resource to ingest, or "all" for every listed resource'
)

args = parser.parse_args()

# Execute API ingestion
def run_ingestion(resource:str, api_url:str, raw_folder:str) -> None:
    config = RESOURCES[resource]
    df = search_api(api_url,resource)
    if config['transform'] is not None:
        df = config['transform'](df)
    load_raw_data(df,config['schema'],raw_folder,resource) 


if args.resource == 'all':
    for resource in RESOURCES:
        run_ingestion(resource, api_url, raw_folder)
else:
    run_ingestion(args.resource, api_url, raw_folder)
    
    
