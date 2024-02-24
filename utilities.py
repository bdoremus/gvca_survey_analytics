from dotenv import dotenv_values


def load_env_vars():
    env_vars = dotenv_values()

    input_filepath = env_vars.get('INPUT_FILEPATH')
    database_schema = env_vars.get('DATABASE_SCHEMA')
    database_connection_string = env_vars.get('DATABASE_CONNECTION_STRING')

    assert input_filepath, \
        ('The env var INPUT_FILEPATH was not found. '
         'This should be the full filepath to the raw survey results csv.')
    assert database_schema, \
        ('The env var DATABASE_SCHEMA was not found. '
         "This should be the schema name into which we're writing the survey results. "
         'Unless you know of a reason otherwise, it should be "sac_survey_202#"')
    assert database_connection_string, \
        ('The env var DATABASE_CONNECTION_STRING was not found.'
         'This should be the full SQLAlchemy connection string, like: '
         'postgresql://username:password@hostname:port/database')

    return input_filepath, database_schema, database_connection_string
