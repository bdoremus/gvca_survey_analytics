from csv import reader as csv_reader
from sqlalchemy import create_engine, text
from pprint import pprint

INPUT_FILEPATH = '/Users/bendoremus/Downloads/2022 Parent Satisfaction Survey.csv'
DATABASE_SCHEMA = 'sac_survey_2022'
DATABASE_CONNECTION_STRING = 'postgresql://bendoremus:@localhost:5432/gvca'


def inspect_file():
    """
    Run only to check out the file structure and figure out what is in each column
    :return:
    """
    # get headers, organize columns
    with open(INPUT_FILEPATH, 'r') as f_in:
        raw_data_reader = csv_reader(f_in)
        raw_header = raw_data_reader.__next__()
        raw_sub_header = raw_data_reader.__next__()
        ignore_sub_headers = ['Open-Ended Response', 'Response']

        # fill empty columns with the appropriate question
        questions = []
        for i, (question, sub_question) in enumerate(zip(raw_header, raw_sub_header)):
            questions += [(i,
                           (question if question else questions[-1][1]),
                           (sub_question if sub_question and sub_question not in ignore_sub_headers else None))]

    pprint(questions)


def validate_header(header, sub_header):
    assert header[0] == 'Respondent ID'
    assert header[2] == 'Start Date'
    assert header[3] == 'End Date'
    assert header[9] == 'How many years have you had a child at Golden View Classical Academy?  The current academic year counts as 1.'
    assert header[10] == 'Did you or one of your children attend conferences this year?'
    assert header[12] == 'Given your children’s education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?'
    assert header[14] == 'How satisfied are you with the education that your children have received at Golden View Classical Academy this year?'
    assert header[16] == 'GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How strongly is the school culture influenced by those virtues?'
    assert header[18] == "How effective is the communication between your family and your childrens' teachers?"
    assert header[20] == 'How effective is the communication between your family and the school leadership?'
    assert header[21] == 'How welcoming is the school community?'
    assert header[23] == "Given this year's challenges, what are your thoughts on the following aspects of the school environment?"
    assert header[27] == "What makes GVCA a good choice for you and your family?"
    assert header[30] == 'Please provide us with examples of how GVCA can better serve you and your family.'
    assert header[33] == 'What services have your children received at Golden View this school year? Please check all that apply.'
    assert header[52] == 'Do you consider yourself or your children part of a racial, ethnic, or cultural minority group?'


