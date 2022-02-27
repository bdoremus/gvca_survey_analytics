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
    q9_teacher_entries = """
        INSERT INTO open_response_categories(question_id, sub_question_id, respondent_id, grammar, upper, category, sentiment)
        VALUES -- grammar 
               (9, 'teacher', 13358865684, TRUE, FALSE, 'Discipline', 'negative'),
               (9, 'teacher', 13350194274, TRUE, FALSE, 'Discipline', 'negative'),
               (9, 'teacher', 13353126665, TRUE, FALSE, 'Adaptable', 'positive'),
               (9, 'teacher', 13350191922, TRUE, FALSE, 'Change', 'negative'),
               (9, 'teacher', 13350103733, TRUE, FALSE, 'Communication', 'positive'),
               (9, 'teacher', 13340938452, TRUE, FALSE, 'Values', 'positive'),
               -- upper
               (9, 'teacher', 13358407155, FALSE, TRUE, 'Culture', 'negative'),
               (9, 'teacher', 13350341077, FALSE, TRUE, 'Culture', 'negative'),
               (9, 'teacher', 13359412498, FALSE, TRUE, 'Professional', 'positive'),
               (9, 'teacher', 13350403757, FALSE, TRUE, 'Professional', 'positive'),
               (9, 'teacher', 13359412498, FALSE, TRUE, 'Encouraging', 'positive'),
               (9, 'teacher', 13359596271, FALSE, TRUE, 'Encouraging', 'positive'),
               (9, 'teacher', 13350091052, FALSE, TRUE, 'Encouraging', 'positive'),
               (9, 'teacher', 13354070978, FALSE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13350274734, FALSE, TRUE, 'Communication', 'positive'),
               (9, 'teacher', 13344905413, FALSE, TRUE, 'Workload', 'negative'),
               -- Indistinguishable whether grammar, upper, or both
               (9, 'teacher', 13355187433, TRUE, TRUE, 'Pedagogy', 'negative'), -- Good SMEs, bad teachers
               (9, 'teacher', 13355187433, TRUE, TRUE, 'New teachers', 'negative'), -- Good SMEs, bad teachers
               (9, 'teacher', 13352228496, TRUE, TRUE, 'Pedagogy', 'negative'), -- Good SMEs, bad teachers
               (9, 'teacher', 13352228496, TRUE, TRUE, 'Professional', 'negative'), -- Good SMEs, bad teachers
               (9, 'teacher', 13350431534, TRUE, TRUE, 'Pedagogy', 'negative'), -- Good SMEs, bad teachers
               (9, 'teacher', 13332517163, TRUE, TRUE, 'Pedagogy', 'negative'), -- Good SMEs, bad teachers
               (9, 'teacher', 13350226486, TRUE, TRUE, 'Culture', 'negative'),
               (9, 'teacher', 13359229618, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13358733555, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13358382215, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13358217342, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13356762179, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13354904720, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13352662328, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13350494194, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13350088079, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13357918978, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13351117342, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13350038294, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13352550552, TRUE, TRUE, 'Communication', 'negative'),
               (9, 'teacher', 13350097341, TRUE, TRUE, 'Communication', 'negative'),
               (9, 'teacher', 13351230532, TRUE, TRUE, 'Communication', 'positive'),
               (9, 'teacher', 13344063967, TRUE, TRUE, 'Communication', 'positive'),
               (9, 'teacher', 13344023693, TRUE, TRUE, 'Communication', 'positive'),
               (9, 'teacher', 13339569204, TRUE, TRUE, 'Communication', 'positive'),
               (9, 'teacher', 13351366504, TRUE, TRUE, 'Culture', 'negative'),
               (9, 'teacher', 13351229688, TRUE, TRUE, 'Discipline', 'negative'),
               (9, 'teacher', 13350952349, TRUE, TRUE, 'Change', 'negative'),
               (9, 'teacher', 13351366504, TRUE, TRUE, 'Change', 'negative'),
               (9, 'teacher', 13339166878, TRUE, TRUE, 'New teachers', 'negative'),
               (9, 'teacher', 13339166878, TRUE, TRUE, 'Professional', 'positive'),
               (9, 'teacher', 13331196802, TRUE, TRUE, 'Professional', 'positive'),
               (9, 'teacher', 13332517163, TRUE, TRUE, 'Professional', 'negative'),
               (9, 'teacher', 13355187433, TRUE, TRUE, 'Professional', 'negative'),
               (9, 'teacher', 13336945553, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13332517163, TRUE, TRUE, 'Math', 'negative'),
               (9, 'teacher', 13332405986, FALSE, TRUE, 'Burnout', 'negative'),
               (9, 'teacher', 13331196802, FALSE, TRUE, 'Workload', 'negative'),
               (9, 'teacher', 13329561663, FALSE, TRUE, 'Masks', 'positive'),
               (9, 'teacher', 13324749423, TRUE, FALSE, 'Masks', 'positive'),
               (9, 'teacher', 13329561663, FALSE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13329247001, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13327926290, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13327926290, TRUE, TRUE, 'Communication', 'positive'),
               (9, 'teacher', 13327159788, TRUE, FALSE, 'Communication', 'positive'),
               (9, 'teacher', 13327159788, TRUE, FALSE, 'Adaptable', 'positive'),
               (9, 'teacher', 13327159788, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13324844541, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13324743599, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13324743599, TRUE, FALSE, 'Professional', 'positive'),
               (9, 'teacher', 13324479205, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13323818079, TRUE, FALSE, 'Workload', 'negative'),
               (9, 'teacher', 13323818079, TRUE, TRUE, 'Culture', 'negative'),
               (9, 'teacher', 13323737631, TRUE, TRUE, 'Discipline', 'negative'),
               (9, 'teacher', 13323236051, FALSE, TRUE, 'Workload', 'negative'),
               (9, 'teacher', 13323236051, FALSE, TRUE, 'Humanities', 'negative'),
               (9, 'teacher', 13323236051, FALSE, TRUE, 'Math', 'negative'),
               (9, 'teacher', 13323236051, FALSE, TRUE, 'Latin', 'positive'),
               (9, 'teacher', 13322565597, FALSE, TRUE, 'Latin', 'positive'),
               (9, 'teacher', 13322565597, FALSE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13323236051, FALSE, TRUE, 'Grammar', 'positive'),
               (9, 'teacher', 13320643648, TRUE, FALSE, 'Professional', 'positive'),
               (9, 'teacher', 13320643648, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13319566768, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13319852604, FALSE, TRUE, 'Workload', 'negative'),
               (9, 'teacher', 13319488811, TRUE, TRUE, 'Communication', 'negative'),
               (9, 'teacher', 13319464923, TRUE, FALSE, 'Masks', 'positive'),
               (9, 'teacher', 13319378222, TRUE, TRUE, 'Culture', 'negative'),
               (9, 'teacher', 13319353296, TRUE, FALSE, 'Masks', 'positive'),
               (9, 'teacher', 13319353296, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13317522231, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13318579270, TRUE, FALSE, 'Adaptable', 'positive'),
               (9, 'teacher', 13316527434, FALSE, TRUE, 'Pedagogy', 'negative'),
               (9, 'teacher', 13316454116, FALSE, TRUE, 'Pedagogy', 'negative'),
               (9, 'teacher', 13316454116, TRUE, FALSE, 'Pedagogy', 'positive'),
               (9, 'teacher', 13316454116, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13316352012, TRUE, TRUE, 'Discipline', 'negative'),
               (9, 'teacher', 13315883409, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13315653131, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13315167727, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13314803408, TRUE, TRUE, 'Adaptable', 'positive'),
               (9, 'teacher', 13314383923, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13314308726, TRUE, FALSE, 'New teachers', 'negative'),
               (9, 'teacher', 13314305661, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13314201294, TRUE, TRUE, 'Discipline', 'negative'),
               (9, 'teacher', 13314201294, TRUE, TRUE, 'Communication', 'negative'),
               (9, 'teacher', 13314072215, TRUE, TRUE, 'Professional', 'positive'),
               (9, 'teacher', 13314047190, TRUE, FALSE, 'Discipline', 'negative'),
               (9, 'teacher', 13313942636, TRUE, FALSE, 'Culture', 'negative'),
               (9, 'teacher', 13313892941, TRUE, FALSE, 'Culture', 'negative'),
               (9, 'teacher', 13313880630, TRUE, FALSE, 'Supportive', 'positive'),
               (9, 'teacher', 13313579032, TRUE, TRUE, 'Communication', 'negative'),
               (9, 'teacher', 13313536929, FALSE, TRUE, 'Supportive', 'negative'),
               (9, 'teacher', 13313529346, TRUE, TRUE, 'Culture', 'positive'),
               (9, 'teacher', 13313476580, FALSE, TRUE, 'New teachers', 'negative'),
               (9, 'teacher', 13313428749, FALSE, TRUE, 'Supportive', 'negative'),
               (9, 'teacher', 13313416051, TRUE, TRUE, 'Supportive', 'positive'),
               (9, 'teacher', 13313406816, FALSE, TRUE, 'Communication', 'positive')
               ;
    """

    with eng.connect() as conn:
        conn.execute('BEGIN TRANSACTION;')
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")
        conn.execute('TRUNCATE open_response_categories;')

        conn.executed(q9_teacher_entries)

        conn.execute('END TRANSACTION;')


if __name__ == '__main__':
    main()
