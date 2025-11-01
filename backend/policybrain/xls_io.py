from typing import List, Tuple
import pandas as pd

def load_excel_with_sheets(path: str) -> List[Tuple[int, str]]:
    """
    Returns a list of (sheet_index_1_based, concatenated_text) tuples.
    We flatten each sheet by joining header names and cell values row-wise.
    """
    result: List[Tuple[int, str]] = []
    # read all sheets as dict of DataFrames
    xls = pd.read_excel(path, sheet_name=None, dtype=str, header=0, engine="openpyxl")
    for idx, (sheet_name, df) in enumerate(xls.items(), start=1):
        # normalize NaNs to empty strings
        df = df.fillna("")
        # build a text blob that includes headers and rows
        parts = []
        # headers
        parts.append(" | ".join(map(str, df.columns.tolist())))
        # rows
        for _, row in df.iterrows():
            parts.append(" | ".join(map(str, row.tolist())))
        text = "\n".join(parts)
        # also include the sheet name to help keyword searches
        blob = f"SHEET: {sheet_name}\n{text}"
        result.append((idx, blob))
    return result
