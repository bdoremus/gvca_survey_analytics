import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
from utilities import load_env_vars

DATABASE_SCHEMA, DATABASE_CONNECTION_STRING, _ = load_env_vars()


def query_to_bar_chart(title: str, x_axis_label: str, x_data_label_query: str, proportion_query: str) -> None:
    """
    Execute two queries and modify results to feed the creation of a stacked bar chart

    :param title:
    :param x_axis_label:
    :param x_data_label_query:
    :param proportion_query:
    :return:
    """
    with create_engine(DATABASE_CONNECTION_STRING).connect() as conn:
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")

        x_data_labels = pd.read_sql(con=conn, sql=x_data_label_query).title.tolist()
        proportions = pd.read_sql(con=conn, sql=proportion_query)

    create_stacked_bar_chart(title=title, x_axis_label=x_axis_label, x_data_labels=x_data_labels, proportions=proportions)


def create_stacked_bar_chart(title: str, x_axis_label: str, x_data_labels: list, proportions: pd.DataFrame) -> None:
    """
    Save a stacked bar chart to ./artifacts/

    :param x_axis_label:
    :param title:
    :param x_data_labels:
    :param proportions: {response_value_1: [q1, q2, q3...], response_value_2: [q1, q2, q3...], ...}
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
    plt.savefig(f'artifacts/{title}', transparent=True)
    plt.show()


def create_question_summary():
    query_to_bar_chart(title="Response Breakdown by Question",
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


def create_grade_summary():
    query_to_bar_chart(title="Response Breakdown by Grade Level",
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


def q5_student_services():
    query_to_bar_chart(title='Q5 (Virtues) with Services Received',
                       x_axis_label='Group Status\n(avg score)',
                       x_data_label_query="""
                            WITH question_avg_score AS
                                     (
                                         SELECT 'Total'                                                                                                 AS question_id,
                                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                                         FROM question_rank_responses
                                                  JOIN
                                              respondents USING (respondent_id)
                                         WHERE NOT soft_delete
                                           AND question_id = 5
                            
                                         UNION ALL
                                         SELECT 'Support Services'                                                                                      AS question_id,
                                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / SUM(num_individuals_in_response), 2) AS avg_score
                                         FROM question_rank_responses
                                                  JOIN
                                              respondents USING (respondent_id)
                                         WHERE NOT soft_delete
                                           AND question_id = 5
                                           AND any_support
                                     )
                            SELECT CONCAT(question_id, E'\n',
                                          '(', avg_score, ')'
                                       ) AS title
                            FROM question_avg_score
                            ORDER BY question_id
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


def yoy_total_diff():
    query_to_bar_chart(title='',
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
                                 distribution AS
                                     (
                                         SELECT '2024'                                                                                                                         AS year,
                                                ROUND(SUM(response_value * num_individuals_in_response)::NUMERIC / (SELECT SUM(num_individuals_in_response) FROM pop_2024), 2) AS pct
                                         FROM pop_2024
                            
                                         UNION ALL
                            
                                         SELECT '2023'                                                                                                               AS year,
                                                ROUND(SUM(response)::NUMERIC / (SELECT COUNT(*) AS num_responses FROM sac_survey_2023.question_rank), 2) AS pct
                                         FROM sac_survey_2023.question_rank
                                     )
                            SELECT CONCAT(year, E'\n',
                                          '(', pct, ')'
                                       ) AS title
                            FROM distribution
                            ORDER BY year
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
                                 distribution AS
                                     (
                                         SELECT '2024'                                                                                              AS year,
                                                response_value,
                                                SUM(num_individuals_in_response)::NUMERIC / (SELECT SUM(num_individuals_in_response) FROM pop_2024) AS pct
                                         FROM pop_2024
                                         GROUP BY response_value
                            
                                         UNION ALL
                            
                                         SELECT '2023'                                                                                                AS year,
                                                response,
                                                COUNT(*)::NUMERIC / (SELECT COUNT(*) AS num_responses FROM sac_survey_2023.question_rank) AS pct
                                         FROM sac_survey_2023.question_rank
                                         GROUP BY response
                            
                                         ORDER BY response_value
                                     )
                            SELECT response_value,
                                   ARRAY_AGG(pct ORDER BY year) as pct,
                                   ARRAY_AGG(year ORDER BY year) as year_order
                            FROM distribution
                            GROUP BY response_value
                            """
                       )


def main():
    create_question_summary()
    create_grade_summary()
    q5_student_services()
    # yoy_total_diff()


if __name__ == '__main__':
    main()
