WITH source AS (

    SELECT

        employee_id,
        store_id,
        salary,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_employees') }}

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY employee_id
            ORDER BY employee_id
        ) AS row_num

    FROM source

)

SELECT
    employee_id,
    store_id,
    salary,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1