import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os
import pyarrow as pa
from src.utils.functions import search_api, load_raw_data
import logging

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
resource = 'carts'

# API lookup
logging.info('Searching data...')
df = search_api(api_url,resource)

# DataFrame definition
df['date'] = pd.to_datetime(df['date'])
df['id'] = df['id'].astype('int64')
df['userId'] = df['userId'].astype('int64')
df = df.drop(columns=['__v'])

# Parquet data schema definition
logging.info('Defining data schema...')
schema = pa.schema([
    ('id',pa.int64()),
    ('userId',pa.int64()),
    ('date',pa.timestamp('ms')),
    ('products',pa.list_(pa.struct([
        ('productId',pa.int64()),
        ('quantity',pa.int64())        
    ])))
])

# Load data into Raw Layer
load_raw_data(df,schema,raw_folder,resource)