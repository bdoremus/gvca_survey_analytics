import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine as sqlalchemy_Engine

from utilities import load_env_vars

_, DATABASE_SCHEMA, DATABASE_CONNECTION_STRING = load_env_vars()


def query_to_bar_chart(conn: sqlalchemy_Engine,
                       title: str,
                       x_axis_label: str,
                       x_data_label_query: str,
                       proportion_query: str,
                       subfolder: Path = None
                       ) -> None:
    """
    Execute two queries and modify results to feed the creation of a stacked bar chart.
    :param conn:
    :param title:
    :param x_axis_label:
    :param x_data_label_query:
    :param proportion_query:
    :param subfolder:
    :return:
    """

    x_data_labels = pd.read_sql(con=conn, sql=x_data_label_query).title.tolist()
    proportions = pd.read_sql(con=conn, sql=proportion_query)

    create_stacked_bar_chart(title=title, x_axis_label=x_axis_label, x_data_labels=x_data_labels,
                             proportions=proportions, subfolder=subfolder)


def create_stacked_bar_chart(title: str, x_axis_label: str, x_data_labels: list, proportions: pd.DataFrame, subfolder: Path = None) -> None:
    """
    Save a stacked bar chart to ./artifacts/

    :param x_axis_label:
    :param title:
    :param x_data_labels:
    :param proportions: {bottom_color_in_each_bar: [col1, col2, col3...],
                         second_from_bottom_color_in_each_bar: [col1, col2, col3...], ...}
    :param subfolder: Optional, otherwise use the title
    :return:
    """
    r1 = proportions[proportions.response_value == 1].pct.values.tolist()[0]
    r2 = proportions[proportions.response_value == 2].pct.values.tolist()[0]
    r3 = proportions[proportions.response_value == 3].pct.values.tolist()[0]
    r4 = proportions[proportions.response_value == 4].pct.values.tolist()[0]

    fig, ax = plt.subplots()
    ax.bar(x_data_labels, r4, label='Very', color='#6caf40', bottom=[q1 + q2 + q3 for q1, q2, q3 in zip(r1, r2, r3)])
    ax.bar(x_data_labels, r3, label='Satisfied', color='#4080af', bottom=[q1 + q2 for q1, q2 in zip(r1, r2)])
    ax.bar(x_data_labels, r2, label='Somewhat', color='#f6c100', bottom=r1)
    ax.bar(x_data_labels, r1, label='Not', color='#ae3f3f')

    ax.set_title(title)
    ax.legend(loc="upper center", ncol=4)
    ax.set_xlabel(x_axis_label)
    ax.set_ylabel("Proportion")

    plt.tight_layout()
    plt.savefig(subfolder / title if subfolder else f'artifacts/{title}', transparent=True)
    plt.show()


def create_question_summary(conn):
    query_to_bar_chart(
        conn=conn,
        title="Response Breakdown by Question",
        x_axis_label="Question ID\n(avg score)",
        x_data_label_query="""
            WITH question_avg_score AS
                     (
                         SELECT question_id::TEXT,
                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                         FROM question_rank_responses
                                  JOIN
                              respondents USING (respondent_id)
                         WHERE NOT soft_delete
                         GROUP BY question_id
            
                     UNION ALL
            
                         SELECT 'Total'                                                                                                 AS question_id,
                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                         FROM question_rank_responses
                                  JOIN
                              respondents USING (respondent_id)
                         WHERE NOT soft_delete
            
                         ORDER BY question_id
                     )
            SELECT CONCAT(question_id, E'\n',
                          '(', avg_score, ')'
                       ) AS title
            FROM question_avg_score
            """,
        proportion_query="""
            WITH question_response_counts AS
                     (
                         SELECT question_id::TEXT,
                                response_value,
                                SUM(num_individuals_in_response) AS num_responses
                         FROM question_rank_responses
                                  JOIN
                              respondents USING (respondent_id)
                         WHERE NOT soft_delete
                         GROUP BY question_id, response_value
            
                         UNION ALL
            
                         SELECT 'Total'                          AS question_id,
                                response_value,
                                SUM(num_individuals_in_response) AS num_responses
                         FROM question_rank_responses
                                  JOIN
                              respondents USING (respondent_id)
                         WHERE NOT soft_delete
                         GROUP BY response_value
                     ),
                 question_totals AS
                     (
                         SELECT question_id,
                                SUM(num_responses) AS total
                         FROM question_response_counts
                         GROUP BY question_id
                     )
            SELECT response_value,
                   ARRAY_AGG(num_responses::NUMERIC / total ORDER BY question_id) AS pct
            FROM question_response_counts
                     JOIN
                 question_totals USING (question_id)
            GROUP BY response_value
            """
    )


