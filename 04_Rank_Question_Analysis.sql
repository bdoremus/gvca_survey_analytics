/*
 Summary of ranked questions
 */
WITH question_totals AS
         (
             SELECT question_id,
                    COUNT(0)::NUMERIC                                  AS question_total,
                    COUNT(0) FILTER ( WHERE grammar )::NUMERIC         AS grammar_total,
                    COUNT(0) FILTER ( WHERE high )::NUMERIC            AS high_total,
                    COUNT(0) FILTER ( WHERE minority )::NUMERIC        AS minority_total,
                    COUNT(0) FILTER ( WHERE NOT minority )::NUMERIC    AS not_minority_total,
                    COUNT(0) FILTER ( WHERE any_support )::NUMERIC     AS recieves_support_total,
                    COUNT(0) FILTER ( WHERE NOT any_support )::NUMERIC AS no_support_total,
                    COUNT(0) FILTER ( WHERE tenure = 1)::NUMERIC       AS first_year_family_total,
                    COUNT(0) FILTER ( WHERE tenure > 1)::NUMERIC       AS not_first_year_family_total,
                    COUNT(0) FILTER ( WHERE tenure <= 3)::NUMERIC      AS third_or_less_year_family_total,
                    COUNT(0) FILTER ( WHERE tenure > 3)::NUMERIC       AS more_than_third_year_family_total
             FROM question_rank_responses
                      LEFT JOIN
                  respondents USING (respondent_id)
             GROUP BY question_id
         ),
     response_totals AS
         (
             SELECT question_id,
                    response_value,
                    COUNT(0)                                      AS total,
                    COUNT(0) FILTER ( WHERE grammar )             AS grammar,
                    COUNT(0) FILTER ( WHERE high )                AS high,
                    COUNT(0) FILTER ( WHERE minority )            AS minority,
                    COUNT(0) FILTER ( WHERE NOT minority )        AS not_minority,
                    COUNT(0) FILTER ( WHERE any_support )         AS recieves_support,
                    COUNT(0) FILTER ( WHERE NOT any_support )     AS no_support,
                    COUNT(0) FILTER ( WHERE tenure = 1)::NUMERIC  AS first_year_family,
                    COUNT(0) FILTER ( WHERE tenure > 1)::NUMERIC  AS not_first_year_family,
                    COUNT(0) FILTER ( WHERE tenure <= 3)::NUMERIC AS third_year_family,
                    COUNT(0) FILTER ( WHERE tenure > 3)::NUMERIC  AS not_third_year_family
             FROM question_rank_responses
                      LEFT JOIN
                  respondents USING (respondent_id)
             GROUP BY question_id, response_value
         )
SELECT question_id,
       question_text,
       response_value,
       response_text,
       NULLIF(total, 0)                                                     AS total,
       total / NULLIF(question_total, 0)                                    AS total_pct,
       NULLIF(grammar, 0)                                                   AS grammar,
       grammar / NULLIF(grammar_total, 0)                                   AS grammar_pct,
       NULLIF(high, 0)                                                      AS high,
       high / NULLIF(high_total, 0)                                         AS high_pct,
       NULLIF(minority, 0)                                                  AS minority,
       minority / NULLIF(minority_total, 0)                                 AS minority_pct,
       NULLIF(not_minority, 0)                                              AS not_minority,
       not_minority / NULLIF(not_minority_total, 0)                         AS not_minority_pct,
       NULLIF(recieves_support, 0)                                          AS recieves_support,
       recieves_support / NULLIF(recieves_support_total, 0)                 AS recieves_support_pct,
       NULLIF(no_support, 0)                                                AS no_support,
       no_support / NULLIF(no_support_total, 0)                             AS no_support_pct,
       NULLIF(first_year_family, 0)                                         AS first_year_family,
       first_year_family / NULLIF(first_year_family_total, 0)               AS first_year_family_pct,
       NULLIF(not_first_year_family, 0)                                     AS not_first_year_family,
       not_first_year_family / NULLIF(not_first_year_family_total, 0)       AS not_first_year_family_pct,
       NULLIF(third_year_family, 0)                                         AS third_year_family,
       third_year_family / NULLIF(third_or_less_year_family_total, 0)       AS third_or_less_year_family_pct,
       NULLIF(not_third_year_family, 0)                                     AS not_third_year_family,
       not_third_year_family / NULLIF(more_than_third_year_family_total, 0) AS more_than_third_year_family_pct
FROM response_totals
         INNER JOIN
     question_totals USING (question_id)
         LEFT JOIN
     questions USING (question_id)
         LEFT JOIN
     question_response_mapping USING (question_id, response_value)
