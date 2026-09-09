WITH source AS (

    SELECT

        p.payment_id,
        p.order_id,

        o.customer_id,
        o.store_id,

        CAST(o.order_date AS DATE) AS order_date,

        p.amount,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_payments') }} AS p

    LEFT JOIN {{ ref('stg_orders') }} AS o
        ON p.order_id = o.order_id

    WHERE p.payment_id IS NOT NULL

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY payment_id
            ORDER BY payment_id
        ) AS row_num

    FROM source

)

SELECT

    payment_id,
    order_id,
    customer_id,
    store_id,
    order_date,
    amount,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1