def create_grade_summary(conn):
    query_to_bar_chart(
        conn=conn,
        title="Response Breakdown by Grade Level",
        x_axis_label="Grade Level\n(avg score)",
        x_data_label_query="""
            WITH question_avg_score AS
                 (
                     SELECT 'Total'                                                                                                 AS question_id,
                            ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
        
                     UNION ALL
                     SELECT 'Grammar'                                                                                               AS question_id,
                            ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND grammar
        
                     UNION ALL
                     SELECT 'Middle'                                                                                               AS question_id,
                            ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND middle
        
                     UNION ALL
                     SELECT 'High'                                                                                               AS question_id,
                            ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND high
                 )
            SELECT CONCAT(question_id, E'\n',
                          '(', avg_score, ')'
                       ) AS title
            FROM question_avg_score
            ORDER BY question_id = 'Total', question_id
            """,
        proportion_query="""
            WITH question_response_counts AS
                 (
                     SELECT 'Grammar' AS question_id,
                            response_value,
                            SUM(num_individuals_in_response) AS num_responses
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete AND grammar
                     GROUP BY response_value
        
                     UNION ALL
                     SELECT 'Middle' AS question_id,
                            response_value,
                            SUM(num_individuals_in_response) AS num_responses
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete AND middle
                     GROUP BY response_value
        
                     UNION ALL
                     SELECT 'High' AS question_id,
                            response_value,
                            SUM(num_individuals_in_response) AS num_responses
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete AND high
                     GROUP BY response_value
        
                     UNION ALL
        
                     SELECT 'Total'                          AS question_id,
                            response_value,
                            SUM(num_individuals_in_response) AS num_responses
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                     GROUP BY response_value
                 ),
             question_totals AS
                 (
                     SELECT question_id,
                            SUM(num_responses) AS total
                     FROM question_response_counts
                     GROUP BY question_id
                 )
            SELECT response_value,
               ARRAY_AGG(num_responses::NUMERIC / total 
                         ORDER BY question_id = 'Total', question_id) AS pct,
               ARRAY_AGG(question_id
                         ORDER BY question_id = 'Total', question_id) AS question_order
        FROM question_response_counts
                 JOIN
             question_totals USING (question_id)
        GROUP BY response_value
        ;
        """
    )


def breakout_by_question(conn):
    # iterate over each question
    questions = pd.read_sql_query(
        sql="""
            SELECT question_id,
                   question_text
            FROM questions
            WHERE question_type = 'rank'
            """,
        con=conn
    )
    for (question_id, question_text) in questions.itertuples(index=False, name=None):
        summarized_text = question_text
        if question_id == 3:
            summarized_text = 'Satisfaction with education'
        elif question_id == 4:
            summarized_text = "Satisfaction with child's intellectual growth"
        elif question_id == 5:
            summarized_text = 'How well is the school culture reflected by the virtues?'
        elif question_id == 6:
            summarized_text = "Satisfaction with child's growth in moral character and civic virtue"
        elif question_id == 7:
            summarized_text = "Communication with teachers"
        elif question_id == 8:
            summarized_text = "Communication with school leadership"

        by_grade_level(conn, question_id, summarized_text)
        by_support_summary(conn, question_id, summarized_text)
        by_minority_summary(conn, question_id, summarized_text)
        by_first_year_family_summary(conn, question_id, summarized_text)
        yoy_question_diff(conn, question_id, summarized_text)


