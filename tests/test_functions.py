import pytest
import pandas as pd
import pyarrow as pa
from datetime import datetime
from src.utils.functions import transform_carts, transform_users, load_raw_data
from src.utils.schemas import CARTS, USERS
import logging
import src.ecommerce_ingestion.ingestion as ingestion

def test_transform_carts():
    data = [
        {
            'id': 101,
            'userId': 1,
            'date': pd.Timestamp('2026-09-01 10:00:00'),
            'products': [
                {'productId': 500, 'quantity': 2},
                {'productId': 501, 'quantity': 1}
            ],
            '__v':0
        },
        {
            'id': 102,
            'userId': 2,
            'date': pd.Timestamp('2026-09-01 11:30:00'),
            'products': [
                {'productId': 502, 'quantity': 5}
            ],
            '__v':0
        }
    ]

    # 2. Criação do DataFrame Pandas
    df = pd.DataFrame(data)
    df = transform_carts(df)
    
    table = pa.Table.from_pandas(df,schema=CARTS, preserve_index=False)
    assert table.num_rows == len(df)
    
def test_transform_users():
    data = {
        'id': [1, 2],
        'email': ['john.doe@example.com', 'jane.smith@example.com'],
        'username': ['johndoe', 'janesmith'],
        'password': ['hash_pass_123', 'hash_pass_456'],
        'name': [
            {'firstname': 'John', 'lastname': 'Doe'},
            {'firstname': 'Jane', 'lastname': 'Smith'}
        ],
        'phone': ['+55 11 99999-0001', '+55 21 98888-0002'],
        'address': [
            {
                'geolocation': {'lat': -23.5505, 'long': -46.6333},
                'city': 'São Paulo',
                'street': 'Av. Paulista',
                'number': '1000',
                'zipcode': '01310-100'
            },
            {
                'geolocation': {'lat': -22.9068, 'long': -43.1729},
                'city': 'Rio de Janeiro',
                'street': 'Rua Copacabana',
                'number': '500',
                'zipcode': '22020-001'
            }
        ],
        '__v':[0,0]
    }
    
    df = pd.DataFrame(data)
    df = transform_users(df)
    
    table = pa.Table.from_pandas(df,schema=USERS, preserve_index=False)
    assert table.num_rows == len(df)
    
    
def test_load_raw_data_with_content(tmp_path):
    df = pd.DataFrame({'id':[1,2],'name': ['a','b']})
    schema = pa.schema([
        ('id', pa.int64()),
        ('name', pa.string())
    ])
    
    load_raw_data(df,schema,str(tmp_path),'test_resource')
    
    file = tmp_path / 'test_resource.parquet'
    assert file.exists()
    
    result = pd.read_parquet(file)
    assert result.equals(df)
    
    
def test_load_raw_data_mismatch(tmp_path):
    df = pd.DataFrame({'id':['not a number']})
    schema = pa.schema([('id', pa.int64())])
    
    with pytest.raises(Exception):
        load_raw_data(df, schema, str(tmp_path),'test_resource')
    
    
import pytest
import requests
import pandas as pd
from src.utils.functions import search_api


def test_search_api_returns_dataframe(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass  # simula uma resposta 200, sem erro

        def json(self):
            return [
                {'id': 1, 'title': 'Product A'},
                {'id': 2, 'title': 'Product B'}
            ]

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(requests, 'get', fake_get)

    df = search_api('https://fakestoreapi.com', 'products')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ['id', 'title']


def test_search_api_raises_on_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise requests.HTTPError('404 Not Found')

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(requests, 'get', fake_get)

    with pytest.raises(requests.HTTPError):
        search_api('https://fakestoreapi.com', 'products')
    
    
def test_run_ingestion_calls_transform_when_transform_exists(monkeypatch):
    calls = {}
    fake_df = pd.DataFrame({'a': [1]})
    transformed_df = pd.DataFrame({'a': [2]})

    def fake_search_api(api_url, resource):
        calls['search_api_args'] = (api_url, resource)
        return fake_df

    def fake_transform(df):
        calls['transform_received'] = df
        return transformed_df

    def fake_load_raw_data(df, schema, raw_folder, resource):
        calls['load_raw_data_args'] = (df, schema, raw_folder, resource)

    monkeypatch.setattr(ingestion, 'search_api', fake_search_api)
    monkeypatch.setattr(ingestion, 'load_raw_data', fake_load_raw_data)
    monkeypatch.setattr(ingestion, 'RESOURCES', {
        'carts': {'schema': 'FAKE_SCHEMA', 'transform': fake_transform}
    })

    ingestion.run_ingestion('carts', 'http://fake-api.com', '/tmp/raw')

    assert calls['search_api_args'] == ('http://fake-api.com', 'carts')
    assert calls['transform_received'].equals(fake_df)
    loaded_df, schema, raw_folder, resource = calls['load_raw_data_args']
    assert loaded_df.equals(transformed_df)
    assert schema == 'FAKE_SCHEMA'
    assert resource == 'carts'


def test_run_ingestion_skips_transform_when_none(monkeypatch):
    calls = {}
    fake_df = pd.DataFrame({'a': [1]})

    def fake_search_api(api_url, resource):
        return fake_df

    def fake_load_raw_data(df, schema, raw_folder, resource):
        calls['loaded_df'] = df

    monkeypatch.setattr(ingestion, 'search_api', fake_search_api)
    monkeypatch.setattr(ingestion, 'load_raw_data', fake_load_raw_data)
    monkeypatch.setattr(ingestion, 'RESOURCES', {
        'products': {'schema': 'FAKE_SCHEMA', 'transform': None}
    })

    ingestion.run_ingestion('products', 'http://fake-api.com', '/tmp/raw')

    assert calls['loaded_df'].equals(fake_df)    