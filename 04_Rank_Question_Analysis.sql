/*
 Summary of ranked questions
 */
WITH question_totals AS
         (
             SELECT question_id,
                    count(0)::numeric                                                     as question_total,
                    count(0) FILTER ( WHERE grammar )::numeric                            as grammar_total,
                    count(0) FILTER ( WHERE high )::numeric                              as high_total,
                    count(0) FILTER ( WHERE minority )::numeric                           as minority_total,
                    count(0) FILTER ( WHERE not minority )::numeric                       as not_minority_total,
                    count(0) FILTER ( WHERE any_support )::numeric                        as recieves_support_total,
                    count(0) FILTER ( WHERE not any_support )::numeric                    as no_support_total,
                    count(0) FILTER ( WHERE tenure = 1)::numeric                          as first_year_family_total,
                    count(0) FILTER ( WHERE tenure > 1)::numeric                          as not_first_year_family_total,
                    count(0) FILTER ( WHERE tenure <= 3)::numeric                         as third_or_less_year_family_total,
                    count(0) FILTER ( WHERE tenure > 3)::numeric                          as more_than_third_year_family_total
             FROM question_rank_responses
                      LEFT JOIN
                  respondents using (respondent_id)
             GROUP BY question_id
         ),
     response_totals AS
         (
             SELECT question_id,
                    response_value,
                    count(0)                                                              as total,
                    count(0) FILTER ( WHERE grammar )                                     as grammar,
                    count(0) FILTER ( WHERE high )                                       as high,
                    count(0) FILTER ( WHERE minority )                                    as minority,
                    count(0) FILTER ( WHERE not minority )                                as not_minority,
                    count(0) FILTER ( WHERE any_support )                                 as recieves_support,
                    count(0) FILTER ( WHERE not any_support )                             as no_support,
                    count(0) FILTER ( WHERE tenure = 1)::numeric                          as first_year_family,
                    count(0) FILTER ( WHERE tenure > 1)::numeric                          as not_first_year_family,
                    count(0) FILTER ( WHERE tenure <= 3)::numeric                         as third_year_family,
                    count(0) FILTER ( WHERE tenure > 3)::numeric                          as not_third_year_family
             FROM question_rank_responses
                      LEFT JOIN
                  respondents using (respondent_id)
             GROUP BY question_id, response_value
         )
SELECT question_id,
       question_text,
       response_value,
       response_text,
       nullif(total, 0)                                                           as total,
       total / nullif(question_total, 0)                                          as total_pct,
       nullif(grammar, 0)                                                         as grammar,
       grammar / nullif(grammar_total, 0)                                         as grammar_pct,
       nullif(high, 0)                                                           as high,
       high / nullif(high_total, 0)                                             as high_pct,
       nullif(minority, 0)                                                        as minority,
       minority / nullif(minority_total, 0)                                       as minority_pct,
       nullif(not_minority, 0)                                                    as not_minority,
       not_minority / nullif(not_minority_total, 0)                               as not_minority_pct,
       nullif(recieves_support, 0)                                                as recieves_support,
       recieves_support / nullif(recieves_support_total, 0)                       as recieves_support_pct,
       nullif(no_support, 0)                                                      as no_support,
       no_support / nullif(no_support_total, 0)                                   as no_support_pct,
       nullif(first_year_family, 0)                                               as first_year_family,
       first_year_family / nullif(first_year_family_total, 0)                     as first_year_family_pct,
       nullif(not_first_year_family, 0)                                           as not_first_year_family,
       not_first_year_family / nullif(not_first_year_family_total, 0)             as not_first_year_family_pct,
       nullif(third_year_family, 0)                                               as third_year_family,
       third_year_family / nullif(third_or_less_year_family_total, 0)             as third_or_less_year_family_pct,
       nullif(not_third_year_family, 0)                                           as not_third_year_family,
       not_third_year_family / nullif(more_than_third_year_family_total, 0)       as more_than_third_year_family_pct
FROM response_totals
         INNER JOIN
     question_totals using (question_id)
         LEFT JOIN
     questions using (question_id)
         LEFT JOIN
     question_response_mapping using (question_id, response_value)
ORDER BY question_id, response_value
;


-- What % of responses are Satisfied or Very Satisfied?
SELECT round(100. * sum(response_value * num_individuals_in_response) FILTER ( WHERE response_value >= 3 ) / sum(response_value * num_individuals_in_response), 1)
FROM sac_survey_2023.respondents
JOIN
    sac_survey_2023.question_rank_responses using(respondent_id)
;