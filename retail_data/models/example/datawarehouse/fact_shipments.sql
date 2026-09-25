WITH source AS (

    SELECT

        s.shipment_id,
        s.order_id,
        s.status,

        o.customer_id,
        o.store_id,

        current_localtimestamp() AS insertion_timestamp

    FROM {{ ref('stg_shipments') }} AS s

    LEFT JOIN {{ ref('stg_orders') }} AS o
        ON s.order_id = o.order_id

    WHERE s.shipment_id IS NOT NULL

),

unique_source AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id
            ORDER BY shipment_id
        ) AS row_num

    FROM source

)

SELECT

    shipment_id,
    order_id,
    customer_id,
    store_id,
    status,
    insertion_timestamp

FROM unique_source

WHERE row_num = 1