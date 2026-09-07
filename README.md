# Fake Store Ecommerce

A small data engineering portfolio project that ingests data from the [Fake Store API](https://fakestoreapi.com) and lands it as Parquet files in a local raw layer. The focus of this project is practicing Python fundamentals for data engineering rather than the business domain itself:

- Consuming a public REST API
- Reading/writing structured and semi-structured (nested) data
- Config-driven pipeline design (Strategy pattern via a resource dictionary)
- Type hints, validated with mypy
- Automated testing with pytest (including mocked HTTP calls)

## Data source

- API: https://fakestoreapi.com
- Resources ingested: `products`, `carts`, `users`

All data is fake/sample data provided by the API.

## Project structure

```
fake_store_ecommerce/
├── src/
│   ├── ecommerce_ingestion/
│   │   └── ingestion.py       # CLI entry point, resource config, orchestration
│   └── utils/
│       ├── functions.py       # search_api, load_raw_data, transform_carts, transform_users
│       └── schemas.py         # Parquet schemas (PRODUCTS, CARTS, USERS)
├── tests/
│   └── test_functions.py      # pytest suite (unit tests + mocked API calls)
├── data/
│   └── raw/                   # Parquet output, one file per resource
├── .env.example
├── .gitignore
├── mypy.ini
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust if needed:
   ```
   API_URL=http://fakestoreapi.com
   RAW_FOLDER=data/raw
   PROCESSED_FOLDER=data/processed
   ```

## Usage

Run the ingestion for a single resource:

```
python -m src.ecommerce_ingestion.ingestion --resource products
python -m src.ecommerce_ingestion.ingestion --resource carts
python -m src.ecommerce_ingestion.ingestion --resource users
```

Run the ingestion for every resource at once:

```
python -m src.ecommerce_ingestion.ingestion --resource all
```

Each run fetches the resource from the API, applies any resource-specific transformation, and writes it to `data/raw/<resource>.parquet` using the schema defined in `src/utils/schemas.py`.

## Development

**Type checking** (static analysis, does not execute the code):

```
mypy src
```

**Automated tests** (executes the code with sample/mocked data):

```
pytest
```

Both should be run from the project root, so that the `src` package can be resolved correctly.

## Notes

- `data/raw/` holds unmodified, landed data — nothing downstream should ever overwrite it in place.
- Adding a new resource only requires: a new schema in `schemas.py`, an optional transform function in `functions.py`, and one new entry in the `RESOURCES` dictionary in `ingestion.py` — no changes to the orchestration logic itself.
