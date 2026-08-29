import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging
from pathlib import Path

def search_api(endpoint:str,resource:str):
    response = requests.get(f'{endpoint}/{resource}', timeout=10)
    response.raise_for_status()
    df = pd.DataFrame.from_dict(response.json())
    
    return df


def load_raw_data(df,schema,raw_folder:str,resource:str):
    
    file = Path(f'{raw_folder}/{resource}.parquet')
    
    try:
        df_pq = pa.Table.from_pandas(df,schema=schema, preserve_index=False)        
        pq.write_table(df_pq,file)
        logging.info(f'Data loaded into: {file}')

    except Exception as e:
        logging.error(f'Error while loading data: {e}')