import os
from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import altair as alt

# --- Page Config & Modern Styling ---
st.set_page_config(
    page_title="Retail Enterprise Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
    }
    div[data-testid="stMetricLabel"] > label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 20px !important;
    }
    .main .block-container { 
        padding-top: 1.5rem; 
        max-width: 95%;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = Path(__file__).resolve().parent
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_dataset_dir():
    candidates = [
        PROJECT_ROOT / "retail_data" / "datasets",
        PROJECT_ROOT / "datasets",
        PROJECT_ROOT,
        Path.cwd() / "datasets",
        Path.cwd(),
    ]
    for candidate in candidates:
        if candidate.exists() and (candidate / "orders.csv").exists():
            return candidate
    return None


@st.cache_data
def load_full_dataset():
    dataset_dir = get_dataset_dir()
    if not dataset_dir:
        return pd.DataFrame(), pd.DataFrame()

    con = duckdb.connect(":memory:")

    tables_def = [
        ("orders.csv", "orders", "SELECT NULL::INT AS order_id, NULL::DATE AS order_date, NULL::INT AS customer_id, NULL::INT AS store_id, NULL::INT AS promotion_id WHERE 1=0"),
        ("order_items.csv", "order_items", "SELECT NULL::INT AS order_item_id, NULL::INT AS order_id, NULL::INT AS product_id, 0 AS qty, 0.0 AS price WHERE 1=0"),
        ("products.csv", "products", "SELECT NULL::INT AS product_id, 'Product ' || product_id AS product_name, NULL::INT AS category_id, NULL::INT AS supplier_id, 0.0 AS price WHERE 1=0"),
        ("categories.csv", "categories", "SELECT NULL::INT AS category_id, 'Uncategorized' AS category_name WHERE 1=0"),
        ("suppliers.csv", "suppliers", "SELECT NULL::INT AS supplier_id, 'Supplier ' || supplier_id AS supplier_name, 'Unknown Country' AS country WHERE 1=0"),
        ("customers.csv", "customers", "SELECT NULL::INT AS customer_id, 'Customer ' || customer_id AS customer_name, 'Unknown Customer City' AS city, NULL::DATE AS signup_date WHERE 1=0"),
        ("stores.csv", "stores", "SELECT NULL::INT AS store_id, 'Store ' || store_id AS store_name, 'Unknown Store City' AS city WHERE 1=0"),
        ("promotions.csv", "promotions", "SELECT NULL::INT AS promotion_id, 'Promo ' || promotion_id AS promotion_name, 0.0 AS discount WHERE 1=0"),
        ("returns.csv", "returns", "SELECT NULL::INT AS order_item_id, 0.0 AS refund WHERE 1=0"),
        ("shipments.csv", "shipments", "SELECT NULL::INT AS order_id, 'Pending' AS status, NULL::DATE AS delivery_date, NULL::DATE AS estimated_delivery_date WHERE 1=0"),
        ("payments.csv", "payments", "SELECT NULL::INT AS order_id, 0.0 AS amount WHERE 1=0"),
        ("employees.csv", "employees", "SELECT NULL::INT AS employee_id, NULL::INT AS store_id, 0.0 AS salary WHERE 1=0")
    ]

    for fname, tname, fallback_sql in tables_def:
        fpath = dataset_dir / fname
        if fpath.exists():
            p_str = str(fpath).replace("\\", "/")
            con.execute(f"CREATE TABLE {tname} AS SELECT * FROM read_csv_auto('{p_str}')")
        else:
            con.execute(f"CREATE TABLE {tname} AS {fallback_sql}")

    def ensure_column(table, col, col_type, default_val="NULL"):
        cols = [r[1].lower() for r in con.execute(f"PRAGMA table_info('{table}')").fetchall()]
        if col.lower() not in cols:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type} DEFAULT {default_val}")

    ensure_column("shipments", "status", "VARCHAR", "'Pending'")
    ensure_column("shipments", "delivery_date", "DATE", "NULL")
    ensure_column("shipments", "estimated_delivery_date", "DATE", "NULL")
    ensure_column("products", "product_name", "VARCHAR", "NULL")
    ensure_column("products", "category_id", "INT", "NULL")
    ensure_column("products", "supplier_id", "INT", "NULL")
    ensure_column("suppliers", "supplier_name", "VARCHAR", "NULL")
    ensure_column("suppliers", "country", "VARCHAR", "'Unknown Country'")
    ensure_column("stores", "store_name", "VARCHAR", "NULL")
    ensure_column("stores", "city", "VARCHAR", "'Unknown Store City'")
    ensure_column("customers", "customer_name", "VARCHAR", "NULL")
    ensure_column("customers", "city", "VARCHAR", "'Unknown Customer City'")
    ensure_column("customers", "signup_date", "DATE", "NULL")
    ensure_column("categories", "category_name", "VARCHAR", "'Uncategorized'")
    ensure_column("promotions", "promotion_name", "VARCHAR", "NULL")
    ensure_column("promotions", "discount", "DOUBLE", "0.0")

    def get_cols(tname):
        return [r[1].lower() for r in con.execute(f"PRAGMA table_info('{tname}')").fetchall()]

    prod_cols = get_cols("products")
    prod_name_sql = "prod.product_name" if "product_name" in prod_cols else ("prod.name" if "name" in prod_cols else "'Product #' || CAST(COALESCE(oi.product_id, 0) AS VARCHAR)")

    sup_cols = get_cols("suppliers")
    sup_name_sql = "sup.supplier_name" if "supplier_name" in sup_cols else ("sup.name" if "name" in sup_cols else "'Supplier #' || CAST(COALESCE(prod.supplier_id, 0) AS VARCHAR)")
    sup_country_sql = "sup.country" if "country" in sup_cols else "'Unknown Country'"

    store_cols = get_cols("stores")
    store_name_sql = "st.store_name" if "store_name" in store_cols else ("st.name" if "name" in store_cols else "'Store #' || CAST(COALESCE(o.store_id, 0) AS VARCHAR)")
    store_city_sql = "st.city" if "city" in store_cols else "'Unknown Store City'"

    promo_cols = get_cols("promotions")
    promo_name_sql = "promotion_name" if "promotion_name" in promo_cols else ("name" if "name" in promo_cols else "CASE WHEN promotion_id IS NULL OR promotion_id = 0 THEN 'No Promotion' ELSE 'Promo #' || CAST(promotion_id AS VARCHAR) END")

    cust_cols = get_cols("customers")
    cust_name_sql = "cust.customer_name" if "customer_name" in cust_cols else ("cust.name" if "name" in cust_cols else "'Customer #' || CAST(COALESCE(o.customer_id, 0) AS VARCHAR)")
    cust_city_sql = "cust.city" if "city" in cust_cols else "'Unknown Customer City'"
    cust_signup_sql = "cust.signup_date" if "signup_date" in cust_cols else "NULL::DATE"

    cat_cols = get_cols("categories")
    cat_name_sql = "c.category_name" if "category_name" in cat_cols else ("c.name" if "name" in cat_cols else "'Uncategorized'")

    try:
        query_main = f"""
            WITH base_promos AS (
                SELECT 
                    promotion_id,
                    CASE 
                        WHEN discount > 1 THEN discount / 100.0 
                        ELSE COALESCE(discount, 0.0) 
                    END AS norm_discount
                FROM promotions
            )
            SELECT 
                o.order_id,
                CAST(o.order_date AS DATE) AS order_date,
                o.store_id,
                o.customer_id,
                COALESCE(o.promotion_id, 0) AS promotion_id,
                oi.order_item_id,
                oi.product_id,
                COALESCE({prod_name_sql}, 'Product #' || CAST(COALESCE(oi.product_id, 0) AS VARCHAR)) AS product_name,
                COALESCE({cat_name_sql}, 'Uncategorized') AS category_name,
                COALESCE({sup_name_sql}, 'Supplier #' || CAST(COALESCE(prod.supplier_id, 0) AS VARCHAR)) AS supplier_name,
                COALESCE({sup_country_sql}, 'Unknown Country') AS supplier_country,
                COALESCE({store_name_sql}, 'Store #' || CAST(COALESCE(o.store_id, 0) AS VARCHAR)) AS store_name,
                COALESCE({store_city_sql}, 'Unknown Store City') AS store_city,
                COALESCE({cust_name_sql}, 'Customer #' || CAST(COALESCE(o.customer_id, 0) AS VARCHAR)) AS customer_name,
                COALESCE({cust_city_sql}, 'Unknown Customer City') AS customer_city,
                CAST({cust_signup_sql} AS DATE) AS customer_signup_date,
                'Customer #' || CAST(COALESCE(o.customer_id, 0) AS VARCHAR) AS customer_label,
                COALESCE(pro_raw_name.p_name, CASE WHEN o.promotion_id IS NULL OR o.promotion_id = 0 THEN 'ไม่มีโปรโมชัน' ELSE 'Promo #' || CAST(o.promotion_id AS VARCHAR) END) AS promotion_name,
                COALESCE(oi.qty, 0) AS quantity,
                COALESCE(oi.price, 0.0) AS unit_price,
                COALESCE(pro.norm_discount, 0.0) AS discount_rate,
                (COALESCE(oi.qty, 0) * COALESCE(oi.price, 0.0) * (1 - COALESCE(pro.norm_discount, 0.0))) AS revenue,
                (COALESCE(oi.qty, 0) * COALESCE(oi.price, 0.0) * COALESCE(pro.norm_discount, 0.0)) AS discount_amount,
                COALESCE(pay.total_payment, 0.0) AS total_payment,
                COALESCE(ret.return_count, 0) > 0 AS is_returned,
                COALESCE(ret.refund_total, 0.0) AS refund_amount,
                COALESCE(shp.status, 'Pending') AS shipment_status,
                CASE 
                    WHEN shp.delivery_date IS NOT NULL AND shp.estimated_delivery_date IS NOT NULL 
                    THEN (shp.delivery_date <= shp.estimated_delivery_date)
                    ELSE NULL 
                END AS is_on_time
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products prod ON oi.product_id = prod.product_id
            LEFT JOIN categories c ON prod.category_id = c.category_id
            LEFT JOIN suppliers sup ON prod.supplier_id = sup.supplier_id
            LEFT JOIN customers cust ON o.customer_id = cust.customer_id
            LEFT JOIN stores st ON o.store_id = st.store_id
            LEFT JOIN base_promos pro ON o.promotion_id = pro.promotion_id
            LEFT JOIN (
                SELECT promotion_id, {promo_name_sql} AS p_name FROM promotions
            ) pro_raw_name ON o.promotion_id = pro_raw_name.promotion_id
            LEFT JOIN (
                SELECT order_item_id, COUNT(*) AS return_count, SUM(refund) AS refund_total
                FROM returns
                GROUP BY order_item_id
            ) ret ON oi.order_item_id = ret.order_item_id
            LEFT JOIN (
                SELECT order_id, status, delivery_date, estimated_delivery_date
                FROM (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_id) AS rn
                    FROM shipments
                ) WHERE rn = 1
            ) shp ON o.order_id = shp.order_id
            LEFT JOIN (
                SELECT order_id, SUM(amount) AS total_payment 
                FROM payments 
                GROUP BY order_id
            ) pay ON o.order_id = pay.order_id
        """

        query_employees = f"""
            SELECT 
                e.employee_id,
                e.store_id,
                e.salary,
                COALESCE({store_city_sql}, 'Unknown Store City') AS store_city,
                COALESCE({store_name_sql}, 'Store #' || CAST(e.store_id AS VARCHAR)) AS store_name
            FROM employees e
            LEFT JOIN stores st ON e.store_id = st.store_id
        """

        df_main = con.execute(query_main).fetchdf()
        df_emp = con.execute(query_employees).fetchdf()

        return process_dataframe(df_main), df_emp
    except Exception as e:
        st.error(f"Error executing DuckDB Query: {e}")
        return pd.DataFrame(), pd.DataFrame()
    finally:
        con.close()