def by_grade_level(conn, question_id, summarized_text):
    """
    Given a question_id, create a chart breaking out each grade into its own column
    """
    subfolder = Path('artifacts/Rank Response - Grade Level')
    subfolder.mkdir(parents=True, exist_ok=True)
    query_to_bar_chart(
        conn=conn,
        title=f'{question_id}: ' + summarized_text,
        subfolder=subfolder,
        x_axis_label='Grade Level',
        x_data_label_query=f"""
            SELECT CASE WHEN grammar THEN 'Grammar'
                        WHEN middle THEN 'Middle'
                        WHEN high THEN 'High'
                        END || 
                        E'\n(' ||
                        ROUND(
                            SUM(response_value * num_individuals_in_response)::NUMERIC /
                                SUM(num_individuals_in_response),
                            2) || 
                        ')' AS title
            FROM question_rank_responses
                     JOIN
                 respondents USING (respondent_id)
            WHERE question_id = {question_id}
            GROUP BY grammar, middle, high
            ORDER BY grammar DESC, middle DESC, high DESC
                """,
        proportion_query=f"""
            WITH expected_values AS
                     (
                         SELECT levels.column1          AS level,
                                levels.column2          AS level_order,
                                response_values.column1 AS response_value
                         FROM (VALUES ('Grammar', 1), ('Middle', 2), ('High', 3)) AS levels,
                              (VALUES (1), (2), (3), (4)) AS response_values
                     ),
                 sum_by_grade AS
                     (
                         SELECT CASE
                                    WHEN grammar THEN 'Grammar'
                                    WHEN middle THEN 'Middle'
                                    WHEN high THEN 'High'
                                    END                          AS level,
                                response_value,
                                SUM(num_individuals_in_response) AS num_responses
                         FROM question_rank_responses
                                  JOIN
                              respondents USING (respondent_id)
                         WHERE question_id = {question_id}
                         GROUP BY level, response_value
                     ),
                 fill_in_blanks AS
                     (
                         -- If a level doesn't have any responses, fill it in as 0
                         SELECT level,
                                level_order,
                                response_value,
                                COALESCE(num_responses, 0) AS num_responses
                         FROM expected_values
                                  LEFT JOIN
                              sum_by_grade USING (level, response_value)
                     ),
                 sum_w_totals AS
                     (
                         SELECT level,
                                SUM(num_responses) AS total
                         FROM fill_in_blanks
                         GROUP BY level
                     )
            SELECT response_value,
                   ARRAY_AGG(num_responses::NUMERIC / total ORDER BY level_order) AS pct
            FROM fill_in_blanks
                     JOIN
                 sum_w_totals USING (level)
            GROUP BY response_value
            ;"""
    )


def by_support_summary(conn, question_id, summarized_text):
    """
    Given a question_id, create a chart breaking out students who received support services from those who did not
    """
    subfolder = Path('artifacts/Rank Response - Student Services')
    subfolder.mkdir(parents=True, exist_ok=True)
    query_to_bar_chart(
        conn=conn,
        title=f'{question_id}: ' + summarized_text,
        subfolder=subfolder,
        x_axis_label='Grade Level',
        x_data_label_query=f"""
            SELECT CASE
                       WHEN respondents.any_support THEN 'Received Support'
                       WHEN NOT any_support THEN 'Did not Receive Support'
                       ELSE 'Did not answer'
                       END ||
                   E'\n(' ||
                   ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                            SUM(num_individuals_in_response),
                         2) ||
                   ')' AS title
            FROM question_rank_responses
                     JOIN
                 respondents USING (respondent_id)
            WHERE question_id = {question_id}
            GROUP BY any_support
            ORDER BY any_support DESC NULLS LAST
                """,
        proportion_query=f"""
            WITH expected_values AS
                     (
                         SELECT demographics.column1    AS demographic,
                                demographics.column2    AS demographic_order, -- any_support desc nulls last
                                response_values.column1 AS response_value
                         FROM (VALUES ('Received Support', 1),
                                      ('Did not Receive Support', 2),
                                      ('Did not answer', 3)) AS demographics,
                              (VALUES (1), (2), (3), (4)) AS response_values
                     ),
                 sum_by_demographic AS
                     (
                         SELECT CASE
                                    WHEN any_support THEN 'Received Support'
                                    WHEN NOT any_support THEN 'Did not Receive Support'
                                    ELSE 'Did not answer'
                                    END                          AS demographic,
                                response_value,
                                SUM(num_individuals_in_response) AS num_responses
                         FROM question_rank_responses
                                  JOIN
                              respondents USING (respondent_id)
                         WHERE question_id = {question_id}
                         GROUP BY demographic, response_value
                     ),
                 fill_in_blanks AS
                     (
                         -- If a demographic doesn't have any responses, fill it in as 0
                         SELECT demographic,
                                demographic_order,
                                response_value,
                                COALESCE(num_responses, 0) AS num_responses
                         FROM expected_values
                                  LEFT JOIN
                              sum_by_demographic USING (demographic, response_value)
                     ),
                 sum_w_totals AS
                     (
                         SELECT demographic,
                                SUM(num_responses) AS total
                         FROM fill_in_blanks
                         GROUP BY demographic
                     )
            SELECT response_value,
                   ARRAY_AGG(num_responses::NUMERIC / total ORDER BY demographic_order) AS pct
            FROM fill_in_blanks
                     JOIN
                 sum_w_totals USING (demographic)
            GROUP BY response_value
            ;"""
    )


