from csv import reader as csv_reader
from sqlalchemy import create_engine, text
from pprint import pprint
from dotenv import dotenv_values

env_vars = dotenv_values()
INPUT_FILEPATH = env_vars.get('INPUT_FILEPATH')
DATABASE_SCHEMA = env_vars.get('DATABASE_SCHEMA')
DATABASE_CONNECTION_STRING = env_vars.get('DATABASE_CONNECTION_STRING')


def check_env_vars():
    assert INPUT_FILEPATH, \
        ('The env var INPUT_FILEPATH was not found. '
         'This should be the full filepath to the raw survey results csv.')
    assert DATABASE_SCHEMA, \
        ('The env var DATABASE_SCHEMA was not found. '
         "This should be the schema name into which we're writing the survey results. "
         'Unless you know of a reason otherwise, it should be "sac_survey_2023"')
    assert DATABASE_CONNECTION_STRING, \
        ('The env var DATABASE_CONNECTION_STRING was not found.'
         'This should be the full SQLAlchemy connection string, like: '
         'postgresql://username:password@hostname:port/database')


def inspect_header():
    """
    Run only to check out the file structure and figure out what is in each column.
    Fix known errors and validate.

    :return questions: dict(int: {'question description': str, 'question context': str})
    """
    # get headers, organize columns
    with open(INPUT_FILEPATH, 'r') as f_in:
        raw_data_reader = csv_reader(f_in)
        raw_header = raw_data_reader.__next__()
        raw_sub_header = raw_data_reader.__next__()

    # fill empty columns with the appropriate question
    questions = {}
    current_question = None
    for i, (question, sub_question) in enumerate(zip(raw_header, raw_sub_header)):
        current_question = question if question else current_question  # if it's blank, use the last question that wasn't blank
        questions[i] = {
            'question description': current_question,
            'question context': (sub_question if sub_question else None)
        }

    # pprint(questions)
    print('_' * 200)
    questions = fix_questions(questions)
    validate_fixed_questions(questions)
    return questions


def fix_questions(questions):
    """
    fix typos in questions, and add additional context where needed.

    :param questions: dict(int: {'question description': str, 'question context': str})
    :return questions:
    """
    # Typo with wrong type of apostrophe
    for i in [12, 24, 25, 44, 45, 65, 66, 67, 92, 104, 105, 123]:
        if questions[i]['question description'] == "Given your children’s education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?":
            questions[i]['question description'] = "Given your children's education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?"

    # Typo: childrens' should be children's
    for i in [93, 106, 107, 124]:
        if questions[i]['question description'] == "GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How well does the school culture reflect these virtues?":
            questions[i]['question description'] = "GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How well is the school culture reflected by these virtues?"

    # Typo: childrens' should be children's
    for i in [15, 30, 31, 50, 51, 74, 75, 76, 95, 110, 111, 126]:
        if questions[i]['question description'] == "How effective is the communication between your family and your childrens' teachers?":
            questions[i]['question description'] = "How effective is the communication between your family and your children's teachers?"

    # Fix question context for open response questions
    # These were weird because the page title was the actual question, and the question was the context.
    # It made sense visually to the survey users, so I intentionally pushed the pain to the data processing step instead of the end users
    open_response_questions = [[18, 19, 20, 21], [36, 37, 38, 39, 40, 41], [56, 57, 58, 59, 60, 61], [83, 84, 85, 86, 87, 88, 89, 90], [98, 99, 100, 101], [116, 117, 118, 119, 120, 121], [129, 130, 131, 132], ]
    for question_group in open_response_questions:
        for i_order, i in enumerate(question_group):
            # Use the current description to correct the context
            if questions[i]['question description'] == 'Responses pertinent to Grammar School only':
                questions[i]['question context'] = 'Grammar School'
            elif questions[i]['question description'] == 'Responses pertinent to Middle School only':
                questions[i]['question context'] = 'Middle School'
            elif questions[i]['question description'] == 'Responses pertinent to Upper School only':
                questions[i]['question context'] = 'Upper School'
            elif questions[i]['question description'] == 'Responses generic to the whole school.':
                questions[i]['question context'] = 'Whole School'

            # Knowing that there are only two pages for each group, we can infer the question by splitting the group in half.
            # The first half are "why is GVCA a good choice" and the second half are "where can we improve"
            if i_order < len(question_group) / 2:
                questions[i]['question description'] = 'What makes GVCA a good choice for you and your family?'
            else:
                questions[i]['question description'] = 'Please provide us with examples of how GVCA can better serve you and your family.'

    return questions


