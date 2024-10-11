Simple script to parse Survey Monkey results into a local database and perform analytics.

## HOW TO
1. Export the results from Survey Monkey.  The following export choices make it the easiest:
   1. Individual Results
   2. All Responses Data
   3. File Format: CSV
   4. Data View: Original View (No rules applied)
   5. Columns: Expanded (I think?)
   6. Cells: Actual Answer Text
2. Set up the python environment using the requirements.txt file
3. Set up a Postgres database (suggest Postgres.App for Mac users)
4. Create a .env file in the root of this directory with the env vars required (see utilities.load_env_vars())
5. Update the Python file with any changes to the survey.  This is harder than it seems, and probably harder than it needs to be.
6. Execute the files in the order given; some on the database, some python scripts.
7. Fix any problems in the scripts
8. Commit your changes and push them back up to the remote git repository
9. Create a release in Github for the current year, so we can rerun prior history if needed.
10. Export the database using pg_dump and each table as a csv.  Save them to the SAC Gdrive.
11. Save all other artifacts to the GDrive.

## Yearly Changelog:

2021-2022:
* First year of processing data this way.
* Release for the version of code used was saved [here](https://github.com/bdoremus/gvca_survey_analytics/releases/tag/year_final)

2022-2023:
* Added `Middle` school as an option.  Previously was just `Grammar` and `Upper`.
* Added the option to complete the survey together with a spouse, or take two surveys separately.  The `respondents.num_individuals_in_response` field is essentially a multiplicative factor which needs to be accounted for when counting survey responses.
* Added technical controls to prevent families from responding to grade-level questions if they did not have a child in that grade level.
* Reduced the options for support services to just a yes/no.
* Included a new collector relevant to handouts given during carline.  This was our first year with a physical presence to remind parents; previously was just the newsletter and Dr. Garrow's email.

2023-2024:
* References to "Upper" school have been replaced with "High" school.
* Fixed some typos in the questions

2024-2025
* Add new way to calculate response rate.  Decision to be made about which to use.
