import pandas as pd
from io import StringIO


class DataImportService:
    def parse_spreadsheet(self, spreadsheet_content):
        file_data = StringIO(spreadsheet_content)
        df = pd.read_csv(file_data, sep="\t")
        df = df.fillna("")
        return df
