WITH source AS (

    SELECT

        customer_id,
        city,
        signup_date,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_customers') }}

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY signup_date
        ) AS row_num

    FROM source

)

SELECT
    customer_id,
    city,
    signup_date,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1