def by_minority_summary(conn, question_id, summarized_text):
    subfolder = Path('artifacts/Rank Response - Minority')
    subfolder.mkdir(parents=True, exist_ok=True)
    query_to_bar_chart(
        conn=conn,
        title=f'{question_id}: ' + summarized_text,
        subfolder=subfolder,
        x_axis_label='Grade Level',
        x_data_label_query=f"""
            SELECT CASE
                       WHEN minority THEN 'Minority'
                       WHEN NOT minority THEN 'Not Minority'
                       ELSE 'Did not answer'
                       END ||
                   E'\n(' ||
                   ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                            SUM(num_individuals_in_response),
                         2) ||
                   ')' AS title
            FROM question_rank_responses
                     JOIN
                 respondents USING (respondent_id)
            WHERE question_id = {question_id}
            GROUP BY minority
            ORDER BY minority DESC NULLS LAST
                    """,
        proportion_query=f"""
                WITH expected_values AS
                         (
                             SELECT demographics.column1    AS demographic,
                                    demographics.column2    AS demographic_order, -- any_support desc nulls last
                                    response_values.column1 AS response_value
                             FROM (VALUES ('Minority', 1),
                                          ('Not Minority', 2),
                                          ('Did not answer', 3)) AS demographics,
                                  (VALUES (1), (2), (3), (4)) AS response_values
                         ),
                     sum_by_demographic AS
                         (
                             SELECT CASE
                                        WHEN minority THEN 'Minority'
                                        WHEN NOT minority THEN 'Not Minority'
                                        ELSE 'Did not answer'
                                        END                          AS demographic,
                                    response_value,
                                    SUM(num_individuals_in_response) AS num_responses
                             FROM question_rank_responses
                                      JOIN
                                  respondents USING (respondent_id)
                             WHERE question_id = {question_id}
                             GROUP BY demographic, response_value
                         ),
                     fill_in_blanks AS
                         (
                             -- If a demographic doesn't have any responses, fill it in as 0
                             SELECT demographic,
                                    demographic_order,
                                    response_value,
                                    COALESCE(num_responses, 0) AS num_responses
                             FROM expected_values
                                      LEFT JOIN
                                  sum_by_demographic USING (demographic, response_value)
                         ),
                     sum_w_totals AS
                         (
                             SELECT demographic,
                                    SUM(num_responses) AS total
                             FROM fill_in_blanks
                             GROUP BY demographic
                         )
                SELECT response_value,
                       ARRAY_AGG(num_responses::NUMERIC / total ORDER BY demographic_order) AS pct
                FROM fill_in_blanks
                         JOIN
                     sum_w_totals USING (demographic)
                GROUP BY response_value
                ;"""
    )


