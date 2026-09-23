#!/usr/bin/env Rscript
# Independent complete-design survey oracle. Inputs stay in ignored local storage.
args <- commandArgs(trailingOnly=TRUE)
value <- function(flag) {
  pos <- match(flag, args)
  if (is.na(pos) || pos == length(args)) stop(paste('missing', flag))
  args[[pos + 1L]]
}
frame_path <- value('--frame')
cases_path <- value('--cases')
output_path <- value('--output')
lib <- Sys.getenv('BRUJULA_R_LIB', '.cache/R-library')
.libPaths(c(lib, .libPaths()))
suppressPackageStartupMessages(library(survey))
suppressPackageStartupMessages(library(jsonlite))
options(survey.lonely.psu='adjust', survey.adjust.domain.lonely=FALSE)

d <- read.csv(frame_path, colClasses='character', na.strings=character(0))
required <- c('stratum','psu','weight','eda','cs_p13_1','cs_p16','cs_p14_c',
              'entity','clase1','clase2','ing7c','ingocup')
if (!setequal(names(d), required) || nrow(d) < 2L) stop('frame columns or design rows invalid')
numeric_columns <- setdiff(required, c('stratum','psu','cs_p14_c'))
for (col in numeric_columns) {
  if (any(!grepl('^-?[0-9]+(\\.[0-9]+)?$', d[[col]]))) stop(paste('invalid numeric', col))
  d[[col]] <- as.numeric(d[[col]])
}
if (any(!is.finite(d$weight) | d$weight <= 0)) stop('invalid design weights')
cases <- fromJSON(cases_path, simplifyVector=FALSE)$cases
ids <- vapply(cases, function(x) x$id, character(1))
if (!length(ids) || anyDuplicated(ids)) stop('empty or duplicate oracle cases')
d$numerator <- 0
d$denominator <- 0
design <- svydesign(ids=~psu, strata=~stratum, weights=~weight, data=d, nest=TRUE)
pack <- function(x) {
  point <- as.numeric(coef(x))
  error <- as.numeric(SE(x))
  if (length(point) != 1L || length(error) != 1L ||
      !is.finite(point) || !is.finite(error)) stop('nonfinite oracle result')
  list(estimate=point, standard_error=error)
}
results <- list()
for (spec in cases) {
  pop <- spec$population_id
  if (!(pop %in% c('national_15_plus_context','completed_professional_known_age')))
    stop('unknown oracle population')
  domain <- d$eda >= 15 & d$eda <= if (pop == 'national_15_plus_context') 98 else 97
  if (pop == 'completed_professional_known_age')
    domain <- domain & d$cs_p13_1 == 7 & d$cs_p16 == 1
  if (spec$field_of_study_id != 'all') domain <- domain & d$cs_p14_c == spec$field_of_study_id
  if (spec$geography_id != 'mx') domain <- domain & d$entity == as.numeric(spec$geography_id)
  metric <- spec$metric_id
  if (metric == 'population_total') {
    num <- as.numeric(domain)
    den <- NULL
  } else if (metric == 'occupied_total') {
    num <- as.numeric(domain & d$clase2 == 1)
    den <- NULL
  } else if (metric == 'pea_total') {
    num <- as.numeric(domain & d$clase1 == 1)
    den <- NULL
  } else if (metric == 'unemployed_total') {
    num <- as.numeric(domain & d$clase1 == 1 & d$clase2 == 2)
    den <- NULL
  } else if (metric == 'participation_rate') {
    num <- as.numeric(domain & d$clase1 == 1)
    den <- as.numeric(domain & d$clase1 %in% c(1,2))
  } else if (metric == 'unemployment_rate') {
    num <- as.numeric(domain & d$clase1 == 1 & d$clase2 == 2)
    den <- as.numeric(domain & d$clase1 == 1 & d$clase2 %in% c(1,2))
  } else if (metric == 'positive_income_mean') {
    eligible <- domain & d$clase2 == 1 & d$ing7c %in% 1:5 &
                d$ingocup >= 1 & d$ingocup <= 999998
    num <- ifelse(eligible, d$ingocup, 0)
    den <- as.numeric(eligible)
  } else stop('unsupported oracle metric')
  design <- update(design, numerator=num, denominator=if (is.null(den)) 0 else den)
  estimate <- if (is.null(den)) svytotal(~numerator, design) else
    svyratio(~numerator, ~denominator, design)
  packed <- pack(estimate)
  if (!is.null(den) && metric != 'positive_income_mean') {
    packed$estimate <- packed$estimate * 100
    packed$standard_error <- packed$standard_error * 100
  }
  results[[spec$id]] <- c(list(id=spec$id, population_id=pop,
                               field_of_study_id=spec$field_of_study_id,
                               geography_id=spec$geography_id, metric_id=metric), packed)
}
output <- list(status='PASS', r_version=R.version.string,
               survey_version=as.character(packageVersion('survey')),
               singleton_policy='adjust', domain_lonely=FALSE,
               design_df=degf(design), cases=unname(results))
write_json(output, output_path, auto_unbox=TRUE, pretty=TRUE, digits=17, null='null')
