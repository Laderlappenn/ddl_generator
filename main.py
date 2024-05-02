import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd

from utils import get_encoding_type


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

        self.dbms_label = tk.Label(master, text="Выбор СУБД:")
        self.dbms_label.pack()

        self.dbms = ["Clickhouse", "PostgreSQL"]
        combobox = ttk.Combobox(values=self.dbms, state="readonly")
        combobox.pack()

        self.database_name_label = tk.Label(master, text="Введите название базы данных")
        self.database_name_label.pack()

        self.database_name_text = tk.Entry(master)
        self.database_name_text.pack()

        self.table_name_label = tk.Label(master, text="Введите название таблицы")
        self.table_name_label.pack()

        self.database_name_text = tk.Entry(master)
        self.database_name_text.pack()

        self.output_text = tk.Text(master, height=20, width=50)
        self.output_text.pack()

        self.generate_button = tk.Button(master, text="Generate DDL", command=self.generate_ddl)
        self.generate_button.pack()

    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=self.filetypes)
        self.label.config(text="Выбранный файл: " + self.filepath)

    def generate_ddl(self):
        try:
            encoding_type = get_encoding_type(self.filepath)
            if self.filepath:
                if self.filepath.endswith('.csv'):
                    df = pd.read_csv(self.filepath, encoding=encoding_type)
                elif self.filepath.endswith('.xlsx'):
                    df = pd.read_excel(self.filepath)
                else:
                    messagebox.showerror("Error", "Unsupported file format")
                    return

                ddl_statements = []
                ddl_statements.append(f"CREATE TABLE database.table\n(")
                for column_name, dtype in df.dtypes.items():
                    if dtype == 'int64':
                        ddl_statements.append(f"    `{column_name}` Int64,")
                    elif dtype == 'float64':
                        ddl_statements.append(f"    `{column_name}` Float64,")
                    elif dtype == 'datetime64[ns]':
                        ddl_statements.append(f"    `{column_name}` DateTime,")
                    elif dtype == 'object':
                        ddl_statements.append(f"    `{column_name}` String,")
                    # Add more data types as needed
                ddl_statements.append(f")\nENGINE = MergeTree()\nORDER BY CounterID")


                ddl_output = "\n".join(ddl_statements)
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert(tk.END, ddl_output)
            else:
                messagebox.showerror("Error", "No file selected")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = DDLGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
