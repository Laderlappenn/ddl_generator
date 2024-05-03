import tkinter as tk
# from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter.messagebox import *
import pandas as pd

import ctypes, threading


from utils import get_encoding_type, get_ddl_type, get_engine_type
from updater import update


class DDLGeneratorApp:
    def __init__(self, master):
        self.filetypes = [("CSV files", "*.csv"),
                          ("Excel files", "*.xlsx")]

        self.master = master
        self.master.title("DDL Generator")

        self.label = tk.Label(master, text="Выбор CSV или Excel файла:")
        self.label.pack()

        self.select_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_button.pack()

        # self.dbms_label = tk.Label(master, text="Выбор СУБД:")
        # self.dbms_label.pack()
        #
        # self.dbms = ["Clickhouse", "PostgreSQL"]
        # combobox = ttk.Combobox(values=self.dbms, state="readonly")
        # combobox.pack()

        self.database_name_label = tk.Label(master, text="Введите название базы данных")
        self.database_name_label.pack()

        self.database_name_text = tk.Entry(master)
        self.database_name_text.pack()

        self.table_name_label = tk.Label(master, text="Введите название таблицы")
        self.table_name_label.pack()

        self.table_name_text = tk.Entry(master)
        self.table_name_text.pack()

        self.output_text = tk.Text(master, height=20, width=50)
        self.output_text.pack()

        self.generate_button = tk.Button(master, text="Generate DDL", command=self.generate_ddl)
        self.generate_button.pack()

    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=self.filetypes)
        self.label.config(text="Выбранный файл: " + self.filepath)

    def generate_ddl(self):
        try:
            if self.filepath:
                if self.filepath.endswith('.csv'):
                    try:
                        df = pd.read_csv(self.filepath)
                    except UnicodeDecodeError as unicode_error:
                        popup = ctypes.windll.user32.MessageBoxW
                        threading.Thread(target=lambda: popup(None, 'Автоматическое распознование кодировки', f'{unicode_error.__class__.__name__}', 0)).start()
                        encoding_type = get_encoding_type(self.filepath)
                        df = pd.read_csv(self.filepath, encoding=encoding_type)
                elif self.filepath.endswith('.xlsx'):
                    df = pd.read_excel(self.filepath)
                else:
                    messagebox.showerror("Error", "Unsupported file format")
                    return

                primary_key = next(df.dtypes.items())[0]
                primary_key_type = next(df.dtypes.items())[1]

                ddl_statements = []
                ddl_statements.append(f"CREATE TABLE {self.database_name_text.get()}.{self.table_name_text.get()}\n(")
                ddl_statements.append(f"    `{primary_key}` {primary_key_type},")

                skip_first_iter = True
                for column_name, dtype in df.dtypes.items():
                    if skip_first_iter:
                        skip_first_iter = False
                        continue
                    ddl_statements.append(get_ddl_type(column_name, dtype))

                ddl_statements.append("    `SDU_LOAD_IN_DT` DateTime DEFAULT now()\n)")
                ddl_statements.append(f"ENGINE = {get_engine_type(df)}")
                ddl_statements.append(f"ORDER BY {primary_key}")
                ddl_statements.append("SETTINGS index_granularity = 8192;")

                ddl_output = "\n".join(ddl_statements)
                self.output_text.insert(tk.END, ddl_output)
            else:
                messagebox.showerror("Error", "No file selected")
        except Exception as e:
            messagebox.showerror("Error", str(e) + " " + str(e.__class__.__name__))



def main():
    root = tk.Tk()
    app = DDLGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    success, message = update()
    if success:
        print(message)
    else:
        print("Failed:", message)
    main()
