import os
from chardet import detect


def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']


def get_ddl_type(column_name, dtype):
    if dtype == 'int64':
        return (f"    `{column_name}` Nullable(Int64),")
    elif dtype == 'float64':
        return (f"    `{column_name}` Nullable(Float64),")
    elif dtype == 'datetime64[ns]':
        return (f"    `{column_name}` Nullable(DateTime),")
    elif dtype == 'object':
        return (f"    `{column_name}` Nullable(String),")

def get_engine_type(df):
    if df.shape[0] >= 1_000_000:
        engine = "MergeTree()"
    else:
        engine = "Log"
    return engine
