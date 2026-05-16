from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    return pd.read_csv(path, dtype=str, quotechar='"').fillna("")
