Simple script to parse Surevy Monkey results into a local database and perform analytics.

Important changes for each year:

2021-2022:
* First year of processing data this way

2022-2023:
* Added `Middle` school as an option.  Previously was just `Grammar` and `Upper`.
* Added the option to complete the survey together with a spouse, or take two surveys separately.  The `respondents.num_individuals_in_response` field is essentially a multiplicative factor which needs to be accounted for when counting survey responses.
* Added technical controls to prevent families from responding to grade-level questions if they did not have a child in that grade level.
* Reduced the options for support services to just a yes/no.
* Included a new collector relevant to handouts given during carline.  This was our first year with a physical presence to remind parents; previously was just the newsletter and Dr. Garrow's email.
