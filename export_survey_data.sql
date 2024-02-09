--respondents
SELECT respondent_id,
       start_datetime,
       end_datetime,
       num_individuals_in_response,
       tenure,
       minority,
       any_support,
       grammar_avg,
       middle_avg,
       high_avg,
       overall_avg,
       collector_id,
       collector_description
FROM respondents
         LEFT JOIN
     collectors USING (collector_id)
WHERE NOT soft_delete
ORDER BY respondent_id
;

-- questions
SELECT *
FROM questions
;

-- responses_rank
WITH all_respondent_questions AS
         (
             SELECT respondent_id,
                    question_id,
                    question_text
             FROM respondents
                      CROSS JOIN
                  questions
             WHERE question_type = 'rank'
               AND NOT soft_delete
         )
SELECT respondent_id,
       question_id,
       question_text,
       CASE
           WHEN grammar THEN 'Grammar'
           WHEN middle THEN 'Middle'
           WHEN high THEN 'High'
           END AS grade_level,
       response_value,
       response_text
FROM all_respondent_questions
         LEFT JOIN
     question_rank_responses USING (respondent_id, question_id)
         LEFT JOIN
     question_response_mapping USING (question_id, response_value)
ORDER BY respondent_id, question_id, grammar DESC, middle DESC, high DESC
;

-- response_open
WITH all_respondent_questions AS
         (
             SELECT respondent_id,
                    question_id,
                    question_text
             FROM respondents
                      CROSS JOIN
                  questions
             WHERE question_type = 'open response'
               AND NOT soft_delete
         )
SELECT respondent_id,
       question_id,
       question_text,
       CASE
           WHEN grammar THEN 'Grammar'
           WHEN middle THEN 'Middle'
           WHEN high THEN 'High'
           WHEN whole_school THEN 'Whole School'
           END AS grade_level,
       response
FROM all_respondent_questions
         LEFT JOIN
     question_open_responses USING (respondent_id, question_id)
ORDER BY respondent_id, question_id, grammar DESC, middle DESC, high DESC, whole_school DESC
;


-- flattened respondent_rank_questions
WITH duplicated_respondents AS
         (
             SELECT respondent_id,
                    tenure = 1              AS new_family,
                    minority,
                    any_support,
                    grammar_avg IS NOT NULL AS grammar_respondent,
                    middle_avg IS NOT NULL  AS middle_respondent,
                    high_avg IS NOT NULL   AS high_respondent,
                    overall_avg             AS avg_score,
                    soft_delete
             FROM respondents
             WHERE NOT soft_delete

             UNION ALL

             -- Get a second rows for any respondent which represented two people
             SELECT respondent_id,
                    tenure = 1              AS new_family,
                    minority,
                    any_support,
                    grammar_avg IS NOT NULL AS grammar_respondent,
                    middle_avg IS NOT NULL  AS middle_respondent,
                    high_avg IS NOT NULL   AS high_respondent,
                    overall_avg             AS avg_score,
                    soft_delete
             FROM respondents
             WHERE NOT soft_delete
               AND num_individuals_in_response = 2
         ),
     all_respondent_questions AS
         (
             SELECT respondent_id,
                    question_id,
                    question_text
             FROM respondents
                      CROSS JOIN
                  questions
             WHERE question_type = 'rank'
               AND NOT soft_delete
         ),
     rank_questions AS
         (
             SELECT respondent_id,
                    question_id,
                    question_text,
                    CASE
                        WHEN grammar THEN 'Grammar'
                        WHEN middle THEN 'Middle'
                        WHEN high THEN 'High'
                        END AS grade_level_for_response,
                    response_value,
                    response_text
             FROM all_respondent_questions
                      LEFT JOIN
                  question_rank_responses USING (respondent_id, question_id)
                      LEFT JOIN
                  question_response_mapping USING (question_id, response_value)
         )
SELECT -- respondents
       respondent_id,
       new_family,
       minority,
       any_support,
       grammar_respondent,
       middle_respondent,
       high_respondent,
       avg_score,

       -- questions
       question_id,
       question_text,
       grade_level_for_response,
       response_value,
       response_text
FROM rank_questions
         JOIN
     duplicated_respondents USING (respondent_id)
ORDER BY respondent_id, question_id, grade_level_for_response
;


-- flattened respondent_rank_questions for 2022 only
WITH respondents_expanded AS
         (
             SELECT respondent_id,
                    tenure = 1              AS new_family,
                    minority,
                    any_support,
                    grammar_avg IS NOT NULL AS grammar_respondent,
                    NULL                    AS middle_respondent,
                    upper_avg IS NOT NULL   AS upper_respondent,
                    overall_avg             AS avg_score
             FROM gvca_survey.sac_survey_2022.respondents
         ),
     all_respondent_questions AS
         (
             SELECT respondent_id,
                    question_id,
                    question_text
             FROM respondents_expanded
                      CROSS JOIN
                  sac_survey_2022.question
             WHERE question_id < 9
               AND question_id > 2
         ),
     rank_questions AS
         (
             SELECT respondent_id,
                    question_id,
                    question_text,
                    CASE
                        WHEN grammar THEN 'Grammar'
                        WHEN upper THEN 'Upper'
                        WHEN NOT grammar AND NOT upper AND question_id = 7 THEN '"Grade level" not used for this question'
                        END AS grade_level_for_response,
                    response
             FROM all_respondent_questions
                      LEFT JOIN
                  sac_survey_2022.question_rank USING (respondent_id, question_id)
         )
SELECT -- respondents
       respondent_id,
       new_family,
       minority,
       any_support,
       grammar_respondent,
       middle_respondent,
       upper_respondent,
       avg_score,

       -- questions
       question_id,
       question_text,
       grade_level_for_response,
       response
FROM rank_questions
         JOIN
     respondents_expanded USING (respondent_id)
ORDER BY respondent_id, question_id, grade_level_for_response
;
