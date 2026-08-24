WITH source AS (

    SELECT

        date_id,
        day,
        month,
        quarter,
        year,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_date') }}

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY date_id
        ) AS row_num

    FROM source

)

SELECT *

EXCLUDE (row_num)

FROM unique_source

WHERE row_num = 1