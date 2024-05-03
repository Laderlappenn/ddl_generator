from chardet import detect


def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']


def get_ddl_type(dtype):
    if dtype == 'int64':
        return "Int64"
    elif dtype == 'float64':
        return "Float64"
    elif dtype == 'datetime64[ns]':
        return "DateTime"
    elif dtype == 'object':
        return "String"

def get_engine_type(df):
    if df.shape[0] >= 1_000_000:
        engine = "MergeTree()"
    else:
        engine = "Log"
    return engine
