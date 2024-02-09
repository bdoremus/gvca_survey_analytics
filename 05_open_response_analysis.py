import pandas as pd
from sqlalchemy import create_engine

env_vars = dotenv_values()
DATABASE_SCHEMA = env_vars.get('DATABASE_SCHEMA')
DATABASE_CONNECTION_STRING = env_vars.get('DATABASE_CONNECTION_STRING')


def main():
    check_env_vars()
    eng = create_engine(DATABASE_CONNECTION_STRING)
    manual_categorization(eng)


def wordcloud(eng):

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
                        FROM sac_survey_2022.question_open_response
                                 JOIN
                             sac_survey_2022.question using (question_id)
                                 JOIN
                             sac_survey_2022.respondents using (respondent_id)
                        WHERE lower(response) <> 'n/a'
                     """)

    # Create word cloud
    # Don't bother with sentiment analysis ; we already have discrete sentiment data
    # Create separate word clouds or other analysis for groups of users
    #  - sentiment groups
    #  - grammar/upper
    #  - all questions together vs separated
    # manual categorizations/tagging


def analysis_of_categories(eng):
    """
    NOTES:
        Must have a minimum of three responses in a category (arbitrary)
        total <= grammar + upper, since some responses are for both grammar and upper and should not be double counted
        Categories are manually curated and defined
        Worth putting a 0-100 color gradient on percentages

    :param eng: SQL Alchemy engine connected to database
    :return: dataframe with counts and segmentation for each question+sub_question+category
    """
    analysis_query = """
        SELECT question_id,
               sub_question_id,
               category,
               count(*) total,
               count(*) FILTER ( WHERE sentiment = 'positive' )::numeric / count(*) as pct_positive,
               count(*) FILTER ( WHERE grammar) as grammar_total,
               count(*) FILTER ( WHERE grammar and sentiment = 'positive' )::numeric / NULLIF(count(*) FILTER ( WHERE grammar ), 0) as grammar_pct_positive,
               count(*) FILTER ( WHERE upper ) as upper_total,
               count(*) FILTER ( WHERE upper and sentiment = 'positive' )::numeric / NULLIF(count(*) FILTER ( WHERE upper ),0) as upper_pct_positive
        FROM open_response_categories
        GROUP BY question_id, sub_question_id, category
        HAVING count(*) > 2
        ORDER BY question_id, sub_question_id, total DESC, category
        ;
        """
    return pd.read_sql(sql=analysis_query, con=eng)


def manual_categorization(eng):
    _entries = """
        INSERT INTO open_response_categories(question_id, sub_question_id, respondent_id, grammar, upper, category, sentiment)
        VALUES (null, null, null, null, null, null, null) 
        """

    with eng.connect() as conn:
        conn.execute('BEGIN TRANSACTION;')
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")
        conn.execute('TRUNCATE open_response_categories;')

        conn.execute(_entries)

        conn.execute('END TRANSACTION;')

    # Big stories:
    # Upper school attrition,
    # upper school stress,
    # uppper school teachers,
    # volunteering/parents in the classroom,
    # more community events,
    # transgender
    # workload (homework) but NOT reducing the challenge or academic rigor
    # Facebook page is out of control
        # use it to build community!  Book clubs, etc.
    # People don't know about student services


if __name__ == '__main__':
    main()