def by_first_year_family_summary(conn, question_id, summarized_text):
    subfolder = Path('artifacts/Rank Response - First Year Families')
    subfolder.mkdir(parents=True, exist_ok=True)
    query_to_bar_chart(
        conn=conn,
        title=f'{question_id}: ' + summarized_text,
        subfolder=subfolder,
        x_axis_label='Grade Level',
        x_data_label_query=f"""
            SELECT CASE
                       WHEN tenure = 1 THEN 'First Year Family'
                       WHEN not tenure = 1 THEN 'Returning Family'
                       ELSE 'Did not answer'
                       END ||
                   E'\n(' ||
                   ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                            SUM(num_individuals_in_response),
                         2) ||
                   ')' AS title
            FROM question_rank_responses
                     JOIN
                 respondents USING (respondent_id)
            WHERE question_id = {question_id}
            GROUP BY tenure = 1
            ORDER BY tenure = 1 DESC NULLS LAST
                    """,
        proportion_query=f"""
                WITH expected_values AS
                         (
                             SELECT demographics.column1    AS demographic,
                                    demographics.column2    AS demographic_order, -- any_support desc nulls last
                                    response_values.column1 AS response_value
                             FROM (VALUES ('First Year Family', 1),
                                          ('Returning Family', 2),
                                          ('Did not answer', 3)) AS demographics,
                                  (VALUES (1), (2), (3), (4)) AS response_values
                         ),
                     sum_by_demographic AS
                         (
                             SELECT CASE
                                        WHEN tenure = 1 THEN 'First Year Family'
                                        WHEN NOT tenure = 1 THEN 'Returning Family'
                                        ELSE 'Did not answer'
                                        END                          AS demographic,
                                    response_value,
                                    SUM(num_individuals_in_response) AS num_responses
                             FROM question_rank_responses
                                      JOIN
                                  respondents USING (respondent_id)
                             WHERE question_id = {question_id}
                             GROUP BY tenure = 1, response_value
                         ),
                     fill_in_blanks AS
                         (
                             -- If a demographic doesn't have any responses, fill it in as 0
                             SELECT demographic,
                                    demographic_order,
                                    response_value,
                                    COALESCE(num_responses, 0) AS num_responses
                             FROM expected_values
                                      LEFT JOIN
                                  sum_by_demographic USING (demographic, response_value)
                         ),
                     sum_w_totals AS
                         (
                             SELECT demographic,
                                    SUM(num_responses) AS total
                             FROM fill_in_blanks
                             GROUP BY demographic
                         )
                SELECT response_value,
                       ARRAY_AGG(num_responses::NUMERIC / total ORDER BY demographic_order) AS pct
                FROM fill_in_blanks
                         JOIN
                     sum_w_totals USING (demographic)
                GROUP BY response_value
                ;"""
    )


def q5_student_services(conn):
    query_to_bar_chart(
        conn=conn,
        title='Q5 (Virtues) with Services Received',
        x_axis_label='Group Status\n(avg score)',
        x_data_label_query="""
            WITH question_avg_score AS
                 (
                     SELECT 'Total'                                                                                                 AS secton_id,
                            ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND question_id = 5
        
                     UNION ALL
                     SELECT 'Support Services'                                                                                      AS secton_id,
                            ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND question_id = 5
                       AND any_support
                 )
            SELECT CONCAT(secton_id, E'\n',
                          '(', avg_score, ')'
                       ) AS title
            FROM question_avg_score
            ORDER BY secton_id
            """,
        proportion_query="""
            WITH question_response_counts AS
                 (
                     SELECT 'Total'                          AS question_id,
                            response_value,
                            SUM(num_individuals_in_response) AS num_responses
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND question_id = 5
                     GROUP BY response_value
        
                     UNION ALL
                     SELECT 'Support Services'               AS question_id,
                            response_value,
                            SUM(num_individuals_in_response) AS num_responses
                     FROM question_rank_responses
                              JOIN
                          respondents USING (respondent_id)
                     WHERE NOT soft_delete
                       AND question_id = 5
                       AND any_support
                     GROUP BY response_value
                 ),
                 question_totals AS
                 (
                     SELECT question_id,
                            SUM(num_responses) AS total
                     FROM question_response_counts
                     GROUP BY question_id
                 )
            SELECT response_value,
                   ARRAY_AGG(num_responses::NUMERIC / total ORDER BY question_id) AS pct,
                   ARRAY_AGG(question_id ORDER BY question_id)                    AS question_order
            FROM question_response_counts
                     JOIN
                 question_totals USING (question_id)
            GROUP BY response_value
            """
    )