def main():
    """
    Insert rows of data into the database.  Tables must already exist.

    :return:
    """
    eng = create_engine(DATABASE_CONNECTION_STRING)
    with open(INPUT_FILEPATH, 'r') as f_in, eng.connect() as conn:
        raw_data_reader = csv_reader(f_in)

        header = raw_header = raw_data_reader.__next__()
        sub_header = raw_sub_header = raw_data_reader.__next__()
        validate_header(header, sub_header)

        # database setup
        conn.execute('BEGIN TRANSACTION;')
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")
        # TODO: Remove the TRUNCATE before pushing to prod!
        conn.execute(f'TRUNCATE respondents CASCADE;')

        # each row represents one respondent's answers to each question.
        # Parse each row into separate tables
        for row in raw_data_reader:
            respondent_id = row[0]
            # Create the respondent, including demographic information
            add_to_table(
                conn,
                tablename='respondents',
                respondent_id=respondent_id,
                collector_id=row[1],
                start_datetime=row[2],
                end_datetime=row[3],
                tenure=int(row[9]) if row[9] else None,
                grammar_conferences=convert_to_bool(row[10]),
                upper_conferences=convert_to_bool(row[11]),
                grammar_support=any(row[33:51:2]), # student services questions alternate between grammar/upper responses
                upper_support=any(row[34:51:2]),
                any_support=any(row[34:52]),
                minority=convert_to_bool(row[52]),
            )

            # question 3:
            # Given your children’s education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?
            insert_rank_responses_split_by_grammar_upper(
                conn,
                question_id=3,
                respondent_id=respondent_id,
                grammar_response=convert_to_int(row[12]),
                upper_response=convert_to_int(row[13]),
            )

            # question 4:
            # How satisfied are you with the education that your children have received at Golden View Classical Academy this year?
            insert_rank_responses_split_by_grammar_upper(
                conn,
                question_id=4,
                respondent_id=respondent_id,
                grammar_response=convert_to_int(row[14]),
                upper_response=convert_to_int(row[15]),
            )

            # question 5:
            # GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How strongly is the school culture influenced by those virtues?
            insert_rank_responses_split_by_grammar_upper(
                conn,
                question_id=5,
                respondent_id=respondent_id,
                grammar_response=convert_to_int(row[16]),
                upper_response=convert_to_int(row[17]),
            )

            # question 6:
            # How effective is the communication between your family and your childrens' teachers?
            insert_rank_responses_split_by_grammar_upper(
                conn,
                question_id=6,
                respondent_id=respondent_id,
                grammar_response=convert_to_int(row[18]),
                upper_response=convert_to_int(row[19]),
            )

            # question 7:
            # How effective is the communication between your family and the school leadership?
            if len(row[20]) > 0:
                add_to_table(
                    conn,
                    tablename='question_rank',
                    respondent_id=respondent_id,
                    question_id=7,
                    grammar=False,
                    upper=False,
                    response=convert_to_int(row[20]),
                )

            # question 8:
            # How welcoming is the school community?
            insert_rank_responses_split_by_grammar_upper(
                conn,
                question_id=8,
                respondent_id=respondent_id,
                grammar_response=convert_to_int(row[21]),
                upper_response=convert_to_int(row[22]),
            )

            # question 9:
            # Given this year's challenges, what are your thoughts on the following aspects of the school environment?
            open_response_question(
                conn,
                sub_questions_and_responses={
                    'teacher': row[23],
                    'leadership': row[24],
                    'student_services': row[25],
                    'child': row[26],
                },
                respondent_id=respondent_id,
                question_id=9,
            )

            # question 10:
            # What makes GVCA a good choice for you and your family?
            open_response_question(
                conn,
                sub_questions_and_responses={
                    'both': row[27],
                    'grammar': row[28],
                    'upper': row[29],
                },
                respondent_id=respondent_id,
                question_id=10,
            )

            # question 11:
            # Please provide us with examples of how GVCA can better serve you and your family.
            open_response_question(
                conn,
                sub_questions_and_responses={
                    'both': row[30],
                    'grammar': row[31],
                    'upper': row[32],
                },
                respondent_id=respondent_id,
                question_id=11,
            )

            # question 12:
            # What services have your children received at Golden View this school year? Please check all that apply.
            add_services(
                conn,
                respondent_id=respondent_id,
                question_id=12,
                grammar_services={
                    'Qualify for Economic Assistance': row[33],
                    'IEP and related services, including Resource Class, Psychological services, Speech/Lanugage services, and Occupational therapy services':
                        row[35],
                    'Section 504 Plan and related services': row[37],
                    'Gifted and Talented Programming/Advanced Learning Plans': row[39],
                    'English Language Learning Services': row[41],
                    'Reading Intervention': row[43],
                    'Math Intervention': row[45],
                    'Student Behavior/Counseling-type services': row[47],
                    'Other': row[49],
                },
                upper_services={
                    'Qualify for Economic Assistance': row[34],
                    'IEP and related services, including Resource Class, Psychological services, Speech/Lanugage services, and Occupational therapy services':
                        row[36],
                    'Section 504 Plan and related services': row[38],
                    'Gifted and Talented Programming/Advanced Learning Plans': row[40],
                    'English Language Learning Services': row[41],
                    'Reading Intervention': row[44],
                    'Math Intervention': row[46],
                    'Student Behavior/Counseling-type services': row[48],
                    'Other': row[50],
                },
                other_description=row[51],
            )

        conn.execute('END TRANSACTION;')


