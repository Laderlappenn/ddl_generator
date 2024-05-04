from tkinter import messagebox
import ctypes
import threading
import csv
import time


from chardet import detect
import pandas as pd



def get_delimiter(file_path: str) -> str:
    with open(file_path, 'r') as csvfile:
        delimiter = str(csv.Sniffer().sniff(csvfile.readline()).delimiter)
        return delimiter


def get_dataframe(filepath, first_10000_rows=False, rows_num=None):

    if first_10000_rows:
        nrows = 10000
        low_memory = True
    elif first_10000_rows is False:
        nrows = rows_num
        low_memory = False

    if filepath.endswith('.csv'):
        delimiter = get_delimiter(filepath)
        try:
            df = pd.read_csv(filepath, nrows=nrows, low_memory=low_memory, na_filter=False, delimiter=delimiter)
        except UnicodeDecodeError as unicode_error:
            popup = ctypes.windll.user32.MessageBoxW
            threading.Thread(
                target=lambda: popup(None, 'Автоматическое распознование кодировки', f'{unicode_error.__class__.__name__}',0)
            ).start()
            encoding_type = get_encoding_type(filepath)
            df = pd.read_csv(filepath, encoding=encoding_type, nrows=nrows, low_memory=low_memory, na_filter=False, delimiter=delimiter)
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        messagebox.showerror("Error", "Unsupported file format")
        return
    return df



def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read(1024)
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

# TODO do smth
def get_engine_type(file_name, first_10000_rows=False, df=None):
    if first_10000_rows:
        with open(file_name) as f:
            line_count = sum(1 for line in f)
    else:
        line_count = df.shape[0]
    if line_count >= 1_000_000:
        engine = "MergeTree()"
    else:
        engine = "Log"
    return engine


def check_cyrillic(column):
    cyrillic_alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й',
                         'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
                         'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
    for char in column:
        if char.lower() in cyrillic_alphabet:
            return True
        return False


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of '{func.__name__}': {execution_time:.6f} seconds")
        return result
    return wrapper

