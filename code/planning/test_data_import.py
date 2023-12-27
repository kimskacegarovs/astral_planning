import pytest
import pandas as pd
from .data_import import DataImportService


class TestDataImportService:
    @pytest.fixture
    def data_import_service(self):
        return DataImportService()

    def test_parse_spreadsheet_with_valid_data(self, data_import_service):
        # Given valid tab-separated data
        valid_data = "Name\tAge\tCountry\nAlice\t25\tUSA\nBob\t30\tCanada"

        # When parse_spreadsheet is called with valid data
        result_df = data_import_service.parse_spreadsheet(valid_data)

        # Then it returns a pandas DataFrame
        assert isinstance(result_df, pd.DataFrame)

        # Then it has the expected number of rows and columns
        assert result_df.shape == (2, 3)

        # Then it contains specific values in the DataFrame
        assert result_df.iloc[0]["Name"] == "Alice"
        assert result_df.iloc[1]["Age"] == 30