def yoy_question_diff(conn, question_id, summarized_text):
    subfolder = Path('artifacts/yoy_comparison')
    subfolder.mkdir(parents=True, exist_ok=True)
    query_to_bar_chart(
        conn=conn,
        title=f'{question_id}: ' + summarized_text,
        subfolder=subfolder,
        x_axis_label='',
        x_data_label_query=f"""
            WITH pop_2024 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2024.question_rank_responses
                                  JOIN
                              sac_survey_2024.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                           AND question_id = {question_id} 
                     ),
                 pop_2023 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2023.question_rank_responses
                                  JOIN
                              sac_survey_2023.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                           AND question_id = {question_id}
                     ),
                 distribution AS
                     (
                         SELECT '2024'                                                            AS yr,
                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                                      (SELECT SUM(num_individuals_in_response) FROM pop_2024), 2) AS pct
                         FROM pop_2024

                         UNION ALL

                         SELECT '2023'                                                            AS yr,
                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                                      (SELECT SUM(num_individuals_in_response) FROM pop_2023), 2) AS pct
                         FROM pop_2023
                     )
            SELECT CONCAT(yr, E'\n',
                          '(', pct, ')'
                       ) AS title
            FROM distribution
            ORDER BY yr
            """,
        proportion_query=f"""
            WITH pop_2024 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2024.question_rank_responses
                                  JOIN
                              sac_survey_2024.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                           AND question_id = {question_id}
                     ),
                 pop_2023 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2023.question_rank_responses
                                  JOIN
                              sac_survey_2023.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                           AND question_id = {question_id}
                     ),
                 distribution AS
                     (
                         SELECT '2024'                                                  AS yr,
                                response_value,
                                SUM(num_individuals_in_response)::NUMERIC /
                                (SELECT SUM(num_individuals_in_response) FROM pop_2024) AS pct
                         FROM pop_2024
                         GROUP BY response_value

                         UNION ALL

                         SELECT '2023'                                                  AS yr,
                                response_value,
                                SUM(num_individuals_in_response)::NUMERIC /
                                (SELECT SUM(num_individuals_in_response) FROM pop_2023) AS pct
                         FROM pop_2023
                         GROUP BY response_value

                         ORDER BY response_value
                     )
            SELECT response_value,
                   ARRAY_AGG(pct ORDER BY yr)  AS pct,
                   ARRAY_AGG(yr ORDER BY yr) AS year_order
            FROM distribution
            GROUP BY response_value
            """
    )


def yoy_total_diff(conn):
    subfolder = Path('artifacts/yoy_comparison')
    subfolder.mkdir(parents=True, exist_ok=True)
    query_to_bar_chart(
        conn=conn,
        title='YoY total difference',
        subfolder=subfolder,
        x_axis_label='',
        x_data_label_query="""
            WITH pop_2024 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2024.question_rank_responses
                                  JOIN
                              sac_survey_2024.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                     ),
                 pop_2023 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2023.question_rank_responses
                                  JOIN
                              sac_survey_2023.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                     ),
                 distribution AS
                     (
                         SELECT '2024'                                                            AS yr,
                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                                      (SELECT SUM(num_individuals_in_response) FROM pop_2024), 2) AS pct
                         FROM pop_2024

                         UNION ALL

                         SELECT '2023'                                                            AS yr,
                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC /
                                      (SELECT SUM(num_individuals_in_response) FROM pop_2023), 2) AS pct
                         FROM pop_2023
                     )
            SELECT CONCAT(yr, E'\n',
                          '(', pct, ')'
                       ) AS title
            FROM distribution
            ORDER BY yr
            """,
        proportion_query="""
            WITH pop_2024 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2024.question_rank_responses
                                  JOIN
                              sac_survey_2024.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                     ),
                 pop_2023 AS
                     (
                         SELECT question_id,
                                response_value,
                                num_individuals_in_response
                         FROM sac_survey_2023.question_rank_responses
                                  JOIN
                              sac_survey_2023.respondents USING (respondent_id)
                         WHERE NOT soft_delete
                     ),
                 distribution AS
                     (
                         SELECT '2024'                                                  AS yr,
                                response_value,
                                SUM(num_individuals_in_response)::NUMERIC /
                                (SELECT SUM(num_individuals_in_response) FROM pop_2024) AS pct
                         FROM pop_2024
                         GROUP BY response_value

                         UNION ALL

                         SELECT '2023'                                                  AS yr,
                                response_value,
                                SUM(num_individuals_in_response)::NUMERIC /
                                (SELECT SUM(num_individuals_in_response) FROM pop_2023) AS pct
                         FROM pop_2023
                         GROUP BY response_value

                         ORDER BY response_value
                     )
            SELECT response_value,
                   ARRAY_AGG(pct ORDER BY yr)  AS pct,
                   ARRAY_AGG(yr ORDER BY yr) AS year_order
            FROM distribution
            GROUP BY response_value
            """
    )


def main():
    with create_engine(DATABASE_CONNECTION_STRING).connect() as conn:
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")

        create_question_summary(conn)
        create_grade_summary(conn)
        q5_student_services(conn)
        breakout_by_question(conn)
        yoy_total_diff(conn)


if __name__ == '__main__':
    main()
