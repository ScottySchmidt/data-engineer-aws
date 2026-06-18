/*
Athena SQL version of the Part 3 analytics notebook.

This script shows how the BLS and DataUSA outputs stored in S3 can be queried
with Athena. The raw tables are cleaned with views, then used for population
summary statistics, BLS yearly totals, and a final joined report.
*/

CREATE OR REPLACE VIEW bls_productivity_db.v_datausa_population_clean AS
SELECT
    '01000US' AS nation_id,
    json_extract_scalar(row_json, '$.Nation') AS nation,
    CAST(json_extract_scalar(row_json, '$.Year') AS INTEGER) AS year,
    CAST(json_extract_scalar(row_json, '$.Population') AS DOUBLE) AS population
FROM bls_productivity_db.datausa_population_raw_json
CROSS JOIN UNNEST(
    CAST(json_extract(json_line, '$.data') AS ARRAY(JSON))
) AS t(row_json);


CREATE OR REPLACE VIEW bls_productivity_db.v_bls_part1_clean AS
SELECT
    TRIM(series_id) AS series_id,
    CAST(year AS INTEGER) AS year,
    TRIM(period) AS period,
    CAST(value AS DOUBLE) AS bls_value,
    footnote_codes
FROM bls_productivity_db.bls_bulk_current
WHERE TRIM(period) IN ('Q01', 'Q02', 'Q03', 'Q04')
  AND TRY_CAST(year AS INTEGER) IS NOT NULL
  AND TRY_CAST(value AS DOUBLE) IS NOT NULL;


/*
Population summary for 2013 through 2018.
*/

SELECT
    AVG(population) AS mean_population,
    STDDEV_SAMP(population) AS stddev_population
FROM bls_productivity_db.v_datausa_population_clean
WHERE year BETWEEN 2013 AND 2018;


/*
Best year by BLS series based on the highest summed quarterly value.
*/

WITH yearly_totals AS (
    SELECT
        series_id,
        year,
        SUM(bls_value) AS total_value
    FROM bls_productivity_db.v_bls_part1_clean
    GROUP BY series_id, year
),

ranked AS (
    SELECT
        series_id,
        year,
        total_value,
        ROW_NUMBER() OVER (
            PARTITION BY series_id
            ORDER BY total_value DESC
        ) AS rn
    FROM yearly_totals
)

SELECT
    series_id,
    year AS best_year,
    total_value AS best_year_total_value
FROM ranked
WHERE rn = 1
ORDER BY series_id;


/*
Final joined report.

This joins BLS series PRS30006032 for Q01 with annual United States population
by year.
*/

SELECT
    b.series_id,
    b.year,
    b.period,
    b.bls_value,
    CAST(p.population AS BIGINT) AS population
FROM bls_productivity_db.v_bls_part1_clean b
INNER JOIN bls_productivity_db.v_datausa_population_clean p
    ON b.year = p.year
WHERE b.series_id = 'PRS30006032'
  AND b.period = 'Q01'
ORDER BY b.year;