def validate_fixed_questions(questions):
    """
    Validate that the questions are what we want them to be after 'fixing' them.

    :param questions: dict(int: {'question description': str, 'question context': str})
    :return: None
    """
    # Test question text and question context
    for indexes, text, text_type in [
        # Question Description checks
        (
                [0],
                "Respondent ID",
                'question description'
        ),
        (
                [1],
                "Collector ID",
                'question description'
        ),
        (
                [2],
                "Start Date",
                'question description'
        ),
        (
                [3],
                "End Date",
                'question description'
        ),
        (
                [9],
                "For your children, choose a method of submission.",
                'question description'
        ),
        (
                [10],
                "This academic year, in which grades are your children?",
                'question description'
        ),
        (
                [11, 22, 23, 42, 43, 62, 63, 64, 91, 102, 103, 122],
                "How satisfied are you with the education that Golden View Classical Academy provided this year?",
                'question description'
        ),
        (
                [12, 24, 25, 44, 45, 65, 66, 67, 92, 104, 105, 123],
                "Given your children's education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?",
                'question description'
        ),
        (
                [13, 26, 27, 46, 47, 68, 69, 70, 93, 106, 107, 124],
                "GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How well is the school culture reflected by these virtues?",
                'question description'
        ),
        (
                [14, 28, 29, 48, 49, 71, 72, 73, 94, 108, 109, 125],
                "How satisfied are you with your children's growth in moral character and civic virtue?",
                'question description'
        ),
        (
                [15, 30, 31, 50, 51, 74, 75, 76, 95, 110, 111, 126],
                "How effective is the communication between your family and your children's teachers?",
                'question description'
        ),
        (
                [16, 32, 33, 52, 53, 77, 78, 79, 96, 112, 113, 127],
                "How effective is the communication between your family and the school leadership?",
                'question description'
        ),
        (
                [17, 34, 35, 54, 55, 80, 81, 82, 97, 114, 115, 128],
                "How welcoming is the school community?",
                'question description'
        ),
        (
                [18, 19, 36, 37, 38, 56, 57, 58, 83, 84, 85, 86, 98, 99, 116, 117, 118, 129, 130],
                "What makes GVCA a good choice for you and your family?",
                'question description'
        ),
        (
                [20, 21, 39, 40, 41, 59, 60, 61, 87, 88, 89, 90, 100, 101, 119, 120, 121, 131, 132],
                "Please provide us with examples of how GVCA can better serve you and your family.",
                'question description'
        ),
        (
                [133],
                "How many years have you had a child at GVCA?  The current academic year counts as 1.",
                'question description'
        ),
        (
                [134],
                "Do you have one or more children on an IEP, 504, ALP, or READ Plan?",
                'question description'
        ),
        (
                [135],
                "Do you consider yourself or your children part of a racial, ethnic, or cultural minority group?",
                'question description'
        ),
        # Question Context checks
        (
                [9, 10, 11, 12, 13, 14, 15, 16, 17, 91, 92, 93, 94, 95, 96, 97, 122, 123, 124, 125, 126, 127, 128, 134, 135],
                "Response",
                'question context'
        ),
        (
                [133],
                "Open-Ended Response",
                'question context'
        ),
        (
                [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 39, 42, 44, 46, 48, 50, 52, 54, 56, 59, 62, 65, 68, 71, 74, 77, 80, 83, 87],
                "Grammar School",
                'question context'
        ),
        (
                [23, 25, 27, 29, 31, 33, 35, 37, 40, 63, 66, 69, 72, 75, 78, 81, 84, 88, 98, 100, 102, 104, 106, 108, 110, 112, 114, 116, 119],
                "Middle School",
                'question context'
        ),
        (
                [43, 45, 47, 49, 51, 53, 55, 57, 60, 64, 67, 70, 73, 76, 79, 82, 85, 89, 103, 105, 107, 109, 111, 113, 115, 117, 120, 129, 131],
                "Upper School",
                'question context'
        ),
        (
                [19, 21, 38, 41, 58, 61, 86, 90, 99, 101, 118, 121, 130, 132],
                "Whole School",
                'question context'
        ),
    ]:
        assert all(text == questions[i][text_type] for i in indexes), (  # compose a useful error message
                f'Expected {text_type} = "{text}"\n\t' + '"\n\t'.join([f'column {i}: "{questions[i]["question description"]}'
                                                                       for i in indexes
                                                                       if text != questions[i]['question description']]) + '"')


def main():
    """
    Insert rows of data into the database.  Tables must already exist.

    :return:
    """
    check_env_vars()
    eng = create_engine(DATABASE_CONNECTION_STRING)
    with open(INPUT_FILEPATH, 'r') as f_in, eng.connect() as conn:
        raw_data_reader = csv_reader(f_in)

        header = raw_data_reader.__next__()
        validate_fixed_questions(header)
        sub_header = raw_data_reader.__next__()

        # database setup
        conn.execute('BEGIN TRANSACTION;')
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}'")
        print(f'Writing to schema: {DATABASE_SCHEMA}')
        # TODO: Remove the TRUNCATE before pushing to prod!
        conn.execute(f'TRUNCATE respondents CASCADE;')

        # each row represents one respondent's answers to each question.
        # Parse each row into separate tables
        for i, row in enumerate(raw_data_reader):
            print(i)
            respondent_id = row[0]
            # Create the respondent, including demographic information
            grammar_rank_questions = [convert_to_int(v) for v in row[12:20:2] + [row[21]] if v]
            upper_rank_questions = [convert_to_int(v) for v in row[13:20:2] + [row[22]] if v]
            all_rank_questions = grammar_rank_questions + upper_rank_questions
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
                # student services questions alternate rows between grammar/upper responses
                grammar_support=any(row[33:51:2]),
                upper_support=any(row[34:51:2]),
                any_support=any(row[34:52]),
                # TODO: Break out IEP and 504s for separate analytics
                minority=convert_to_bool(row[52]),
                grammar_avg=(sum(grammar_rank_questions) / len(grammar_rank_questions)
                             if len(grammar_rank_questions) > 0 else None),
                upper_avg=(sum(upper_rank_questions) / len(upper_rank_questions)
                           if len(upper_rank_questions) > 0 else None),
                overall_avg=(sum(all_rank_questions) / len(all_rank_questions)
                             if len(all_rank_questions) > 0 else None),
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


def insert_rank_responses_split_by_grammar_upper(conn, question_id: int, grammar_response: int, upper_response: int,
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
    # main()
    inspect_header()
