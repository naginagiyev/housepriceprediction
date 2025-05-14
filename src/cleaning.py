import json
import warnings
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")

class DatasetCleaner:
    def __init__(self, filename):
        self.project_folder = Path().resolve()
        self.data_folder = self.project_folder / "data"
        self.filename = filename
        self.df = None

    def load_data(self):
        with open(self.data_folder / self.filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        self.df = pd.DataFrame(data)

    def rename_columns(self):
        replacements = {
            "kateqoriya": "category", "mərtəbə": "floor", "sahə": "area",
            "otaq sayı": "rooms", "çıxarış": "receipt", "təmir": "repaired", "i̇poteka": "mortgage"
        }
        self.df = self.df.rename(columns=replacements)

    def preprocess_text(self):
        self.df = self.df.map(lambda x: x.lower() if isinstance(x, str) else x)
        self.df = self.df.apply(lambda col: col.str.replace('\xa0', ' ', regex=False) if col.dtype == 'object' else col)

    def process_columns(self):
        self.df["mortgage"] = self.df["mortgage"].map({"var": 1}).fillna(0).astype(int)
        self.df.dropna(inplace=True)
        self.df.drop_duplicates(inplace=True)

        replace_map = {"var": 1, "yoxdur": 0}
        self.df[["repaired", "receipt"]] = self.df[["repaired", "receipt"]].replace(replace_map)

        self.df["category"] = self.df["category"].replace({"yeni tikili": 1, "köhnə tikili": 0})

        self.df[["floor", "max_floor"]] = self.df["floor"].str.extract(r'(\d+)\s*/\s*(\d+)')
        self.df["floor"] = pd.to_numeric(self.df["floor"], errors="coerce")
        self.df["max_floor"] = pd.to_numeric(self.df["max_floor"], errors="coerce")

        self.df["area"] = self.df["area"].str.extract(r'(\d+)')
        self.df["price"] = self.df["price"].str.replace(' ', '')

    def set_column_types(self):
        column_types = {
            "latitude": "float64", "longitude": "float64", "price": "int64", "address": "object",
            "category": "int64", "floor": "int64", "area": "int64", "rooms": "int64",
            "receipt": "int64", "repaired": "int64", "mortgage": "int64", "max_floor": "int64"
        }
        self.df = self.df.astype(column_types)
        self.df = self.df[["address", "latitude", "longitude", "area", "rooms", "floor",
                           "max_floor", "category", "repaired", "receipt", "mortgage", "price"]]

    def save_to_excel(self, filename):
        if filename:
            save_path = self.data_folder / f"{filename}.xlsx"
        else:
            save_path = self.data_folder / f"cleaned_{self.filename}".replace("json", "xlsx")
        self.df.to_excel(save_path, index=False)
        return save_path

    def clean(self, filename=None):
        self.load_data()
        self.rename_columns()
        self.preprocess_text()
        self.process_columns()
        self.set_column_types()
        return self.save_to_excel(filename)

cleaner = DatasetCleaner("ootdata.json")
cleaner.clean("ootnew")