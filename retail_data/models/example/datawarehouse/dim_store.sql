WITH source AS (

    SELECT

        store_id,
        city,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_stores') }}

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY store_id
            ORDER BY store_id
        ) AS row_num

    FROM source

)

SELECT
    store_id,
    city,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1