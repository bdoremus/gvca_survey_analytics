-- Apply soft deletes to those who didn't fill out any non-mandatory information
WITH responses_by_respondents AS
         (
             SELECT respondent_id,
                    open_response.respondent_id IS NOT NULL AS has_open_response,
                    rank_response.respondent_id IS NOT NULL AS has_rank_response
             FROM respondents
                      LEFT JOIN
                      (SELECT DISTINCT respondent_id FROM question_open_responses) AS open_response USING (respondent_id)
                      LEFT JOIN
                      (SELECT DISTINCT respondent_id FROM question_rank_responses) AS rank_response USING (respondent_id)
         )
UPDATE respondents
SET soft_delete = TRUE
FROM responses_by_respondents
WHERE responses_by_respondents.respondent_id = respondents.respondent_id
  AND NOT has_open_response
  AND NOT has_rank_response
;


/*
How many users answered the survey?
How many filled out >0 non-mandatory fields?
How many filled out all fields?
 */
SELECT COUNT(*) FILTER ( WHERE NOT soft_delete )                             AS max_families,
       SUM(num_individuals_in_response) FILTER ( WHERE NOT soft_delete ) / 2 AS min_families,
       COUNT(*) FILTER ( WHERE soft_delete )                                 AS num_responses_with_no_contents
FROM respondents
;

-- Calculate the "final" completion rate by averaging the max and min families, then dividing by the number of families
SELECT (386 + 326) / 2. / 418
;
-- 85.2%

-- Look at those who didn't do any ranked choice, but did do open response.  What were their responses?
SELECT respondent_id,
       ROUND(EXTRACT(EPOCH FROM end_datetime - start_datetime) / 60, 1) AS minutes_elapsed,
       question_id,
       question_text,
       grammar,
       middle,
       upper,
       whole_school,
       response
FROM respondents
         LEFT JOIN
     question_open_responses USING (respondent_id)
LEFT JOIN
    questions using(question_id)
WHERE overall_avg IS NULL AND NOT soft_delete
;
-- Only one person filled out the open response but not the rank questions.  Curious, but fine.


-- Look at distribution of open and rank responses by question_id.
SELECT question_id,
       question_type,
       COUNT(DISTINCT COALESCE(question_open_responses.respondent_id, question_rank_responses.respondent_id)),
       question_text
FROM questions
         LEFT JOIN
     question_open_responses USING (question_id)
         LEFT JOIN
     question_rank_responses USING (question_id)
GROUP BY question_id, question_type, question_text
ORDER BY question_id
;

-- Ensure each question type is assigned one and only one level
SELECT *
FROM question_open_responses
WHERE grammar::int + middle::int + upper::int + whole_school::int <> 1
;
SELECT *
FROM question_rank_responses
WHERE grammar::int + middle::int + upper::int <> 1
;

-- Look at distribution of scores
SELECT COUNT(*) FILTER ( WHERE overall_avg >= 3 )                     AS exceeds,
       COUNT(*) FILTER ( WHERE overall_avg >= 2 AND overall_avg < 3 ) AS meets,
       COUNT(*) FILTER ( WHERE overall_avg < 2 )                      AS fails
FROM respondents
;

-- For giggles, take a look at open response for 'fails' group
SELECT respondent_id,
       tenure,
       minority,
       any_support,
       grammar_avg,
       middle_avg,
       upper_avg,
       CASE
           WHEN grammar THEN 'Grammar'
           WHEN middle THEN 'Middle'
           WHEN upper THEN 'Upper'
           WHEN whole_school THEN 'All'
           END AS response_category,
       response
FROM respondents
         JOIN
     question_open_responses USING (respondent_id)
WHERE overall_avg < 2
ORDER BY respondent_id, question_id
;
