"""
datashed.py
Fergus McLellan
18th September 2020
"""


# Import required modules
import pandas as pd
import pandas_schema
from pandas_schema.validation import CustomElementValidation
import numpy as np
import unicodedata
import re
import os
import datetime
from fuzzywuzzy import fuzz
import argparse

# Increase the fuzz_score to capture fewer similarities, and return more strict comparisons
# Decrease the v to capture more vague similarities
fuzz_score = 50

def parseArguments():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_file", type=str, required=False,
                    default='DataShed_Technical_Test.csv',
    	            help="path to input file to be processed")
    ap.add_argument("-o", "--output_file", type=str, required=False,
                    default="summary.txt",
    	            help="type of preprocessing to be done")
    args = vars(ap.parse_args())
    return args



def check_for_similar_record(input_date):
    """
    check_for_similar_record - takes a date as input
    Retrieves all rows which include that date, and creates dictionaries of the given names and surnames.
    Fuzzywuzzy is used to score the similarity between the given names and the surnames.

    Any pair of row indexes which have a score of greater than 'fuzz_score' (set to 50, but this can be modified)
    for both the given name and the surname are considered to be similar.

    Output: row indices for the 2 records which are considered to be similar
    """
    given_names_dict = dict(enumerate(df_cleaned_records[df_cleaned_records['date_of_birth'] == input_date]['ascii_given_name']))
    surnames_dict = dict(enumerate(df_cleaned_records[df_cleaned_records['date_of_birth'] == input_date]['ascii_surname']))
    index_dict = dict(enumerate(df_cleaned_records[df_cleaned_records['date_of_birth'] == input_date].index))
    for this_record in range(len(surnames_dict)):
        for compare_record in range(len(surnames_dict)):
            # do not compare record against itself
            if not compare_record == this_record:
                given_name_score =  fuzz.ratio(given_names_dict[this_record], given_names_dict[compare_record])
                if given_name_score > fuzz_score:
                    surname_score =  fuzz.ratio(surnames_dict[this_record], surnames_dict[compare_record])
                    if surname_score > fuzz_score:
                        return index_dict[this_record], index_dict[compare_record]

def check_string(a_string):
    try:
        str(a_string)
    except InvalidOperation:
        return False
    return True

def check_date(a_date):
    try:
        datetime.datetime.strptime(a_date, date_format)
    except ValueError:
        return False
    return True


args = parseArguments()
input_file_name = args["input_file"]
output_file_name = args["output_file"]

# Open file and check for errors
if not os.path.exists(input_file_name):
    print("Unable to find filename provided")

try:
    df_people_records = pd.read_csv(input_file_name)

except pd.errors.EmptyDataError:
    print("Note: the given .csv was empty.")
except pd.errors.ParserError:
    print("Error parsing .csv file.")


# Requirement 1) the number of records in the source data set
# Capture the number of entries in the dataframe, and assert that there are more than 5 rows
no_of_records_in_source = df_people_records.shape[0]
print("Total number of records in source: " + str(no_of_records_in_source))
assert no_of_records_in_source > 5, ".csv file does not have enough entries to perform useful comparisons"

# Check that the column names are as expected
expected_column_names = ['given_name', 'surname', 'date_of_birth', 'sex']
column_assert_message = "Input file has different column names from the Github sample"
for expected_column in expected_column_names:
    assert expected_column in df_people_records.columns, expected_column + " not found. " + column_assert_message

df_people_records.head()

# Requirement 2) the number of unique records in the source data set
# Duplicates are captured, and saved to a separate file, exact_duplicates.csv
df_duplicate_records = df_people_records[pd.DataFrame.duplicated(df_people_records)]
df_duplicate_records.to_csv('exact_duplicates.csv', index=False)

# Remove duplicates from current dataFrame
df_people_records = df_people_records.drop_duplicates()
number_of_unique_records = df_people_records.shape[0]
print("Number of unique records: " + str(number_of_unique_records))

