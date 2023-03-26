/*
 Summary of ranked questions
 */
WITH question_totals AS
         (
             SELECT question_id,
                    count(0)::numeric                                                     as question_total,
                    count(0) FILTER ( WHERE grammar )::numeric                            as grammar_total,
                    count(0) FILTER ( WHERE grammar_conferences and grammar)::numeric     as grammar_with_conferences_total,
                    count(0) FILTER ( WHERE not grammar_conferences and grammar)::numeric as grammar_without_conferences_total,
                    count(0) FILTER ( WHERE upper )::numeric                              as upper_total,
                    count(0) FILTER ( WHERE upper_conferences and upper)::numeric         as upper_with_conferences_total,
                    count(0) FILTER ( WHERE not upper_conferences and upper)::numeric     as upper_without_conferences_total,
                    count(0) FILTER ( WHERE minority )::numeric                           as minority_total,
                    count(0) FILTER ( WHERE not minority )::numeric                       as not_minority_total,
                    count(0) FILTER ( WHERE any_support )::numeric                        as recieves_support_total,
                    count(0) FILTER ( WHERE not any_support )::numeric                    as no_support_total,
                    count(0) FILTER ( WHERE tenure = 1)::numeric                          as first_year_family_total,
                    count(0) FILTER ( WHERE tenure > 1)::numeric                          as not_first_year_family_total,
                    count(0) FILTER ( WHERE tenure <= 3)::numeric                         as third_or_less_year_family_total,
                    count(0) FILTER ( WHERE tenure > 3)::numeric                          as more_than_third_year_family_total
             FROM question_rank_
                      LEFT JOIN
                  respondents using (respondent_id)
             GROUP BY question_id
         ),
     response_totals AS
         (
             SELECT question_id,
                    response,
                    count(0)                                                              as total,
                    count(0) FILTER ( WHERE grammar )                                     as grammar,
                    count(0) FILTER ( WHERE grammar_conferences and grammar)::numeric     as grammar_with_conferences,
                    count(0) FILTER ( WHERE not grammar_conferences and grammar)::numeric as grammar_without_conferences,
                    count(0) FILTER ( WHERE upper )                                       as upper,
                    count(0) FILTER ( WHERE upper_conferences and upper)::numeric         as upper_with_conferences,
                    count(0) FILTER ( WHERE not upper_conferences and upper)::numeric     as upper_without_conferences,
                    count(0) FILTER ( WHERE minority )                                    as minority,
                    count(0) FILTER ( WHERE not minority )                                as not_minority,
                    count(0) FILTER ( WHERE any_support )                                 as recieves_support,
                    count(0) FILTER ( WHERE not any_support )                             as no_support,
                    count(0) FILTER ( WHERE tenure = 1)::numeric                          as first_year_family,
                    count(0) FILTER ( WHERE tenure > 1)::numeric                          as not_first_year_family,
                    count(0) FILTER ( WHERE tenure <= 3)::numeric                         as third_year_family,
                    count(0) FILTER ( WHERE tenure > 3)::numeric                          as not_third_year_family
             FROM question_rank
                      LEFT JOIN
                  respondents using (respondent_id)
             GROUP BY question_id, response
         )
SELECT question_id,
       question_text,
       response,
       response_description,
       nullif(total, 0)                                                           as total,
       total / nullif(question_total, 0)                                          as total_pct,
       nullif(grammar, 0)                                                         as grammar,
       grammar / nullif(grammar_total, 0)                                         as grammar_pct,
       nullif(grammar_with_conferences, 0)                                        as grammar_with_conferences,
       grammar_with_conferences / nullif(grammar_with_conferences_total, 0)       as grammar_with_conferences_pct,
       nullif(grammar_without_conferences, 0)                                     as grammar_without_conferences,
       grammar_without_conferences / nullif(grammar_without_conferences_total, 0) as grammar_without_conferences_pct,
       nullif(upper, 0)                                                           as upper,
       upper / nullif(upper_total, 0)                                             as upper_pct,
       nullif(upper_with_conferences, 0)                                          as upper_with_conferences,
       upper_with_conferences / nullif(upper_with_conferences_total, 0)           as upper_with_conferences_pct,
       nullif(upper_without_conferences, 0)                                       as upper_without_conferences,
       upper_without_conferences / nullif(upper_without_conferences_total, 0)     as upper_without_conferences_pct,
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
     question using (question_id)
         LEFT JOIN
     response_definition using (question_id, response)
ORDER BY question_id, response
;


/*
 Cleaner organization of open response questions
 */
SELECT
--        question_id,
--        question_text,
--        sub_question_id,
       response,
       respondent_id,
       grammar_avg,
       upper_avg,
       overall_avg,
       tenure,
       minority,
       grammar_conferences,
       upper_conferences,
       any_support
FROM question_open_response
         JOIN
     question using (question_id)
         JOIN
     respondents using (respondent_id)
WHERE lower(response) <> 'n/a'
AND question_id = '9'
AND sub_question_id = 'child'
;