ORDER BY question_id, response_value
;


-- What % of responses are Satisfied or Very Satisfied (weighted by # individuals)?
SELECT ROUND(100. * SUM(family.num_individuals_in_response) FILTER ( WHERE q.response_value >= 3 ) /
             SUM(family.num_individuals_in_response), 1)                           AS overall,

       ROUND(100. * SUM(family.num_individuals_in_response) FILTER ( WHERE q.response_value >= 3 AND q.grammar) /
             SUM(family.num_individuals_in_response) FILTER ( WHERE q.grammar), 1) AS grammar,

       ROUND(100. * SUM(family.num_individuals_in_response) FILTER ( WHERE q.response_value >= 3 AND q.middle) /
             SUM(family.num_individuals_in_response) FILTER ( WHERE q.middle ), 1) AS middle,

       ROUND(100. * SUM(family.num_individuals_in_response) FILTER ( WHERE q.response_value >= 3 AND q.high) /
             SUM(family.num_individuals_in_response) FILTER ( WHERE q.high ), 1)   AS high,

       ROUND(100. * (
                       SUM(family.num_individuals_in_response) FILTER ( WHERE q.response_value >= 3 AND q.middle) +
                       SUM(family.num_individuals_in_response) FILTER ( WHERE q.response_value >= 3 AND q.high)
           ) / (
                             SUM(family.num_individuals_in_response) FILTER ( WHERE q.middle) +
                             SUM(family.num_individuals_in_response) FILTER ( WHERE q.high)
                 ), 1)                                                             AS upper
FROM respondents AS family
         JOIN
     question_rank_responses AS q USING (respondent_id)
;

-- What % of parents/guardians had an average score of 3 or above, broken out by grammar/middle/high.
WITH respondents_grade_level_combined AS
         (
             SELECT num_individuals_in_response,
                    grammar_avg,
                    middle_avg,
                    high_avg,
                    (middle_avg + high_avg) / 2 AS upper_avg,
                    overall_avg
             FROM respondents
             WHERE NOT soft_delete
               AND overall_avg IS NOT NULL
         ),
     satisfaction_per_group AS
         (
             SELECT SUM(num_individuals_in_response) FILTER ( WHERE grammar_avg >= 3)::NUMERIC
                        / SUM(num_individuals_in_response) FILTER ( WHERE grammar_avg IS NOT NULL) AS pct_grammar_gte_3,

                    SUM(num_individuals_in_response) FILTER ( WHERE middle_avg >= 3)::NUMERIC
                        /
                    SUM(num_individuals_in_response) FILTER ( WHERE middle_avg IS NOT NULL)        AS pct_middle_gte_3,

                    SUM(num_individuals_in_response) FILTER ( WHERE high_avg >= 3)::NUMERIC
                        /
                    SUM(num_individuals_in_response) FILTER ( WHERE high_avg IS NOT NULL)          AS pct_high_gte_3,

                    SUM(num_individuals_in_response) FILTER ( WHERE upper_avg >= 3)::NUMERIC
                        / SUM(num_individuals_in_response)
                          FILTER ( WHERE upper_avg IS NOT NULL)                                    AS pct_upper_gte_3,

                    SUM(num_individuals_in_response) FILTER ( WHERE overall_avg >= 3)::NUMERIC
                        / SUM(num_individuals_in_response) FILTER ( WHERE overall_avg IS NOT NULL) AS pct_overall_gte_3
             FROM respondents_grade_level_combined
         )
SELECT ROUND(100 * pct_grammar_gte_3, 1) AS pct_grammar_gte_3,
       ROUND(100 * pct_middle_gte_3, 1)  AS pct_middle_gte_3,
       ROUND(100 * pct_high_gte_3, 1)    AS pct_high_gte_3,
       ROUND(100 * pct_upper_gte_3, 1)   AS pct_upper_gte_3,
       ROUND(100 * pct_overall_gte_3, 1) AS pct_overall_gte_
FROM satisfaction_per_group
;

-- What's the breakdown of responses?
WITH responses AS
         (
             SELECT response_value,
                    SUM(num_individuals_in_response) AS num_responses
             FROM question_rank_responses
                      JOIN
                  respondents USING (respondent_id)
             WHERE NOT soft_delete
             GROUP BY response_value
             ORDER BY response_value DESC
         ),
     totals AS
         (
             SELECT SUM(num_responses) AS total
             FROM responses
         )
SELECT response_value,
       num_responses,
       total,
       ROUND(100. * num_responses / total, 1) AS pct
FROM responses,
     totals
;
