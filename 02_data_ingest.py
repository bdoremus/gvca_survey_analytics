# TODO refactor this whole thing to be config based.  Given text[], standardized text output, indexes, etc.
#      One major problem is that questions are defined separately in the database and the functions below.  If the text doesn't match exactly, there are silent errors.

import logging
from csv import reader as csv_reader
from sqlalchemy import create_engine, text
from dotenv import dotenv_values
from pprint import pprint

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


def inspect_header(conn):
    """
    Run only to check out the file structure and figure out what is in each column.
    Fix known errors and validate.
    Return a list with info about each column in the survey data, aka "header information."

    :return questions: dict(int: {'question description': str, 'question context': str, 'question type': str})
    """
    # get headers, organize columns
    with open(INPUT_FILEPATH, 'r') as f_in:
        raw_data_reader = csv_reader(f_in)
        raw_header = raw_data_reader.__next__()
        raw_sub_header = raw_data_reader.__next__()

    # fill empty columns with the appropriate question
    raw_questions = {}
    current_question = None
    for i, (question, sub_question) in enumerate(zip(raw_header, raw_sub_header)):
        current_question = question if question else current_question  # if it's blank, use the last question that wasn't blank

        # save results for this column of the survey
        raw_questions[i] = {
            'question description': current_question,
            'question context': (sub_question if sub_question else None),
        }

    logging.info(raw_questions)
    raw_questions = fix_questions(conn, raw_questions)
    validate_fixed_questions(raw_questions)
    return raw_questions


