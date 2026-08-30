import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging
from pathlib import Path
from typing import Callable

def search_api(endpoint:str,resource:str) -> pd.DataFrame:
    logging.info(f'Searching {resource} data...')
    response = requests.get(f'{endpoint}/{resource}', timeout=10)
    response.raise_for_status()
    df = pd.DataFrame.from_dict(response.json())
    
    return df


def load_raw_data(df: pd.DataFrame,schema: pa.Schema, raw_folder:str, resource:str) -> None:
    
    file = Path(f'{raw_folder}/{resource}.parquet')
    
    try:
        df_pq = pa.Table.from_pandas(df,schema=schema, preserve_index=False)        
        pq.write_table(df_pq,file)
        logging.info(f'Data loaded into: {file}')

    except Exception as e:
        logging.error(f'Error while loading data: {e}')
        

def  transform_users(df: pd.DataFrame):
    # DataFrame definition
    df = df.drop(columns='__v')
    df['address'] = df['address'].apply(lambda addr: {
        **addr,
        'number': str(addr['number']),
        'geolocation': {
            'lat': float(addr['geolocation']['lat']),
            'long': float(addr['geolocation']['lat'])
        }
    })
    
    return df


def transform_carts(df: pd.DataFrame):
    # DataFrame definition
    df['date'] = pd.to_datetime(df['date'])
    df['id'] = df['id'].astype('int64')
    df['userId'] = df['userId'].astype('int64')
    df = df.drop(columns=['__v'])
    
    return df   
    

