/*
How many users answered the survey?
How many filled out >0 non-mandatory fields?
How many filled out all fields?
 */
WITH responses_by_respondent AS
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
SELECT COUNT(*)                                                                                      AS max_families,
       COUNT(*) FILTER ( WHERE has_open_response OR has_rank_response )                              AS max_families_any_responses,
       COUNT(*) FILTER ( WHERE has_open_response AND has_rank_response )                             AS max_families_fully_completed_responses,
       SUM(num_individuals_in_response) / 2                                                          AS min_families,
       SUM(num_individuals_in_response) FILTER ( WHERE has_open_response OR has_rank_response ) / 2  AS min_families_any_responses,
       SUM(num_individuals_in_response) FILTER ( WHERE has_open_response AND has_rank_response ) / 2 AS min_families_fully_completed_responses
FROM respondents
         JOIN
     responses_by_respondent USING (respondent_id)
;

-- Calculate the "final" completion rate by averaging the max and min families, then dividing by the number of families
SELECT (386 + 326) / 2. / 418
;
-- 85.2%

-- Look at those who didn't do any ranked choice, but did do open response.  What were their responses?
SELECT respondent_id,
       respondent_id,
       collector_id,
       start_datetime,
       end_datetime,
       num_individuals_in_response,
       tenure,
       minority,
       ROUND(EXTRACT(EPOCH FROM end_datetime - start_datetime) / 60, 1) AS minutes_elapsed,
       question_id,
       grammar,
       middle,
       upper,
       whole_school,
       response
FROM respondents
         LEFT JOIN
     question_open_responses USING (respondent_id)
WHERE overall_avg IS NULL
;
-- Only one person filled out the open response but not the rank questions.  Curious, but fine.


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
