CREATE SCHEMA IF NOT EXISTS sac_survey_2022;
SET SCHEMA 'sac_survey_2022';

create table respondents
(
    respondent_id       bigint not null
        constraint respondents_pk
            primary key,
    collector_id        bigint,
    start_datetime      timestamp,
    end_datetime        timestamp,
    tenure              integer,
    minority            boolean,
    grammar_conferences boolean,
    upper_conferences   boolean,
    grammar_support     boolean,
    upper_support       boolean,
    any_support         boolean,
    grammar_avg         float4,
    upper_avg           float4,
    overall_avg         float4
);

create table question_rank
(
    respondent_id bigint            not null
            references respondents(respondent_id),
    question_id   integer default 2 not null,
    grammar       boolean           not null,
    upper         boolean           not null,
    response      smallint,
    constraint question_rank_pk
        primary key (respondent_id, upper, grammar, question_id)
);

create table question_open_response
(
    respondent_id   bigint   not null
            references respondents(respondent_id),
    question_id     smallint not null,
    sub_question_id text     not null,
    response        text,
    constraint question_open_response_pk
        primary key (respondent_id, question_id, sub_question_id)
);

create table question_services_provided
(
    respondent_id bigint  not null
            references respondents(respondent_id),
    question_id   integer not null,
    grammar       boolean not null,
    upper         boolean not null,
    service_name  text    not null,
    constraint question_services_provided_pk
        primary key (respondent_id, question_id, grammar, upper, service_name)
);

create table question
(
    question_id   smallint primary key,
    question_text text
);

INSERT INTO question (question_id, question_text)
VALUES (1, 'How many years have you had a child at Golden View Classical Academy?  The current academic year counts as 1.'),
       (2, 'Did you or one of your children attend conferences this year?'),
       (3, 'Given your children''s education level at the beginning of of the year, how satisfied are you with their intellectual growth this year?'),
       (4, 'How satisfied are you with the education that your children have received at Golden View Classical Academy this year?'),
       (5, 'GVCA emphasizes 7 core virtues: Courage, Moderation, Justice, Responsibility, Prudence, Friendship, and Wonder. How strongly is the school culture influenced by those virtues?'),
       (6, 'How effective is the communication between your family and your childrens'' teachers?'),
       (7, 'How effective is the communication between your family and the school leadership?'),
       (8, 'How welcoming is the school community?'),
       (9, 'Given this year''s challenges, what are your thoughts on the following aspects of the school environment?'),
       (10, 'What makes GVCA a good choice for you and your family?'),
       (11, 'Please provide us with examples of how GVCA can better serve you and your family.'),
       (12, 'What services have your children received at Golden View this school year? Please check all that apply.'),
       (13, 'Do you consider yourself or your children part of a racial, ethnic, or cultural minority group?')
;

create table response_definition
(
    question_id          smallint references question (question_id),
    response             smallint,
    response_description text,
    constraint response_definition_pk
        primary key (question_id, response)
);

INSERT INTO response_definition (question_id, response, response_description)
VALUES (3, 4, 'Extremely Satisfied'),
       (3, 3, 'Satisfied'),
       (3, 2, 'Somewhat Satisfied'),
       (3, 1, 'Not Satisfied'),

       (4, 4, 'Extremely Satisfied'),
       (4, 3, 'Satisfied'),
       (4, 2, 'Somewhat Satisfied'),
       (4, 1, 'Not Satisfied'),

       (5, 4, 'Strongly Influenced'),
       (5, 3, 'Influenced'),
       (5, 2, 'Somewhat Influenced'),
       (5, 1, 'Not Influenced'),

       (6, 4, 'Extremely Effective'),
       (6, 3, 'Effective'),
       (6, 2, 'Somewhat Effective'),
       (6, 1, 'Not Effective'),

       (7, 4, 'Extremely Effective'),
       (7, 3, 'Effective'),
       (7, 2, 'Somewhat Effective'),
       (7, 1, 'Not Effective'),

       (8, 4, 'Extremely Welcoming'),
       (8, 3, 'Welcoming'),
       (8, 2, 'Somewhat Welcoming'),
       (8, 1, 'Not Welcoming')
;

CREATE TABLE open_response_categories
(
    question_id     smallint
        references question (question_id),
    sub_question_id text,
    respondent_id   bigint
        references respondents (respondent_id),
    grammar         bool,
    upper           bool,
    category        text,
    sentiment       text
)
;