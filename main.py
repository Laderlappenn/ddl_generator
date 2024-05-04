import tkinter as tk
from tkinter import ttk
from tkinter import BooleanVar
from tkinter import filedialog, messagebox
from tkinter.messagebox import *


import ctypes
import threading


from utils import get_ddl_type, get_engine_type, get_dataframe, timer
from updater import update


class DDLGeneratorApp:
    def __init__(self, master):
        self.filetypes = [("CSV files", "*.csv"),
                          ("Excel files", "*.xlsx")]

        self.master = master
        self.master.title("DDL Generator")

        self.label = tk.Label(master, text="Выбор CSV или Excel файла:")
        self.label.pack(padx=6, pady=6)

        self.select_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_button.pack()

        self.first_10000_rows_bool_var = BooleanVar()
        self.enabled_checkbutton = ttk.Checkbutton(text="Только первые 10000 строк", variable=self.first_10000_rows_bool_var)
        self.enabled_checkbutton.pack(padx=6, pady=6)

        # self.dbms_label = tk.Label(master, text="Выбор СУБД:")
        # self.dbms_label.pack()
        #
        # self.dbms = ["Clickhouse", "PostgreSQL"]
        # combobox = ttk.Combobox(values=self.dbms, state="readonly")
        # combobox.pack()

        self.database_name_label = tk.Label(master, text="Название базы данных")
        self.database_name_label.pack()

        self.database_name_text = tk.Entry(master)
        self.database_name_text.pack(padx=6, pady=6)

        self.table_name_label = tk.Label(master, text="Название таблицы")
        self.table_name_label.pack()

        self.table_name_text = tk.Entry(master)
        self.table_name_text.pack(padx=6, pady=6)

        self.output_text = tk.Text(master, height=20, width=50)
        self.output_text.pack(padx=6, pady=6)

        self.generate_button = tk.Button(master, text="Generate DDL", command=self.generate_ddl)
        self.generate_button.pack()

    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=self.filetypes)
        self.label.config(text="Выбранный файл: " + self.filepath)

    @timer
    def generate_ddl(self):
        try:
            if self.filepath:
                df = get_dataframe(filepath=self.filepath, first_10000_rows=self.first_10000_rows_bool_var.get())
                ddl_statements = []
                ddl_statements.append(f"CREATE TABLE {self.database_name_text.get()}.{self.table_name_text.get()}\n(")

                primary_key = next(df.dtypes.items())[0].upper()
                primary_key_type = next(df.dtypes.items())[1]
                ddl_statements.append(f"    `{primary_key}` {get_ddl_type(primary_key_type)},")

                skip_first_iter = True
                for column_name, dtype in df.dtypes.items():
                    if skip_first_iter:
                        skip_first_iter = False
                        continue

                    ddl_statements.append(f"    `{column_name.upper()}` Nullable({get_ddl_type(dtype)}),")

                ddl_statements.append("    `SDU_LOAD_IN_DT` DateTime DEFAULT now()\n)")
                ddl_statements.append(f"ENGINE = {get_engine_type(self.filepath, first_10000_rows=self.first_10000_rows_bool_var, df=df)}") # i don't like that df here
                                                                                                                                            # because sometimes i don't need it

                if get_engine_type(self.filepath, first_10000_rows=self.first_10000_rows_bool_var, df=df) == "MergeTree()":
                    ddl_statements.append(f"ORDER BY {primary_key}")
                    ddl_statements.append("SETTINGS index_granularity = 8192;\n")
                else:
                    ddl_statements.append("\n")

                ddl_output = "\n".join(ddl_statements)
                self.output_text.insert(tk.END, ddl_output)
            else:
                messagebox.showerror("Error", "No file selected")
        except Exception as e:
            messagebox.showerror("Error", str(e) + "\n" + str(e.__class__.__name__))


def main():
    root = tk.Tk()
    app = DDLGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    update()
    main()