def add_to_table(conn, tablename: str, **kwargs) -> None:
    """
    Insert values into table.
    Current data model dictates that, at a minimum, all "question" tables should have the following in kwargs:
        * question_id
        * respondent_id

    :param conn: connection to database
    :param tablename: name of the table into which the values will be inserted
    :param kwargs: values are inserted into a column with the same name as the key
    :return: None
    """
    keys = kwargs.keys()
    query = text(f'INSERT INTO {tablename} ({", ".join(list(keys))}) '
                 f'VALUES ({", ".join([":" + k for k in keys])})')
    conn.execute(query, {**{'tablename': tablename}, **kwargs})


def insert_rank_responses_split_by_grammar_upper(conn, question_id: int, grammar_response: int, upper_response:int,
                                                 **kwargs) -> None:
    """
    "Rank" type questions have both a Grammar and an Upper answer, which may or may not be null.
    Separate those onto a different row for each non-null response, and indicate whether it was for Grammar or Upper.

    :param conn: connection to database
    :param question_id: numeric question identifier
    :param grammar_response: text response to the question for Grammar School.  May be null.
    :param upper_response: text response to the question for Upper School.  May be null.
    :param kwargs: expect at least respondent_id; pass it through to add_to_table()
    :return: None
    """
    tablename = 'question_rank'
    if grammar_response:
        add_to_table(conn=conn,
                     tablename=tablename,
                     question_id=question_id,
                     grammar=True,
                     upper=False,
                     response=grammar_response,
                     **kwargs
                     )
    if upper_response:
        add_to_table(conn=conn,
                     tablename=tablename,
                     question_id=question_id,
                     grammar=False,
                     upper=True,
                     response=upper_response,
                     **kwargs
                     )


def open_response_question(conn, sub_questions_and_responses: dict, **kwargs) -> None:
    """
    Open response questions have multiple different text boxes for different responses.
    E.G. What do you think of: Teachers, Leadership, Student Services.
    Separate each sub-question with a non-null response into its own row.

    :param conn: connection to database
    :param sub_questions_and_responses: {'teachers': 'They rock', 'leadership': 'The best ever'}
    :param kwargs: expected at least: question_id, respondent_id
    :return: None
    """
    for sub_question_id, response in sub_questions_and_responses.items():
        if response:
            add_to_table(
                conn,
                tablename='question_open_response',
                sub_question_id=sub_question_id,
                response=response,
                **kwargs
            )


def add_services(conn, grammar_services: dict, upper_services: dict, other_description: str, **kwargs) -> None:
    """
    There's a big long list of different student services with separate checkboxes for grammar and upper school.
    Separate each box which was checked (value is "Upper School" or "Grammar School") onto a separate row.

    :param conn:
    :param grammar_services:
    :param upper_services:
    :param other_description:
    :param kwargs:
    :return:
    """
    for k, v in grammar_services.items():
        if v:
            add_to_table(
                conn,
                tablename='question_services_provided',
                grammar=True,
                upper=False,
                service_name=k,
                **kwargs,
            )
    for k, v in upper_services.items():
        if v:
            add_to_table(
                conn,
                tablename='question_services_provided',
                grammar=False,
                upper=True,
                service_name=k,
                **kwargs,
            )
    if other_description:
        add_to_table(
            conn,
            tablename='question_services_provided',
            grammar=False,
            upper=False,
            service_name=f'OTHER DESCRIPTION: {other_description}',
            **kwargs,
        )


def convert_to_bool(value):
    return True if value == 'Yes' else False if value == 'No' else None


def convert_to_int(value):
    if value.startswith('Extremely') or value.startswith('Strongly'):
        return 4
    if value.startswith('Somewhat'):
        return 2
    if value.startswith('Not'):
        return 1
    if len(value) == 0:
        return None
    return 3

if __name__ == '__main__':
    main()
