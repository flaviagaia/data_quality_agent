from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DATASET_PATH = RAW_DIR / "customer_master_sample.csv"


DEFAULT_RECORDS = [
    {
        "record_id": "DQ-1001",
        "customer_name": "Ana Paula Costa",
        "email": "ana.costa@example.com",
        "phone": "(21) 99999-1111",
        "city": "Rio de Janeiro",
        "state": "RJ",
        "birth_date": "1989-06-12",
        "income_br": 8200,
        "status": "active",
    },
    {
        "record_id": "DQ-1002",
        "customer_name": "Carlos Mendes",
        "email": "carlos.mendesatexample.com",
        "phone": "21988887777",
        "city": "São Paulo",
        "state": "SP",
        "birth_date": "1994/02/30",
        "income_br": -1500,
        "status": "active",
    },
    {
        "record_id": "DQ-1003",
        "customer_name": "Fernanda Rocha",
        "email": "fernanda.rocha@example.com",
        "phone": "(31) 98888-2222",
        "city": "Belo Horizonte",
        "state": "MG",
        "birth_date": "1978-11-04",
        "income_br": 13200,
        "status": "inactive",
    },
]


def ensure_sample_data() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not DATASET_PATH.exists():
        pd.DataFrame(DEFAULT_RECORDS).to_csv(DATASET_PATH, index=False)
    return pd.read_csv(DATASET_PATH)


def load_dataset() -> pd.DataFrame:
    return ensure_sample_data()


def load_record(record_id: str) -> dict:
    dataset = ensure_sample_data()
    match = dataset.loc[dataset["record_id"] == record_id]
    if match.empty:
        raise KeyError(f"Record id not found: {record_id}")
    return match.iloc[0].to_dict()