def fix_questions(conn, questions):
    """
    fix typos in questions, and add additional context where needed.

    :param conn: sqlalchemy connection
    :param questions: dict(int: {'question description': str, 'question context': str})
    :return questions:
    """
    # Typo with wrong type of apostrophe
    for i in [12, 24, 25, 44, 45, 65, 66, 67, 92, 104, 105, 123]:
        if questions[i]['question description'] == "Given your children’s education level at the beginning of the year, how satisfied are you with their intellectual growth this year?":
            questions[i]['question description'] = "Given your children's education level at the beginning of the year, how satisfied are you with their intellectual growth this year?"

    # # Typo: childrens' should be children's
    # for i in [93, 106, 107, 124]:
    #     if questions[i]['question description'] == "GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How well does the school culture reflect these virtues?":
    #         questions[i]['question description'] = "GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How well is the school culture reflected by these virtues?"

    # # Typo: childrens' should be children's
    # for i in [15, 30, 31, 50, 51, 74, 75, 76, 95, 110, 111, 126]:
    #     if questions[i]['question description'] == "How effective is the communication between your family and your childrens' teachers?":
    #         questions[i]['question description'] = "How effective is the communication between your family and your children's teachers?"

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
            elif questions[i]['question description'] == 'Responses pertinent to High School only':
                questions[i]['question context'] = 'High School'
            elif questions[i]['question description'] == 'Responses generic to the whole school.':
                questions[i]['question context'] = 'Whole School'

            # Knowing that there are only two pages for each group, we can infer the question by splitting the group in half.
            # The first half are "why is GVCA a good choice" and the second half are "where can we improve"
            if i_order < len(question_group) / 2:
                questions[i]['question description'] = 'What makes GVCA a good choice for you and your family?'
            else:
                questions[i]['question description'] = 'Please provide us with examples of how GVCA can better serve you and your family.'

    # Fix question context where it wasn't a matrix question because there was only one grade level involved
    for i in range(11, 18):
        if questions[i]['question context'] == "Response":
            questions[i]['question context'] = "Grammar School"
    for i in range(91, 98):
        if questions[i]['question context'] == "Response":
            questions[i]['question context'] = "Middle School"
    for i in range(122, 129):
        if questions[i]['question context'] == "Response":
            questions[i]['question context'] = "High School"

    # Add additional information to each header
    question_info_from_db = conn.execute(f"""SELECT question_id, question_type, question_text FROM {DATABASE_SCHEMA}.questions;""").fetchall()

    # Add in identifiers and types from the database
    for i, q in questions.items():
        results = [(question_type, question_id)
                   for question_id, question_type, question_text
                   in question_info_from_db
                   if question_text == q['question description']]
        if len(results) == 0:
            continue
        elif len(results) > 1:
            raise IndexError

        question_type, question_id = results[0]
        q['question type'] = question_type
        q['question_id'] = question_id

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
                "Choose a method of submission.",
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
                "Given your children's education level at the beginning of the year, how satisfied are you with their intellectual growth this year?",
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
                "Do you consider yourself or any of your children part of a racial, ethnic, or cultural minority group?",
                'question description'
        ),
        # Question Context checks
        (
                [9, 10, 134, 135],
                "Response",
                'question context'
        ),
        (
                [133],
                "Open-Ended Response",
                'question context'
        ),
        (
                [*range(11, 18), *range(18, 38, 2), 39, 42, 44, 46, 48, 50, 52, 54, 56, 59, 62, 65, 68, 71, 74, 77, 80, 83, 87],
                "Grammar School",
                'question context'
        ),
        (
                [23, 25, 27, 29, 31, 33, 35, 37, 40, 63, 66, 69, 72, 75, 78, 81, 84, 88, *range(91, 98), 98, 100, 102, 104, 106, 108, 110, 112, 114, 116, 119],
                "Middle School",
                'question context'
        ),
        (
                [43, 45, 47, 49, 51, 53, 55, 57, 60, 64, 67, 70, 73, 76, 79, 82, 85, 89, 103, 105, 107, 109, 111, 113, 115, 117, 120, *range(122, 129), 129, 131],
                "High School",
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


def get_question_response(questions: dict, question_description: str, response_row: dict) -> int:
    """
    Iterate through all the columns which match the description.  Return the first of those columns which has been answered (should only be one).

    :param questions: dictionary of all questions and their indexes
    :param question_description: the text to match
    :param response_row: the row of responses we're searching through for a response to the question
    :return:
    """
    for i in [question_index for question_index, question_values in questions.items() if question_values['question description'] == question_description]:
        if response_row[i]:
            return convert_to_int(response_row[i])


def main():
    """
    Insert rows of data into the database.  Tables must already exist.

    :return:
    """
    check_env_vars()
    eng = create_engine(DATABASE_CONNECTION_STRING)
    with open(INPUT_FILEPATH, 'r') as f_in, eng.connect() as conn:
        raw_data_reader = csv_reader(f_in)

        raw_questions = inspect_header(conn)
        # since the questions have been fixed, skip reading those here
        header = raw_data_reader.__next__()
        sub_header = raw_data_reader.__next__()

        # database setup
        conn.execute('BEGIN TRANSACTION;')
        conn.execute(f"SET SCHEMA '{DATABASE_SCHEMA}';")
        logging.info(f'Writing to schema: {DATABASE_SCHEMA}')

        # each row represents one respondent's answers to every question.
        # Parse each row into separate tables
        for i, row in enumerate(raw_data_reader):
            logging.info(f'Processing row {i}')

            # Includes questions 1, 2, 12, 13, 14, and meta information
            populate_respondents(conn, raw_questions, row)

            # iterate through all questions.  Check the question type, then insert data into the correct place
            for question_id, question_type, question_text in conn.execute(f"""SELECT question_id, question_type, question_text FROM {DATABASE_SCHEMA}.questions;""").all():
                logging.info(f'Processing question {question_id} for row {i}')
                if question_type == 'rank':
                    populate_rank_response(conn, question_id, question_text, raw_questions, row)
                if question_type == 'open response':
                    populate_open_response(conn, question_id, question_text, raw_questions, row)

        conn.execute('END TRANSACTION;')


def populate_respondents(conn, questions, row):
    # Create the respondent, including demographic information
    grammar_rank_questions = [convert_to_int(row[i]) for i, q in questions.items() if q['question context'] == 'Grammar School' and row[i]]
    middle_rank_questions = [convert_to_int(row[i]) for i, q in questions.items() if q['question context'] == 'Middle School' and row[i]]
    high_rank_questions = [convert_to_int(row[i]) for i, q in questions.items() if q['question context'] == 'High School' and row[i]]
    all_rank_questions = grammar_rank_questions + middle_rank_questions + high_rank_questions
    add_to_table(
        conn,
        tablename='respondents',
        respondent_id=row[0],
        collector_id=row[1],
        start_datetime=row[2],
        end_datetime=row[3],
        num_individuals_in_response=(1 if row[9] == 'Each parent or guardian will submit a separate survey, and we will submit two surveys.' else
                                     2 if row[9] == 'All parents and guardians will coordinate responses, and we will submit only one survey.' else
                                     None),
        tenure=int(row[133]) if row[133] else None,
        minority=convert_to_bool(row[135]),
        any_support=convert_to_bool(row[134]),
        grammar_avg=(sum(grammar_rank_questions) / len(grammar_rank_questions)
                     if len(grammar_rank_questions) > 0 else None),
        middle_avg=(sum(middle_rank_questions) / len(middle_rank_questions)
                    if len(middle_rank_questions) > 0 else None),
        high_avg=(sum(high_rank_questions) / len(high_rank_questions)
                   if len(high_rank_questions) > 0 else None),
        overall_avg=(sum(all_rank_questions) / len(all_rank_questions)
                     if len(all_rank_questions) > 0 else None),
    )


def populate_rank_response(conn, question_id, question_text, raw_questions, row):
    # Iterate through the columns of responses.  If it matches the question and has a response, insert it into the db
    for question, response in zip(raw_questions.values(), row):
        logging.debug(f'question_id: {question_id}')
        logging.debug(f'question_text: {question_text}')
        if question['question description'] == question_text and response:
            logging.debug(f'{question["question context"]} response: {response}')
            add_to_table(
                conn,
                tablename='question_rank_responses',
                respondent_id=row[0],
                question_id=question_id,
                grammar=question['question context'] == 'Grammar School',
                middle=question['question context'] == 'Middle School',
                high=question['question context'] == 'High School',
                response_value=convert_to_int(response)
            )

            
def populate_open_response(conn, question_id, question_text, raw_questions, row):
    # Iterate through the columns of responses.  If it matches the question and has a response, insert it into the db
    for question, response in zip(raw_questions.values(), row):
        logging.debug(f'question_id: {question_id}')
        logging.debug(f'question_text: {question_text}')
        if question['question description'] == question_text and response:
            logging.debug(f'{question["question context"]} response: {response}')
            add_to_table(
                conn,
                tablename='question_open_responses',
                respondent_id=row[0],
                question_id=question_id,
                grammar=question['question context'] == 'Grammar School',
                middle=question['question context'] == 'Middle School',
                high=question['question context'] == 'High School',
                whole_school=question['question context'] == 'Whole School',
                response=response
            )


def add_to_table(conn, tablename: str, **kwargs) -> None:
    """
    Insert values into table.
    Current data model dictates that, at a minimum, all "question_*_response" tables should have the following in kwargs:
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
