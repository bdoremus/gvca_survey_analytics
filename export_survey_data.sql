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
       upper_avg,
       overall_avg,
       collector_id,
       collector_description
FROM respondents
LEFT JOIN
    collectors USING(collector_id)
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
       grammar,
       middle,
       upper,
       response_value,
       response_text
FROM all_respondent_questions
         LEFT JOIN
     question_rank_responses USING (respondent_id, question_id)
         LEFT JOIN
     question_response_mapping USING (question_id, response_value)
ORDER BY respondent_id, question_id, grammar DESC, middle DESC, upper DESC
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
       grammar,
       middle,
       upper,
       whole_school,
       response
FROM all_respondent_questions
         LEFT JOIN
     question_open_responses USING (respondent_id, question_id)
ORDER BY respondent_id, question_id, grammar DESC, middle DESC, upper DESC, whole_school DESC
;