def process_dataframe(df):
    if df.empty:
        return df
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"]).copy()
    df["year"] = df["order_date"].dt.year
    df["year_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["month_name"] = df["order_date"].dt.strftime("%Y-%m (%B)")
    df["quarter_label"] = df["order_date"].dt.year.astype(str) + "-Q" + df["order_date"].dt.quarter.astype(str)
    df["date_label"] = df["order_date"].dt.strftime("%Y-%m-%d")
    df["day_name"] = df["order_date"].dt.strftime("%A")
    if "customer_signup_date" in df.columns:
        df["signup_year"] = pd.to_datetime(df["customer_signup_date"], errors="coerce").dt.year.fillna(0).astype(int)
    if "shipment_status" in df.columns:
        df["shipment_status"] = df["shipment_status"].astype(str).str.title()
    
    if "store_name" in df.columns and "store_city" in df.columns:
        df["store_label"] = df["store_name"] + " (" + df["store_city"] + ")"
    else:
        df["store_label"] = "Store #" + df["store_id"].astype(str)

    df["is_promo"] = df["promotion_id"].apply(lambda x: "มีโปรโมชัน" if pd.notnull(x) and x > 0 else "ไม่มีโปรโมชัน")

    return df


def main():
    st.title("🛍️ Retail Enterprise Analytics Dashboard")
    st.caption("ระบบวิเคราะห์เชิงลึกข้อมูลการขาย สิทธิประโยชน์ ลูกค้า และห่วงโซ่อุปทาน (Enterprise Business Intelligence)")

    df, df_emp = load_full_dataset()
    if df.empty:
        st.warning("⚠️ ไม่พบข้อมูลไฟล์ CSV ในโฟลเดอร์ที่กำหนด")
        return

    st.sidebar.header("🔍 ตัวกรองข้อมูล (Filters)")
    min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()

    date_range = st.sidebar.date_input(
        "ช่วงวันที่", [min_d, max_d], min_value=min_d, max_value=max_d
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_d, end_d = date_range
    elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
        start_d = end_d = date_range[0]
    else:
        start_d = end_d = date_range

    cities = st.sidebar.multiselect(
        "สาขาตามเมือง (Store City)",
        options=sorted(df["store_city"].dropna().unique()),
        default=df["store_city"].dropna().unique(),
    )
    categories = st.sidebar.multiselect(
        "หมวดหมู่สินค้า",
        options=sorted(df["category_name"].dropna().unique()),
        default=df["category_name"].dropna().unique(),
    )

    df_filtered = df[
        (df["order_date"].dt.date >= start_d)
        & (df["order_date"].dt.date <= end_d)
        & (df["store_city"].isin(cities))
        & (df["category_name"].isin(categories))
    ]

    if df_filtered.empty:
        st.info("ไม่มีข้อมูลตรงกับเงื่อนไขตัวกรองที่เลือก")
        return

    df_emp_filtered = df_emp[df_emp["store_city"].isin(cities)] if not df_emp.empty else pd.DataFrame()

    rev = df_filtered["revenue"].sum()
    orders = df_filtered["order_id"].nunique()
    qty = df_filtered["quantity"].sum()
    refunds = df_filtered["refund_amount"].sum()
    overall_aov = (rev / orders) if orders > 0 else 0

    cust_orders = df_filtered.groupby("customer_id")["order_id"].nunique()
    total_customers = len(cust_orders)
    repeat_customers = (cust_orders > 1).sum()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("ยอดขายรวม (Revenue)", f"${rev:,.0f}")
    k2.metric("จำนวนคำสั่งซื้อ", f"{orders:,.0f}")
    k3.metric("ยอดขายเฉลี่ย/คำสั่งซื้อ (AOV)", f"${overall_aov:,.2f}")
    k4.metric("สินค้าที่ขายได้", f"{qty:,.0f} ชิ้น")
    k5.metric("อัตราซื้อซ้ำ (Repeat Rate)", f"{repeat_rate:.1f}%")
    k6.metric("ยอดคืนเงินรวม (Refunds)", f"${refunds:,.0f}")

    st.markdown("---")

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📈 ยอดขาย & แนวโน้มการเติบโต",
        "📦 สินค้า & หมวดหมู่",
        "🎟️ โปรโมชัน & ชำระเงิน",
        "🏬 สาขา & ซัพพลายเออร์ (HR)",
        "👤 พฤติกรรมลูกค้า & ซื้อซ้ำ",
        "🚚 การจัดส่ง & การคืนสินค้า",
    ])

    with t1:
        st.header("📈 ยอดขายรวม แนวโน้มการเติบโต และยอดขายเฉลี่ย")

        monthly_df = df_filtered.groupby("year_month", as_index=False).agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            qty=("quantity", "sum")
        ).sort_values("year_month")
        
        monthly_df["aov"] = monthly_df.apply(lambda x: x["revenue"] / x["orders"] if x["orders"] > 0 else 0, axis=1)
        monthly_df["prev_revenue"] = monthly_df["revenue"].shift(1)
        monthly_df["mom_growth_%"] = monthly_df.apply(
            lambda x: ((x["revenue"] - x["prev_revenue"]) / x["prev_revenue"] * 100) if pd.notnull(x["prev_revenue"]) and x["prev_revenue"] > 0 else 0,
            axis=1
        )

        if not monthly_df.empty:
            max_m_row = monthly_df.loc[monthly_df["revenue"].idxmax()]
            min_m_row = monthly_df.loc[monthly_df["revenue"].idxmin()]
            latest_m_row = monthly_df.iloc[-1]

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("🟢 เดือนที่ยอดขายสูงสุด", f"{max_m_row['year_month']}", f"${max_m_row['revenue']:,.2f}")
            mc2.metric("🔴 เดือนที่ยอดขายต่ำสุด", f"{min_m_row['year_month']}", f"${min_m_row['revenue']:,.2f}")
            mc3.metric("💳 ยอดขายเฉลี่ยต่อคำสั่งซื้อ (AOV)", f"${overall_aov:,.2f}")
            mc4.metric("📊 เติบโต MoM ล่าสุด", f"{latest_m_row['year_month']}", f"{latest_m_row['mom_growth_%']:+.2f}%")

        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("ยอดขายรวมรายเดือน & อัตราการเติบโต MoM %")
            t_chart = alt.Chart(monthly_df).mark_line(point=True, color="#38bdf8", strokeWidth=3).encode(
                x=alt.X("year_month:N", title="เดือน (YYYY-MM)"),
                y=alt.Y("revenue:Q", title="ยอดขายรวม ($)"),
                tooltip=["year_month", alt.Tooltip("revenue:Q", format="$,.2f"), alt.Tooltip("mom_growth_%:Q", format="+.2f")]
            ).properties(height=320)
            st.altair_chart(t_chart, use_container_width=True)

        with c2:
            st.subheader("ยอดขายเฉลี่ยต่อคำสั่งซื้อ (AOV) รายเดือน")
            aov_chart = alt.Chart(monthly_df).mark_bar(color="#8b5cf6", cornerRadiusEnd=6).encode(
                x=alt.X("year_month:N", title="เดือน"),
                y=alt.Y("aov:Q", title="AOV ($)"),
                tooltip=["year_month", alt.Tooltip("aov:Q", format="$,.2f")]
            ).properties(height=320)
            st.altair_chart(aov_chart, use_container_width=True)

        st.subheader("📋 ตารางสรุปยอดขายแยกตามรายเดือน")
        st.dataframe(
            monthly_df[["year_month", "revenue", "orders", "aov", "mom_growth_%"]].rename(columns={
                "year_month": "เดือน",
                "revenue": "ยอดขายรวม ($)",
                "orders": "จำนวนออเดอร์",
                "aov": "ยอดขายเฉลี่ย/ออเดอร์ (AOV)",
                "mom_growth_%": "การเติบโตจากเดือนก่อน (%)"
            }).style.format({
                "ยอดขายรวม ($)": "${:,.2f}",
                "จำนวนออเดอร์": "{:,}",
                "ยอดขายเฉลี่ย/ออเดอร์ (AOV)": "${:,.2f}",
                "การเติบโตจากเดือนก่อน (%)": "{:+.2f}%"
            }),
            use_container_width=True
        )

    with t2:
        st.header("📦 การวิเคราะห์ระดับสินค้า และหมวดหมู่สินค้า")

        prod_df = df_filtered.groupby(["product_name", "category_name"], as_index=False).agg(
            total_revenue=("revenue", "sum"),
            total_qty=("quantity", "sum"),
            refund_amount=("refund_amount", "sum")
        )

        top_rev_prod = prod_df.loc[prod_df["total_revenue"].idxmax()] if not prod_df.empty else None
        top_qty_prod = prod_df.loc[prod_df["total_qty"].idxmax()] if not prod_df.empty else None

        pc1, pc2 = st.columns(2)
        if top_rev_prod is not None:
            pc1.metric("🏆 สินค้าที่สร้างรายได้สูงที่สุด", f"{top_rev_prod['product_name']}", f"${top_rev_prod['total_revenue']:,.2f}")
        if top_qty_prod is not None:
            pc2.metric("📦 สินค้าที่ขายได้จำนวนชิ้นมากที่สุด", f"{top_qty_prod['product_name']}", f"{top_qty_prod['total_qty']:,} ชิ้น")

        r1, r2 = st.columns(2)
        with r1:
            st.subheader("Top 10 สินค้าสร้างรายได้สูงสุด")
            top_rev_10 = prod_df.sort_values("total_revenue", ascending=False).head(10)
            st.altair_chart(
                alt.Chart(top_rev_10).mark_bar(color="#10b981", cornerRadiusEnd=6).encode(
                    x=alt.X("total_revenue:Q", title="รายได้ ($)"),
                    y=alt.Y("product_name:N", sort="-x", title="ชื่อสินค้า"),
                    tooltip=["product_name", "category_name", alt.Tooltip("total_revenue:Q", format="$,.2f")]
                ).properties(height=320),
                use_container_width=True
            )

        with r2:
            st.subheader("Top 10 สินค้าขายได้จำนวนชิ้นมากที่สุด")
            top_qty_10 = prod_df.sort_values("total_qty", ascending=False).head(10)
            st.altair_chart(
                alt.Chart(top_qty_10).mark_bar(color="#f59e0b", cornerRadiusEnd=6).encode(
                    x=alt.X("total_qty:Q", title="จำนวนชิ้น"),
                    y=alt.Y("product_name:N", sort="-x", title="ชื่อสินค้า"),
                    tooltip=["product_name", "category_name", alt.Tooltip("total_qty:Q", format=",d")]
                ).properties(height=320),
                use_container_width=True
            )

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("หมวดหมู่สินค้าที่ทำรายได้ดีที่สุด")
            cat_df = df_filtered.groupby("category_name", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
            st.altair_chart(
                alt.Chart(cat_df).mark_bar(color="#6366f1", cornerRadiusEnd=6).encode(
                    x=alt.X("revenue:Q", title="ยอดขายรวม ($)"),
                    y=alt.Y("category_name:N", sort="-x", title="หมวดหมู่"),
                    tooltip=["category_name", alt.Tooltip("revenue:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

        with c2:
            st.subheader("หมวดหมู่ที่มีมูลค่าการคืนสินค้าสูงสุด")
            cat_ret_df = df_filtered.groupby("category_name", as_index=False)["refund_amount"].sum().sort_values("refund_amount", ascending=False)
            st.altair_chart(
                alt.Chart(cat_ret_df).mark_bar(color="#ef4444", cornerRadiusEnd=6).encode(
                    x=alt.X("refund_amount:Q", title="มูลค่าเงินคืน ($)"),
                    y=alt.Y("category_name:N", sort="-x", title="หมวดหมู่"),
                    tooltip=["category_name", alt.Tooltip("refund_amount:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

    with t3:
        st.header("🎟️ การวิเคราะห์ผลกระทบของโปรโมชันและการชำระเงิน")

        promo_comp = df_filtered.groupby("is_promo", as_index=False).agg(
            total_revenue=("revenue", "sum"),
            orders_count=("order_id", "nunique"),
            total_qty=("quantity", "sum")
        )
        promo_comp["aov"] = promo_comp.apply(lambda x: x["total_revenue"] / x["orders_count"] if x["orders_count"] > 0 else 0, axis=1)

        p1, p2 = st.columns(2)
        with p1:
            st.subheader("เปรียบเทียบยอดขาย: มีโปรโมชัน vs ไม่มีโปรโมชัน")
            st.altair_chart(
                alt.Chart(promo_comp).mark_bar(cornerRadiusEnd=6).encode(
                    x=alt.X("is_promo:N", title="สถานะโปรโมชัน"),
                    y=alt.Y("total_revenue:Q", title="ยอดขายรวม ($)"),
                    color=alt.Color("is_promo:N", scale=alt.Scale(domain=["มีโปรโมชัน", "ไม่มีโปรโมชัน"], range=["#10b981", "#64748b"])),
                    tooltip=["is_promo", alt.Tooltip("total_revenue:Q", format="$,.2f"), "orders_count", alt.Tooltip("aov:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

        with p2:
            st.subheader("เปรียบเทียบยอดขายเฉลี่ย/คำสั่งซื้อ (AOV) จากโปรโมชัน")
            st.altair_chart(
                alt.Chart(promo_comp).mark_bar(cornerRadiusEnd=6).encode(
                    x=alt.X("is_promo:N", title="สถานะโปรโมชัน"),
                    y=alt.Y("aov:Q", title="AOV ($)"),
                    color=alt.Color("is_promo:N", scale=alt.Scale(domain=["มีโปรโมชัน", "ไม่มีโปรโมชัน"], range=["#06b6d4", "#94a3b8"])),
                    tooltip=["is_promo", alt.Tooltip("aov:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

        promo_name_df = df_filtered.groupby("promotion_name", as_index=False).agg(
            total_revenue=("revenue", "sum"),
            orders_count=("order_id", "nunique")
        ).sort_values("total_revenue", ascending=False)

        top_promo_row = promo_name_df.iloc[0] if not promo_name_df.empty else None
        if top_promo_row is not None:
            st.metric("🎟️ โปรโมชันที่สร้างรายได้จากการขายมากที่สุด", f"{top_promo_row['promotion_name']}", f"${top_promo_row['total_revenue']:,.2f}")

        st.altair_chart(
            alt.Chart(promo_name_df).mark_bar(color="#f59e0b", cornerRadiusEnd=6).encode(
                x=alt.X("total_revenue:Q", title="ยอดขายรวม ($)"),
                y=alt.Y("promotion_name:N", sort="-x", title="ชื่อโปรโมชัน"),
                tooltip=["promotion_name", alt.Tooltip("total_revenue:Q", format="$,.2f"), "orders_count"]
            ).properties(height=320),
            use_container_width=True
        )

    with t4:
        st.header("🏬 การวิเคราะห์ประสิทธิภาพสาขา ร้านค้า ซัพพลายเออร์ และ HR")

        store_df = df_filtered.groupby("store_label", as_index=False).agg(
            total_revenue=("revenue", "sum"),
            orders_count=("order_id", "nunique")
        )
        store_df["aov"] = store_df.apply(lambda x: x["total_revenue"] / x["orders_count"] if x["orders_count"] > 0 else 0, axis=1)

        best_sales_store = store_df.loc[store_df["total_revenue"].idxmax()] if not store_df.empty else None
        best_aov_store = store_df.loc[store_df["aov"].idxmax()] if not store_df.empty else None

        sup_df = df_filtered.groupby(["supplier_name", "supplier_country"], as_index=False).agg(
            total_revenue=("revenue", "sum"),
            items_sold=("quantity", "sum")
        ).sort_values("total_revenue", ascending=False)
        top_sup_row = sup_df.iloc[0] if not sup_df.empty else None

        sc1, sc2, sc3 = st.columns(3)
        if best_sales_store is not None:
            sc1.metric("🏬 ร้านค้าที่มียอดขายดีที่สุด", f"{best_sales_store['store_label']}", f"${best_sales_store['total_revenue']:,.2f}")
        if best_aov_store is not None:
            sc2.metric("💳 ร้านค้าที่มียอดขายเฉลี่ย/ออเดอร์สูงสุด", f"{best_aov_store['store_label']}", f"${best_aov_store['aov']:,.2f}")
        if top_sup_row is not None:
            sc3.metric("🏭 Supplier ที่สร้างรายได้สูงที่สุด", f"{top_sup_row['supplier_name']}", f"${top_sup_row['total_revenue']:,.2f}")

        s1, s2 = st.columns(2)
        with s1:
            st.subheader("ยอดขายรวมแยกตามร้านค้า/สาขา")
            st.altair_chart(
                alt.Chart(store_df.sort_values("total_revenue", ascending=False)).mark_bar(color="#6366f1", cornerRadiusEnd=6).encode(
                    x=alt.X("total_revenue:Q", title="ยอดขาย ($)"),
                    y=alt.Y("store_label:N", sort="-x", title="ร้านค้า/สาขา"),
                    tooltip=["store_label", alt.Tooltip("total_revenue:Q", format="$,.2f"), "orders_count"]
                ).properties(height=300),
                use_container_width=True
            )

        with s2:
            st.subheader("ยอดขายเฉลี่ยต่อคำสั่งซื้อ (AOV) แยกตามสาขา")
            st.altair_chart(
                alt.Chart(store_df.sort_values("aov", ascending=False)).mark_bar(color="#06b6d4", cornerRadiusEnd=6).encode(
                    x=alt.X("aov:Q", title="AOV ($)"),
                    y=alt.Y("store_label:N", sort="-x", title="ร้านค้า/สาขา"),
                    tooltip=["store_label", alt.Tooltip("aov:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

        st.subheader("ซัพพลายเออร์ (Supplier) ที่สร้างรายได้สูงสุด")
        st.altair_chart(
            alt.Chart(sup_df.head(10)).mark_bar(color="#ec4899", cornerRadiusEnd=6).encode(
                x=alt.X("total_revenue:Q", title="รายได้สร้างจากสินค้า ($)"),
                y=alt.Y("supplier_name:N", sort="-x", title="ชื่อ Supplier"),
                tooltip=["supplier_name", "supplier_country", alt.Tooltip("total_revenue:Q", format="$,.2f")]
            ).properties(height=300),
            use_container_width=True
        )

        if not df_emp_filtered.empty:
            st.markdown("---")
            st.subheader("📊 สถิติด้านทรัพยากรบุคคลและความคุ้มค่าแรงงาน (HR Analytics)")
            hr_city = df_emp_filtered.groupby("store_city", as_index=False).agg(
                headcount=("employee_id", "count"),
                total_payroll=("salary", "sum"),
                avg_salary=("salary", "mean"),
            )
            city_rev = df_filtered.groupby("store_city", as_index=False)["revenue"].sum()
            hr_city = pd.merge(city_rev, hr_city, on="store_city", how="outer").fillna(0)
            hr_city["revenue_per_emp"] = hr_city.apply(lambda x: x["revenue"] / x["headcount"] if x["headcount"] > 0 else 0, axis=1)
            hr_city["payroll_to_revenue_%"] = hr_city.apply(lambda x: (x["total_payroll"] / x["revenue"]) * 100 if x["revenue"] > 0 else 0, axis=1)

            st.dataframe(
                hr_city.style.format({
                    "headcount": "{:,.0f}",
                    "total_payroll": "${:,.2f}",
                    "avg_salary": "${:,.2f}",
                    "revenue": "${:,.2f}",
                    "revenue_per_emp": "${:,.2f}",
                    "payroll_to_revenue_%": "{:.2f}%",
                }),
                use_container_width=True
            )

    with t5:
        st.header("👤 การวิเคราะห์พฤติกรรมลูกค้า กลุ่มลูกค้า และการซื้อซ้ำ")

        cust_summary = df_filtered.groupby("customer_id", as_index=False).agg(
            orders_count=("order_id", "nunique"),
            total_spend=("revenue", "sum"),
            items_bought=("quantity", "sum"),
            customer_name=("customer_name", "first"),
            customer_city=("customer_city", "first")
        )

        def get_freq_segment(cnt):
            if cnt == 1:
                return "1. One-time (1 ออเดอร์)"
            elif cnt <= 3:
                return "2. Occasional (2-3 ออเดอร์)"
            elif cnt <= 5:
                return "3. Frequent (4-5 ออเดอร์)"
            else:
                return "4. VIP (6+ ออเดอร์)"

        cust_summary["segment"] = cust_summary["orders_count"].apply(get_freq_segment)
        seg_df = cust_summary.groupby("segment", as_index=False).agg(
            customer_count=("customer_id", "count"),
            total_revenue=("total_spend", "sum")
        ).sort_values("segment")

        uc1, uc2 = st.columns(2)
        uc1.metric("🔄 อัตราการกลับมาซื้อซ้ำของลูกค้า", f"{repeat_rate:.2f}%", f"{repeat_customers:,} จาก {total_customers:,} ราย")
        top_seg_row = seg_df.loc[seg_df["total_revenue"].idxmax()] if not seg_df.empty else None
        if top_seg_row is not None:
            uc2.metric("👥 กลุ่มลูกค้าที่สร้างรายได้มากที่สุด", f"{top_seg_row['segment']}", f"${top_seg_row['total_revenue']:,.2f}")

        u1, u2 = st.columns(2)
        with u1:
            st.subheader("รายได้แยกตามกลุ่มพฤติกรรมการซื้อซ้ำของลูกค้า")
            st.altair_chart(
                alt.Chart(seg_df).mark_bar(color="#3b82f6", cornerRadiusEnd=6).encode(
                    x=alt.X("total_revenue:Q", title="รายได้รวม ($)"),
                    y=alt.Y("segment:N", title="กลุ่มลูกค้า"),
                    tooltip=["segment", "customer_count", alt.Tooltip("total_revenue:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

        with u2:
            st.subheader("ยอดขายแบ่งตามเมืองของลูกค้า (Customer City Segment)")
            city_cust_df = df_filtered.groupby("customer_city", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
            st.altair_chart(
                alt.Chart(city_cust_df).mark_bar(color="#10b981", cornerRadiusEnd=6).encode(
                    x=alt.X("revenue:Q", title="ยอดขาย ($)"),
                    y=alt.Y("customer_city:N", sort="-x", title="เมืองของลูกค้า"),
                    tooltip=["customer_city", alt.Tooltip("revenue:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )

        st.subheader("🏆 Top 10 ลูกค้าที่มียอดใช้จ่ายสูงสุด")
        top_10_cust = cust_summary.sort_values("total_spend", ascending=False).head(10)
        st.dataframe(
            top_10_cust[["customer_name", "customer_city", "orders_count", "items_bought", "total_spend"]].rename(columns={
                "customer_name": "ชื่อลูกค้า",
                "customer_city": "เมือง",
                "orders_count": "จำนวนออเดอร์",
                "items_bought": "จำนวนสินค้าที่ซื้อ",
                "total_spend": "ยอดใช้จ่ายรวม ($)"
            }).style.format({
                "จำนวนออเดอร์": "{:,}",
                "จำนวนสินค้าที่ซื้อ": "{:,}",
                "ยอดใช้จ่ายรวม ($)": "${:,.2f}"
            }),
            use_container_width=True
        )

    with t6:
        st.header("🚚 การวิเคราะห์ประสิทธิภาพการจัดส่งและการคืนสินค้า")

        ship_df = df_filtered.drop_duplicates(subset=["order_id"]).copy()

        if "is_on_time" in ship_df.columns and ship_df["is_on_time"].notnull().any():
            on_time_count = ship_df["is_on_time"].sum()
            total_shipped = ship_df["is_on_time"].count()
            on_time_rate = (on_time_count / total_shipped * 100) if total_shipped > 0 else 0
        else:
            delivered_statuses = ["Delivered", "On Time", "Shipped", "Completed"]
            delivered_count = ship_df["shipment_status"].isin(delivered_statuses).sum()
            total_shipped = len(ship_df)
            on_time_rate = (delivered_count / total_shipped * 100) if total_shipped > 0 else 0

        shp_stat_df = ship_df.groupby("shipment_status", as_index=False)["order_id"].count()

        sh1, sh2 = st.columns(2)
        sh1.metric("🚚 อัตราการจัดส่งตรงเวลา/สำเร็จ", f"{on_time_rate:.1f}%", f"{total_shipped:,} ออเดอร์ทั้งหมด")
        sh2.metric("💸 มูลค่าเงินคืนรวมจากการส่งคืนสินค้า", f"${refunds:,.2f}")

        d1, d2 = st.columns(2)
        with d1:
            st.subheader("สัดส่วนสถานะการจัดส่งสินค้า")
            st.altair_chart(
                alt.Chart(shp_stat_df).mark_arc(innerRadius=50, cornerRadius=4).encode(
                    theta=alt.Theta("order_id:Q"),
                    color=alt.Color("shipment_status:N", scale=alt.Scale(scheme="tableau10"), title="สถานะ"),
                    tooltip=["shipment_status", alt.Tooltip("order_id:Q", title="จำนวนออเดอร์", format=",d")]
                ).properties(height=300),
                use_container_width=True
            )

        with d2:
            st.subheader("Top 10 สินค้าที่มีมูลค่าการคืนเงินสูงสุด")
            ret_prod_df = df_filtered.groupby("product_name", as_index=False)["refund_amount"].sum().sort_values("refund_amount", ascending=False).head(10)
            st.altair_chart(
                alt.Chart(ret_prod_df).mark_bar(color="#f43f5e", cornerRadiusEnd=6).encode(
                    x=alt.X("refund_amount:Q", title="มูลค่าคืนเงิน ($)"),
                    y=alt.Y("product_name:N", sort="-x", title="ชื่อสินค้า"),
                    tooltip=["product_name", alt.Tooltip("refund_amount:Q", format="$,.2f")]
                ).properties(height=300),
                use_container_width=True
            )


if __name__ == "__main__":
    main()