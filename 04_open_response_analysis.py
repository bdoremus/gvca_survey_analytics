import pandas as pd
from sqlalchemy import create_engine

DATABASE_SCHEMA = 'sac_survey_2022'
DATABASE_CONNECTION_STRING = 'postgresql://bendoremus:@localhost:5432/gvca'


def main():
    eng = create_engine(DATABASE_CONNECTION_STRING)
    df = pd.read_sql(con=eng,
                     sql="""
                        SELECT question_id,
                        question_text
                        FROM question_open_response
                            JOIN
                                question using(question_id)
                     """)


if __name__ == '__main__':
    main()
