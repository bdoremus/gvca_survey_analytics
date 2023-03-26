import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
from utilities import load_env_vars

DATABASE_SCHEMA, DATABASE_CONNECTION_STRING, _ = load_env_vars()


def create_question_summary():
    with create_engine(DATABASE_CONNECTION_STRING).connect() as conn:
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")

        questions = pd.read_sql(con=conn,
                                sql="""
                                    WITH question_avg_score AS
                                             (
                                                 SELECT question_id::text,
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
                                    """
                                ).title.tolist()

        responses = pd.read_sql(con=conn,
                                sql="""
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
                                    GROUP BY response_value"""
                                )

    create_stacked_bar_chart("Response Breakdown by Question", questions, responses)


def create_stacked_bar_chart(title: str, x_axis_labels: list, responses: pd.DataFrame) -> None:
    r1 = responses[responses.response_value == 1].pct.values.tolist()[0]
    r2 = responses[responses.response_value == 2].pct.values.tolist()[0]
    r3 = responses[responses.response_value == 3].pct.values.tolist()[0]
    r4 = responses[responses.response_value == 4].pct.values.tolist()[0]

    fig, ax = plt.subplots()
    ax.bar(x_axis_labels, r4, label='Very', color='#6caf40', bottom=[q1 + q2 + q3 for q1, q2, q3 in zip(r1, r2, r3)])
    ax.bar(x_axis_labels, r3, label='Satisfied', color='#4080af', bottom=[q1 + q2 for q1, q2 in zip(r1, r2)])
    ax.bar(x_axis_labels, r2, label='Somewhat', color='#f6c100', bottom=r1)
    ax.bar(x_axis_labels, r1, label='Not', color='#ae3f3f')
    ax.set_title(title)
    ax.legend(loc="upper center", ncol=4)
    ax.set_xlabel("Question ID\n(avg score)")
    ax.set_ylabel("Proportion")

    plt.tight_layout()
    plt.savefig(f'artifacts/{title}', transparent=True)
    plt.show()


def main():
    create_question_summary()


if __name__ == '__main__':
    main()
