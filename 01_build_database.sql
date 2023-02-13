CREATE DATABASE gvca_survey OWNER "ben.doremus";
SET ROLE "ben.doremus";

CREATE SCHEMA sac_survey_2023;
SET SCHEMA 'sac_survey_2023';


CREATE TABLE collectors
(
    collector_id          BIGINT NOT NULL
        CONSTRAINT collectors_pk PRIMARY KEY,
    collector_description TEXT,
    collector_created     TIMESTAMP
);

INSERT INTO collectors(collector_id, collector_description, collector_created)
VALUES ('449194212', 'Testing', '1/3/23 20:24'),
       ('449194285', 'Dr. Garrow''s emails', '1/3/23 20:38'),
       ('449205805', 'Signage', '1/4/23 12:49'),
       ('449205862', 'Newsletter', '1/4/23 12:51')
;


CREATE TABLE respondents
(
    respondent_id               BIGINT NOT NULL
        CONSTRAINT respondents_pk PRIMARY KEY,
    collector_id                BIGINT
        CONSTRAINT respondents_collectors_fk REFERENCES collectors (collector_id),
    start_datetime              TIMESTAMP,
    end_datetime                TIMESTAMP,
    num_individuals_in_response SMALLINT,
    tenure                      INTEGER,
    minority                    BOOLEAN,
    any_support                 BOOLEAN,
    grammar_avg                 FLOAT4,
    middle_avg                  FLOAT4,
    upper_avg                   FLOAT4,
    overall_avg                 FLOAT4,
    soft_delete                 BOOLEAN DEFAULT FALSE
);

CREATE TABLE questions
(
    question_id   SMALLINT
        CONSTRAINT questions_pk PRIMARY KEY,
    question_type TEXT,
    question_text TEXT,
    mandatory     BOOLEAN
);

INSERT INTO questions (question_id, question_type, question_text, mandatory)
VALUES (1, 'multiple choice', 'Choose a method of submission.', TRUE),
       (2, 'multiple choice', 'This academic year, in which grades are your children?', TRUE),
       (3, 'rank', 'How satisfied are you with the education that Golden View Classical Academy provided this year?', FALSE),
       (4, 'rank', 'Given your children''s education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?', FALSE),
       (5, 'rank', 'GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How well is the school culture reflected by these virtues?', FALSE),
       (6, 'rank', 'How satisfied are you with your children''s growth in moral character and civic virtue?', FALSE),
       (7, 'rank', 'How effective is the communication between your family and your children''s teachers?', FALSE),
       (8, 'rank', 'How effective is the communication between your family and the school leadership?', FALSE),
       (9, 'rank', 'How welcoming is the school community?', FALSE),
       (10, 'open response', 'What makes GVCA a good choice for you and your family?', FALSE),
       (11, 'open response', 'Please provide us with examples of how GVCA can better serve you and your family.', FALSE),
       (12, 'numeric', 'How many years have you had a child at GVCA?  The current academic year counts as 1.', FALSE),
       (13, 'boolean', 'Do you have one or more children on an IEP, 504, ALP, or READ Plan?', FALSE),
       (14, 'boolean', 'Do you consider yourself or any of your children part of a racial, ethnic, or cultural minority group?', FALSE)
;


CREATE TABLE question_rank_responses
(
    respondent_id  BIGINT  NOT NULL
        CONSTRAINT question_rank_responses_respondents_fk REFERENCES respondents (respondent_id),
    question_id    INTEGER NOT NULL
        CONSTRAINT question_rank_responses_question_fk REFERENCES questions (question_id),
    grammar        BOOLEAN NOT NULL,
    middle         BOOLEAN NOT NULL,
    upper          BOOLEAN NOT NULL,
    response_value SMALLINT,
    CONSTRAINT question_rank_responses_pk
        PRIMARY KEY (respondent_id, upper, middle, grammar, question_id)
);


CREATE TABLE question_open_responses
(
    respondent_id BIGINT   NOT NULL
        CONSTRAINT question_open_responses_respondents_fk REFERENCES respondents (respondent_id),
    question_id   SMALLINT NOT NULL
        CONSTRAINT question_open_responses_questions_fk REFERENCES questions (question_id),
    grammar       BOOLEAN  NOT NULL,
    middle        BOOLEAN  NOT NULL,
    upper         BOOLEAN  NOT NULL,
    whole_school  BOOLEAN  NOT NULL,
    response      TEXT,
    CONSTRAINT question_open_responses_pk
        PRIMARY KEY (respondent_id, question_id, grammar, middle, upper, whole_school)
);


CREATE TABLE question_response_mapping
(
    question_id    SMALLINT
        CONSTRAINT question_response_mapping_question_fk REFERENCES questions (question_id),
    response_value SMALLINT,
    response_text  TEXT,
    CONSTRAINT question_response_mapping_pk
        PRIMARY KEY (question_id, response_value)
);

INSERT INTO question_response_mapping (question_id, response_value, response_text)
VALUES (1, 1, 'Each parent or guardian will submit a separate survey, and we will submit two surveys.'),
       (1, 2, 'All parents and guardians will coordinate responses, and we will submit only one survey.'),

       (3, 4, 'Extremely Satisfied'),
       (3, 3, 'Satisfied'),
       (3, 2, 'Somewhat Satisfied'),
       (3, 1, 'Not Satisfied'),

       (4, 4, 'Extremely Satisfied'),
       (4, 3, 'Satisfied'),
       (4, 2, 'Somewhat Satisfied'),
       (4, 1, 'Not Satisfied'),

       (5, 4, 'Strongly Reflected'),
       (5, 3, 'Reflected'),
       (5, 2, 'Somewhat Reflected'),
       (5, 1, 'Not Reflected'),

       (6, 4, 'Extremely Satisfied'),
       (6, 3, 'Satisfied'),
       (6, 2, 'Somewhat Satisfied'),
       (6, 1, 'Not Satisfied'),

       (7, 4, 'Extremely Effective'),
       (7, 3, 'Effective'),
       (7, 2, 'Somewhat Effective'),
       (7, 1, 'Not Effective'),

       (8, 4, 'Extremely Effective'),
       (8, 3, 'Effective'),
       (8, 2, 'Somewhat Effective'),
       (8, 1, 'Not Effective'),

       (9, 4, 'Extremely Welcoming'),
       (9, 3, 'Welcoming'),
       (9, 2, 'Somewhat Welcoming'),
       (9, 1, 'Not Welcoming')
;
