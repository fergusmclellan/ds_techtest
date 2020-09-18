#DataShed Technical Test
##Requirements
The application should:

Read data from the source file Output:

1) the number of records in the source data set

2) the number of unique records* in the source data set

3) the number of different people** in the source data set

4) Write the data that is considered duplicated/related to a CSV file called relateddata.csv

5) Consider data that is similar and classify it as a duplicated/related. For example "Wilyam Premadasta" and "William Premadasa" should be considered the same person.

*exact duplicate records should be eliminated from this measure.

** the number of records following your de-duplication processing.

##Solution
My solution is based on Python 3, relying heavily on Pandas to import and clean the data. The "fuzzywuzzy" module is used to assist with the identification of records which are related with similar given names and surnames. The requirements give no indication as to how much weight should be given to the date of birth, and there are a number of records which have the same names, but a very different date of birth. For the purposes of this solution, it is assumed that the date of birth is correct, and we are identifying records which have the same date of birth and similar names. There is also no direction given as to whether or not any errors in the sex provided should be captured, as there are a large number of "v" entries.


##Setup
<ol>
<li>Use the requirements.txt to install the required Python modules:</li>
pip install -r requirements.txt
<li>Run the script from the command line or terminal using "python datashed.py"</li>
<li>The default input .csv file and default output summary file can be changed using the -i and -o flags. 
  Use "python datashed.py --help" for more information
</ol>

The Jenkinsfile which was used for testing the script in Docker is included on Github.

Due to the use of Pandas, a Jupyter Notebook of the prototype solution is also included here for convenience. 

##Output files
summary.txt - contains the summary information and figures for the number of records and duplicates outlined in the requirements
exact_duplicates.csv - contains the records which have an exact duplicate
related.csv - contains the data that is considered related, with the related pair records listed side by side
cleaned.csv - contains the final data which has had duplicate and the 2nd occurence of a related record removed
invalid_data.csv - contains the records which did not contain data in the expected format. Some entries were identified with an inconsistent date format.
