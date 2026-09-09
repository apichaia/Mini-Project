WITH source AS (

    SELECT

        r.return_id,
        r.order_item_id,

        oi.order_id,
        oi.product_id,

        o.customer_id,
        o.store_id,

        CAST(o.order_date AS DATE) AS order_date,

        r.refund,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_returns') }} AS r

    LEFT JOIN {{ ref('stg_order_items') }} AS oi
        ON r.order_item_id = oi.order_item_id

    LEFT JOIN {{ ref('stg_orders') }} AS o
        ON oi.order_id = o.order_id

    WHERE r.return_id IS NOT NULL

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY return_id
            ORDER BY return_id
        ) AS row_num

    FROM source

)

SELECT

    return_id,
    order_item_id,
    order_id,
    product_id,
    customer_id,
    store_id,
    order_date,
    refund,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1