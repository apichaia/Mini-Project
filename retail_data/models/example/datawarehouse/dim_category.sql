WITH source AS (

    SELECT

        category_id,
        category_name,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_categories') }}

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY category_id
            ORDER BY category_id
        ) AS row_num

    FROM source

)

SELECT
    category_id,
    category_name,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1