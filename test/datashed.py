import pandas as pd
import pandas_schema
from pandas_schema.validation import CustomElementValidation
import numpy as np
import unicodedata
import re
import os
import sys

import datetime
from fuzzywuzzy import fuzz
import argparse


def parse_arguments():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_file", type=str, required=False,
                    default='DataShed_Technical_Test.csv',
    	            help="path to input file to be processed")
    ap.add_argument("-o", "--output_file", type=str, required=False,
                    default="summary.txt",
    	            help="type of preprocessing to be done")
    args = vars(ap.parse_args())
    return args["input_file"], args["output_file"]

def open_csv(input_file_name):
    # Confirm that csv file exists, open file using Pandas and check for errors
    df = pd.DataFrame()
    if not os.path.exists(input_file_name):
        print("Unable to find filename provided")

    try:
        df = pd.read_csv(input_file_name)

    except pd.errors.EmptyDataError:
        print("Note: the given .csv was empty.")
    except pd.errors.ParserError:
        print("Error parsing .csv file.")
    if not df.shape[1] == 4:
        print("Wrong number of columns. Was expecting 4 columns.")
        sys.exit()
    return df

def check_string(a_string):
    # Confirm that data is a string, and does not contain numbers
    try:
        str(a_string)
    except InvalidOperation:
        return False
    if len(re.findall('[0-9]', str(a_string))) > 0:
        # This contains numbers
        return False
    return True

def check_date(a_date):
    # Confirm that data is in the expected date format
    date_format = "%d/%m/%Y"
    try:
        datetime.datetime.strptime(a_date, date_format)
    except ValueError:
        return False
    return True

def validate_schema(input_df):
    string_validation = [CustomElementValidation(lambda s: check_string(s), 'is not a string')]
    date_validation = [CustomElementValidation(lambda d: check_date(d), 'is not a correct date')]

    schema = pandas_schema.Schema([
                pandas_schema.Column('given_name', string_validation),
                pandas_schema.Column('surname', string_validation),
                pandas_schema.Column('date_of_birth', date_validation),
                pandas_schema.Column('sex', string_validation)])

    # apply data type validation
    errors = schema.validate(df_people_records)
    errors_index_rows = [error.row for error in errors]

    if len(errors_index_rows) > 0:
        df_invalid_data = df_people_records[df_people_records.index.isin(errors_index_rows)]
        print("Data in these rows did not match expected data type or format:")
        print(df_invalid_data)
        df_invalid_data.to_csv('invalid_data.csv', index=False)

def number_of_records(input_df):
    # Return the number of rows in a Dataframe
    return input_df.shape[0]

def verify_column_names(input_df):
    # Verify that the column names are as expected
    expected_column_names = ['given_name', 'surname', 'date_of_birth', 'sex']
    not_found_message = "Input file has different column names from the Github sample"
    for expected_column in expected_column_names:
        if not expected_column in input_df.columns:
            print(expected_column + " not found. " + not_found_message)
            return False
    return True

if __name__ == "__main__":
    input_file_name, output_file_name = parse_arguments()
    print(input_file_name)
    df_people_records = open_csv(input_file_name)

    # Requirement 1) the number of records in the source data set
    # Capture the number of entries in the dataframe, and assert that there are more than 5 rows
    no_of_records_in_source = number_of_records(df_people_records)
    print("Total number of records in source: " + str(no_of_records_in_source))
    assert no_of_records_in_source > 5, ".csv file does not have enough entries to perform useful comparisons"

    # Validate the record data
    print("Check that the column names are as expected: ")
    print(verify_column_names(df_people_records))


