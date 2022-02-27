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
                    count(0) FILTER ( WHERE tenure <= 3)::numeric                         as third_year_family_total,
                    count(0) FILTER ( WHERE tenure > 3)::numeric                          as not_third_year_family_total

             FROM question_rank
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
       total,
       total / question_total                                                       as total_pct,
       grammar,
       CASE
           WHEN grammar_total = 0 THEN 0
           ELSE grammar / grammar_total END                                         as grammar_pct,
       grammar_with_conferences,
       CASE
           WHEN grammar_with_conferences_total = 0 THEN 0
           ELSE grammar_with_conferences / grammar_with_conferences_total END       as grammar_with_conferences_pct,
       grammar_without_conferences,
       CASE
           WHEN grammar_without_conferences_total = 0 THEN 0
           ELSE grammar_without_conferences / grammar_without_conferences_total END as grammar_without_conferences_pct,
       upper,
       CASE
           WHEN upper_total = 0 THEN 0
           ELSE upper / upper_total END                                             as upper_pct,
       upper_with_conferences,
       CASE
           WHEN upper_with_conferences_total = 0 THEN 0
           ELSE upper_with_conferences / upper_with_conferences_total END           as upper_with_conferences_pct,
       upper_without_conferences,
       CASE
           WHEN upper_without_conferences_total = 0 THEN 0
           ELSE upper_without_conferences / upper_without_conferences_total END     as upper_without_conferences_pct,
       minority,
       CASE
           WHEN minority_total = 0 THEN 0
           ELSE minority / minority_total END                                       as minority_pct,
       not_minority,
       CASE
           WHEN not_minority_total = 0 THEN 0
           ELSE not_minority / not_minority_total END                               as not_minority_pct,
       recieves_support,
       CASE
           WHEN recieves_support_total = 0 THEN 0
           ELSE recieves_support / recieves_support_total END                       as recieves_support_pct,
       no_support,
       CASE
           WHEN no_support_total = 0 THEN 0
           ELSE no_support / no_support_total END                                   as no_support_pct,
       first_year_family,
       CASE
           WHEN first_year_family_total = 0 THEN 0
           ELSE first_year_family / first_year_family_total END                     as first_year_family_pct,
       not_first_year_family,
       CASE
           WHEN not_first_year_family_total = 0 THEN 0
           ELSE not_first_year_family / not_first_year_family_total END             as not_first_year_family_pct,
       third_year_family,
       CASE
           WHEN third_year_family_total = 0 THEN 0
           ELSE third_year_family / third_year_family_total END                     as third_year_family_pct,
       not_third_year_family,
       CASE
           WHEN not_third_year_family_total = 0 THEN 0
           ELSE not_third_year_family / not_third_year_family_total END             as not_third_year_family_pct

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
SELECT question_id,
       question_text,
       sub_question_id,
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
;
