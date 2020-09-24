import pytest
from io import BytesIO, StringIO
from datashed import *
import pandas


class TestCheckString(object):

    def test_check_string_with_string(self):
        assert check_string("a string") is True

    def test_check_string_with_number(self):
        assert check_string(10) is False


class TestCheckDate(object):

    def test_check_date(self):
        assert check_date("23/09/2020") is True
    
    def test_wrong_date_format(self):
        assert check_date("2020/09/23") is False
    
    def test_string(self):
        assert check_date("a string") is False

class TestNumberOfRecords(object):

    def test_number_of_records(self):
        d = {'col1': [1, 2], 'col2': [3, 4]}
        test_df = pd.DataFrame(data=d)
        assert number_of_records(test_df) == 2


"""
# Cannot work out how to use dataframes in fixtures. Want to be able to create a dummy valid dataframe,
# and some dummy invalid dataframes, so that can re-use these across multiple test objects.
@pytest.fixture
def good_df():
    return pd.DataFrame(
        data=[
            ['John', 'Smith', '01/01/2000', 'm'],
            ['Joe', 'Bloggs', '10/10/1990', 'm'],
            ['Jane', 'Doe', '08/08/1995', 'f']
        ],
        columns=['given_name', 'surname', 'date_of_birth', 'sex'],
    )


class TestDataValidation(object):

    def test_verify_column_names_with_correct_names(good_df):
        print(good_df.columns)
        assert verify_column_names(good_df) is True
"""