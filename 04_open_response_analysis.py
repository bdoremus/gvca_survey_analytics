import pandas as pd
from sqlalchemy import create_engine

DATABASE_SCHEMA = 'sac_survey_2022'
DATABASE_CONNECTION_STRING = 'postgresql://bendoremus:@localhost:5432/gvca'


def main():
    eng = create_engine(DATABASE_CONNECTION_STRING)
    df = pd.read_sql(con=eng,
                     sql="""
                        SELECT question_id,
                               question_text,
                               sub_question_id,
                               response,
                               respondent_id,
                               tenure,
                               minority,
                               grammar_conferences,
                               upper_conferences,
                               any_support
                        FROM question_open_response
                                 JOIN
                             question using (question_id)
                                 JOIN
                             respondents using (respondent_id)
                        WHERE lower(response) <> 'n/a'
                     """)

    # Create word cloud
    # Don't bother with sentiment analysis ; we already have discrete sentiment data
    # Create separate word clouds or other analysis for groups of users
    #  - sentiment groups
    #  - grammar/upper
    #  - all questions together vs separated
    # manual categorizations/tagging


if __name__ == '__main__':
    main()
