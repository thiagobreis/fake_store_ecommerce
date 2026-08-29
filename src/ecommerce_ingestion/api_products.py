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
resource = 'products'

# API lookup
logging.info('Searching data...')
df = search_api(api_url,resource)

# Parquet data schema definition
schema = pa.schema([
    ('id',pa.int64()),
    ('title',pa.string()),
    ('price',pa.float64()),
    ('description',pa.string()),
    ('category',pa.string()),
    ('image',pa.string()),
    ('rating',pa.struct([
        ('rate',pa.float64()),
        ('count',pa.int64())
        ]))
])

# Load data into Raw Layer
load_raw_data(df,schema,raw_folder,resource)
