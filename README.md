Simple script to parse Surevy Monkey results into a local database and perform analytics.

## HOW TO
1. Export the results from Survey Monkey.  The following export choices make it the easiest:
   1. Individual Results
   2. All Responses Data
   3. File Format: CSV
   4. Data View: Original View (No rules applied)
   5. Columns: Expanded
   6. Cells: Actual Answer Text

## Important changes for each year:

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
