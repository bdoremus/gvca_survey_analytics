import pandas as pd
from sqlalchemy import create_engine
from wordcloud import WordCloud, STOPWORDS

from utilities import load_env_vars

_, DATABASE_SCHEMA, DATABASE_CONNECTION_STRING = load_env_vars()


def main():
    eng = create_engine(DATABASE_CONNECTION_STRING)
    with eng.connect() as conn:
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}';")
        build_wordclouds(conn)


def build_wordclouds(conn):
    """
    Create wordclouds for each open response section.
    Have separate plots for each grade level, as well as one with all results together.
    """
    # Curate a list of stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(["GVCA", "School", "Golden", "View", "Academy",
                      "Child", "Children", "Student", "Students", "Kids",
                      "Grader", "Grammar", "Middle", "High",
                      "Year", "Really", "Often", "Don"
                      ])

    # Separate plots for each grade level (and one for all responses together)
    for grade_level, subtitle in [(None, 'All Response'),
                                  ('grammar', 'Grammar'),
                                  ('middle', 'Middle'),
                                  ('high', 'High')]:

        # no `grade_level_filter` when looking at all responses
        grade_level_filter = f'AND {grade_level}' if grade_level else ''
        df = pd.read_sql(con=conn,
                         sql=f"""
                                SELECT question_id,
                                       question_text,
                                       response
                                FROM question_open_responses
                                         JOIN
                                     questions USING (question_id)
                                WHERE response IS NOT NULL
                                      {grade_level_filter}
                             """)

        for question_id in df.question_id.unique():
            # expect one "positive" and one "negative" question
            text = " ".join(df[df.question_id == question_id].response.tolist())
            title = df[df.question_id == question_id].question_text.values[0]

            build_wordcloud(text, stopwords, title, subtitle)


def build_wordcloud(text, stopwords, title, subtitle):
    """
    Generate a word cloud image with a transparent background.
    Save as a file in the artifacts/ folder.
    """
    wordcloud = WordCloud(stopwords=stopwords,
                          max_words=50,
                          min_word_length=3,
                          relative_scaling=1,  # frequency determines word size
                          scale=4,  # image size
                          colormap='PuOr',  # semi-close to GVCA colors.  Can also try YlGnBu
                          background_color=None, mode="RGBA",  # transparent background
                          ).generate(text)
    wordcloud.to_file(f"artifacts/Open Response/{title} - {subtitle}.png")


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
               COUNT(*) total,
               COUNT(*) FILTER ( WHERE sentiment = 'positive' )::NUMERIC / COUNT(*) AS pct_positive,
               COUNT(*) FILTER ( WHERE grammar) AS grammar_total,
               COUNT(*) FILTER ( WHERE grammar AND sentiment = 'positive' )::NUMERIC / NULLIF(COUNT(*) FILTER ( WHERE grammar ), 0) AS grammar_pct_positive,
               COUNT(*) FILTER ( WHERE upper ) AS upper_total,
               COUNT(*) FILTER ( WHERE upper AND sentiment = 'positive' )::NUMERIC / NULLIF(COUNT(*) FILTER ( WHERE upper ),0) AS upper_pct_positive
        FROM open_response_categories
        GROUP BY question_id, sub_question_id, category
        HAVING COUNT(*) > 2
        ORDER BY question_id, sub_question_id, total DESC, category
        ;
        """
    return pd.read_sql(sql=analysis_query, con=eng)


def manual_categorization(eng):
    _entries = """
        INSERT INTO open_response_categories(question_id, sub_question_id, respondent_id, grammar, upper, category, sentiment)
        VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
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
