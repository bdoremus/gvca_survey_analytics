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
    any_support         boolean
);

alter table respondents
    owner to bendoremus;

create table question_rank
(
    respondent_id bigint            not null
        constraint question2_respondents_respondent_id_fk
            references respondents,
    question_id   integer default 2 not null,
    grammar       boolean           not null,
    upper         boolean           not null,
    response      smallint,
    constraint question2_pk
        primary key (respondent_id, upper, grammar, question_id)
);

alter table question_rank
    owner to bendoremus;

create table question_open_response
(
    respondent_id   bigint   not null
        constraint open_response_question_respondents_respondent_id_fk
            references respondents,
    question_id     smallint not null,
    sub_question_id text     not null,
    response        text,
    constraint open_response_question_pk
        primary key (respondent_id, question_id, sub_question_id)
);

alter table question_open_response
    owner to bendoremus;

create table question_services_provided
(
    respondent_id bigint  not null
        constraint services_provided_respondents_respondent_id_fk
            references respondents,
    question_id   integer not null,
    grammar       boolean not null,
    upper         boolean not null,
    service_name  text    not null,
    constraint services_provided_pk
        primary key (respondent_id, question_id, grammar, upper, service_name)
);

alter table question_services_provided
    owner to bendoremus;

create table rank_definition
(
    question_id      smallint,
    rank             smallint,
    rank_description text
);

alter table rank_definition
    owner to bendoremus;

INSERT INTO rank_definition (question_id, rank, rank_description)
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