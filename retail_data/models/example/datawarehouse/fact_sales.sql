{{ config(
    partition_by = {
        "field": "order_date",
        "data_type": "date"
    }
) }}

WITH source AS (

    SELECT

        oi.order_item_id,
        oi.order_id,
        oi.product_id,

        o.customer_id,
        o.store_id,
        o.promotion_id,

        p.supplier_id,

        oi.qty AS quantity,
        oi.price AS unit_price,

        promo.discount,

        CAST(o.order_date AS DATE) AS order_date,

        oi.qty * oi.price AS sales_amount,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_orders') }} AS o

    LEFT JOIN {{ ref('stg_order_items') }} AS oi
        ON oi.order_id = o.order_id

    LEFT JOIN {{ ref('stg_products') }} AS p
        ON oi.product_id = p.product_id

    LEFT JOIN {{ ref('stg_promotions') }} AS promo
        ON o.promotion_id = promo.promotion_id

    WHERE oi.order_item_id IS NOT NULL

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_item_id
            ORDER BY order_item_id
        ) AS row_num

    FROM source

)

SELECT

    order_item_id,
    order_id,
    product_id,
    order_date,
    customer_id,
    store_id,
    promotion_id,
    supplier_id,
    quantity,
    unit_price,
    discount,
    sales_amount,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1