# Validate that all input data contains string or date information
# The bulk of the date of birth data is in dd/mm/YYYY date format.
# However, a small number of entries were found with inconsistent dates.
date_format = "%d/%m/%Y"



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

# New dataframe with any invalid data rows dropped
df_cleaned_records = df_people_records.drop(index=errors_index_rows)

# Unicode data found in data source - this makes comparison operations difficult.
# Convert unicode characters into their ascii equivalent equivalent characters
df_cleaned_records["ascii_given_name"] = df_cleaned_records['given_name'].apply(lambda x: str(unicodedata.normalize('NFKD', str(x)).encode('ascii', 'ignore')).split("'")[1])
df_cleaned_records["ascii_surname"] = df_cleaned_records['surname'].apply(lambda x: str(unicodedata.normalize('NFKD', str(x)).encode('ascii', 'ignore')).split("'")[1])

# Remove anything which is not a letter, e.g. hyphen, apostrophes, etc.
regex = re.compile('[^a-zA-Z]')
df_cleaned_records["ascii_given_name"] = df_cleaned_records["ascii_given_name"].apply(lambda x: regex.sub('', x))
df_cleaned_records["ascii_surname"] = df_cleaned_records["ascii_surname"].apply(lambda x: regex.sub('', x))

# create a list of tuples, which contain the dataFrame indices for any matching record pairs
fuzzy_matched_records = [check_for_similar_record(x) for x in df_cleaned_records[df_cleaned_records.duplicated(subset=['date_of_birth'])]['date_of_birth'].unique()]

# Drop any empty entries from list
if len(fuzzy_matched_records) > 0:
    fuzzy_matched_records = [idx for idx in fuzzy_matched_records if idx]


# Create DataFrame of the fuzzy matched records
if len(fuzzy_matched_records) > 0:
    df_fuzzy_matched_records = pd.concat([
        pd.DataFrame([df_cleaned_records.loc[idx[0]] for idx in fuzzy_matched_records]).reset_index(drop=True),
        pd.DataFrame([df_cleaned_records.loc[idx[1]] for idx in fuzzy_matched_records]).reset_index(drop=True)],
        axis=1, ignore_index=True)

# Drop Ascii versions of columns to leave the original encoding versions
df_fuzzy_matched_records.drop([4, 5, 10, 11], axis='columns', inplace=True)

# Rename fuzzy matched columns
df_fuzzy_matched_records.columns = ['given_name_A', 'surname_A', 'date_of_birth_A', 'sex_A',
                                    'given_name_B', 'surname_B', 'date_of_birth_B', 'sex_B']

number_of_pairs_of_similar_records = df_fuzzy_matched_records.shape[0]

# Drop 2nd fuzzy match from original dataframe, and drop the ascii columns
df_cleaned_records.drop([idx[1] for idx in fuzzy_matched_records if idx], axis=0, inplace=True)
df_cleaned_records.drop(columns=['ascii_given_name', 'ascii_surname'], inplace=True)

df_cleaned_records.to_csv('cleaned.csv', index=False)

# Requirement 3) the number of different people in the source data set

number_of_different_people = df_cleaned_records.shape[0]
print("Number of different people: " + str(number_of_different_people))

# Requirement 4) Write the data that is considered duplicated/related to a CSV file called relateddata.csv

df_fuzzy_matched_records.to_csv('relateddata.csv', index=False)

# Create summary file
output_file = open(output_file_name, "w")
output_file.write("Summary information on the records in the input file: " + input_file_name + '\n')
output_file.write("====================================================================" + '\n\n')
output_file.write("Total number of records in source: " + str(no_of_records_in_source) + '\n')
output_file.write("Number of unique records: " + str(number_of_unique_records) + '\n')
output_file.write("Number of pairs of similar records: " + str(number_of_pairs_of_similar_records) + '\n')
output_file.write("Number of different people: " + str(number_of_different_people) + '\n')
output_file.close()
