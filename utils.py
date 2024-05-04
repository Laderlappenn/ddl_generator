from tkinter import messagebox
import ctypes
import threading
import csv


from chardet import detect
import pandas as pd



def get_delimiter(file_path: str) -> str:
    with open(file_path, 'r') as csvfile:
        delimiter = str(csv.Sniffer().sniff(csvfile.read(1024)).delimiter)
        return delimiter


def get_dataframe(filepath, first_10000_rows=False, rows_num=None):

    if first_10000_rows:
        nrows = 10000
        low_memory = True
    elif first_10000_rows is False:
        nrows = rows_num
        low_memory = False

    if filepath.endswith('.csv'):
        try:
            if get_delimiter(filepath) == ";":
                df = pd.read_csv(filepath, nrows=nrows, low_memory=low_memory, na_filter=False, delimiter=";")
            else:
                df = pd.read_csv(filepath, nrows=nrows, low_memory=low_memory, na_filter=False)
        except UnicodeDecodeError as unicode_error:
            popup = ctypes.windll.user32.MessageBoxW
            threading.Thread(
                target=lambda: popup(None, 'Автоматическое распознование кодировки', f'{unicode_error.__class__.__name__}',0)
            ).start()
            encoding_type = get_encoding_type(filepath)
            df = pd.read_csv(filepath, encoding=encoding_type, nrows=nrows, low_memory=low_memory, na_filter=False)
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        messagebox.showerror("Error", "Unsupported file format")
        return
    return df



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
