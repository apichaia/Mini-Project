import os
from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import altair as alt

# --- Page Config & Modern Styling ---
st.set_page_config(
    page_title="Retail Enterprise Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Contrast Glassmorphism Theme
st.markdown("""
<style>
    /* Metric Cards Styling */
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
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Tabs Custom Styling */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 20px !important;
    }
    
    /* Main Layout Tweaks */
    .main .block-container { 
        padding-top: 2rem; 
        max-width: 95%;
    }
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = Path(__file__).resolve().parent

def get_dataset_dir():
    candidates = [
        PROJECT_ROOT / "retail_data" / "datasets",
        PROJECT_ROOT / "datasets",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

@st.cache_data
def load_full_dataset():
    dataset_dir = get_dataset_dir()
    if not dataset_dir:
        return pd.DataFrame()

    con = duckdb.connect(":memory:")

    def p(filename): 
        return str(dataset_dir / filename).replace("\\", "/")

    try:
        query = f"""
            SELECT 
                o.order_id,
                CAST(o.order_date AS DATE) AS order_date,
                oi.order_item_id,
                oi.product_id,
                'Product #' || CAST(oi.product_id AS VARCHAR) AS product_name,
                COALESCE(c.category_name, 'Uncategorized') AS category_name,
                COALESCE(sup.country, 'Unknown Country') AS supplier_country,
                COALESCE(st.city, 'Unknown Store City') AS store_city,
                COALESCE(cust.city, 'Unknown Customer City') AS customer_city,
                'Customer #' || CAST(o.customer_id AS VARCHAR) AS customer_label,
                oi.qty AS quantity,
                oi.price AS unit_price,
                COALESCE(pro.discount, 0.0) AS discount_rate,
                (oi.qty * oi.price * (1 - COALESCE(pro.discount, 0.0))) AS revenue,
                (oi.qty * oi.price * COALESCE(pro.discount, 0.0)) AS discount_amount,
                COALESCE(pay.total_payment, 0.0) AS total_payment,
                ret.refund IS NOT NULL AS is_returned,
                COALESCE(ret.refund, 0.0) AS refund_amount,
                COALESCE(shp.status, 'Pending') AS shipment_status
            FROM read_csv_auto('{p("orders.csv")}') o
            LEFT JOIN read_csv_auto('{p("order_items.csv")}') oi ON o.order_id = oi.order_id
            LEFT JOIN read_csv_auto('{p("products.csv")}') p ON oi.product_id = p.product_id
            LEFT JOIN read_csv_auto('{p("categories.csv")}') c ON p.category_id = c.category_id
            LEFT JOIN read_csv_auto('{p("suppliers.csv")}') sup ON p.supplier_id = sup.supplier_id
            LEFT JOIN read_csv_auto('{p("customers.csv")}') cust ON o.customer_id = cust.customer_id
            LEFT JOIN read_csv_auto('{p("stores.csv")}') st ON o.store_id = st.store_id
            LEFT JOIN read_csv_auto('{p("promotions.csv")}') pro ON o.promotion_id = pro.promotion_id
            LEFT JOIN read_csv_auto('{p("returns.csv")}') ret ON oi.order_item_id = ret.order_item_id
            LEFT JOIN read_csv_auto('{p("shipments.csv")}') shp ON o.order_id = shp.order_id
            LEFT JOIN (
                SELECT order_id, SUM(amount) AS total_payment 
                FROM read_csv_auto('{p("payments.csv")}') 
                GROUP BY order_id
            ) pay ON o.order_id = pay.order_id
        """
        df = con.execute(query).fetchdf()
        con.close()
        return process_dataframe(df)
    except Exception as e:
        st.error(f"Error executing DuckDB Query: {e}")
        con.close()
        return pd.DataFrame()

def process_dataframe(df):
    if df.empty:
        return df
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["quarter_label"] = "Q" + df["order_date"].dt.quarter.astype(str)
    df["month_name"] = df["order_date"].dt.strftime("%Y-%m (%B)")
    df["date_label"] = df["order_date"].dt.strftime("%Y-%m-%d")
    df["day_name"] = df["order_date"].dt.strftime("%A")
    return df

def main():
    st.title("🛍️ Retail Enterprise Dashboard")
    st.caption("ระบบวิเคราะห์ข้อมูลการขาย OLAP แบบเรียลไทม์")

    df = load_full_dataset()
    if df.empty:
        st.warning("⚠️ ไม่พบข้อมูลไฟล์ CSV ในโฟลเดอร์ datasets")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("🔍 ตัวกรองข้อมูล (Filters)")
    min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()
    start_d, end_d = st.sidebar.date_input("ช่วงวันที่", [min_d, max_d], min_value=min_d, max_value=max_d)

    cities = st.sidebar.multiselect("สาขาตามเมือง (Store City)", options=sorted(df["store_city"].dropna().unique()), default=df["store_city"].dropna().unique())
    categories = st.sidebar.multiselect("หมวดหมู่สินค้า", options=sorted(df["category_name"].dropna().unique()), default=df["category_name"].dropna().unique())

    df_filtered = df[
        (df["order_date"].dt.date >= start_d) & 
        (df["order_date"].dt.date <= end_d) &
        (df["store_city"].isin(cities)) &
        (df["category_name"].isin(categories))
    ]

    # --- Executive High-Contrast KPIs ---
    rev = df_filtered["revenue"].sum()
    orders = df_filtered["order_id"].nunique()
    qty = df_filtered["quantity"].sum()
    refunds = df_filtered["refund_amount"].sum()
    disc_val = df_filtered["discount_amount"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("ยอดขายรวม (Revenue)", f"${rev:,.0f}")
    k2.metric("จำนวนออเดอร์", f"{orders:,.0f}")
    k3.metric("สินค้าที่ขายได้", f"{qty:,.0f} ชิ้น")
    k4.metric("ยอดคืนเงิน (Refunds)", f"${refunds:,.0f}")
    k5.metric("ส่วนลดรวม (Discounts)", f"${disc_val:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Dashboard Tabs ---
    t1, t2, t3, t4, t5 = st.tabs([
        "📈 ยอดขาย & เวลา", 
        "📦 การคืนสินค้า & ขนส่ง", 
        "🎟️ โปรโมชัน & ชำระเงิน", 
        "🏬 สาขา & ซัพพลายเออร์", 
        "👤 พฤติกรรมลูกค้า"
    ])

    # Tab 1: Sales & Time
    with t1:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("แนวโน้มยอดขายตามช่วงเวลา")
            t_level = st.selectbox("มุมมองเวลา", ["date_label", "month_name", "quarter_label", "day_name"], index=0)
            t_df = df_filtered.groupby(t_level, as_index=False)["revenue"].sum()
            chart = alt.Chart(t_df).mark_line(point=True, color="#38bdf8", strokeWidth=3).encode(
                x=alt.X(f"{t_level}:N", title="ช่วงเวลา"),
                y=alt.Y("revenue:Q", title="ยอดขาย ($)"),
                tooltip=[t_level, alt.Tooltip("revenue:Q", format="$,.2f")]
            ).properties(height=340)
            st.altair_chart(chart, use_container_width=True)

        with c2:
            st.subheader("ยอดขายตามหมวดหมู่สินค้า")
            cat_df = df_filtered.groupby("category_name", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
            cat_chart = alt.Chart(cat_df).mark_bar(cornerRadiusEnd=6, color="#10b981").encode(
                x=alt.X("revenue:Q", title="ยอดขาย ($)"),
                y=alt.Y("category_name:N", sort="-x", title="หมวดหมู่"),
                tooltip=["category_name", alt.Tooltip("revenue:Q", format="$,.2f")]
            ).properties(height=340)
            st.altair_chart(cat_chart, use_container_width=True)

    # Tab 2: Returns & Shipments
    with t2:
        r1, r2 = st.columns(2)
        with r1:
            st.subheader("ยอดเงินคืน (Refunds) ตามหมวดหมู่")
            ret_df = df_filtered[df_filtered["is_returned"] == True].groupby("category_name", as_index=False)["refund_amount"].sum()
            ret_chart = alt.Chart(ret_df).mark_bar(cornerRadiusEnd=6, color="#f43f5e").encode(
                x=alt.X("refund_amount:Q", title="มูลค่าเงินคืน ($)"),
                y=alt.Y("category_name:N", sort="-x", title="หมวดหมู่"),
                tooltip=["category_name", alt.Tooltip("refund_amount:Q", format="$,.2f")]
            ).properties(height=300)
            st.altair_chart(ret_chart, use_container_width=True)

        with r2:
            st.subheader("สัดส่วนสถานะการจัดส่ง (Shipment Status)")
            shp_df = df_filtered.groupby("shipment_status", as_index=False)["order_id"].nunique()
            shp_chart = alt.Chart(shp_df).mark_arc(innerRadius=45, cornerRadius=4).encode(
                theta=alt.Theta("order_id:Q"),
                color=alt.Color("shipment_status:N", scale=alt.Scale(scheme="tableau10"), title="สถานะ"),
                tooltip=["shipment_status", "order_id"]
            ).properties(height=300)
            st.altair_chart(shp_chart, use_container_width=True)

    # Tab 3: Promotions & Payments
    with t3:
        p1, p2 = st.columns(2)
        with p1:
            st.subheader("ผลกระทบของส่วนลดต่อยอดขาย")
            promo_df = df_filtered.groupby("discount_rate", as_index=False).agg(
                total_revenue=("revenue", "sum"),
                total_orders=("order_id", "nunique")
            )
            promo_df["discount_percent"] = (promo_df["discount_rate"] * 100).astype(int).astype(str) + "%"
            p_chart = alt.Chart(promo_df).mark_bar(cornerRadiusTop=6, color="#f59e0b").encode(
                x=alt.X("discount_percent:N", title="อัตราส่วนลด"),
                y=alt.Y("total_revenue:Q", title="ยอดขายรวม ($)"),
                tooltip=["discount_percent", alt.Tooltip("total_revenue:Q", format="$,.2f"), "total_orders"]
            ).properties(height=320)
            st.altair_chart(p_chart, use_container_width=True)

        with p2:
            st.subheader("ยอดการชำระเงินเทียบกับยอดขาย")
            pay_df = pd.DataFrame({
                "Category": ["Gross Sales", "Payments Received", "Discounts Given"],
                "Amount": [rev, df_filtered["total_payment"].sum(), disc_val]
            })
            pay_chart = alt.Chart(pay_df).mark_bar(cornerRadiusEnd=6, color="#8b5cf6").encode(
                x=alt.X("Amount:Q", title="มูลค่า ($)"),
                y=alt.Y("Category:N", sort="-x", title="รายการ"),
                tooltip=["Category", alt.Tooltip("Amount:Q", format="$,.2f")]
            ).properties(height=320)
            st.altair_chart(pay_chart, use_container_width=True)

    # Tab 4: Store & Supplier
    with t4:
        s1, s2 = st.columns(2)
        with s1:
            st.subheader("ยอดขายแบ่งตามเมืองที่ตั้งสาขา")
            st_df = df_filtered.groupby("store_city", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
            st.altair_chart(alt.Chart(st_df).mark_bar(cornerRadiusEnd=6, color="#6366f1").encode(
                x=alt.X("revenue:Q", title="ยอดขาย ($)"),
                y=alt.Y("store_city:N", sort="-x", title="เมืองที่ตั้งสาขา"),
                tooltip=["store_city", alt.Tooltip("revenue:Q", format="$,.2f")]
            ).properties(height=300), use_container_width=True)

        with s2:
            st.subheader("ยอดขายแบ่งตามประเทศซัพพลายเออร์")
            sup_df = df_filtered.groupby("supplier_country", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
            st.altair_chart(alt.Chart(sup_df).mark_bar(cornerRadiusEnd=6, color="#06b6d4").encode(
                x=alt.X("revenue:Q", title="ยอดขาย ($)"),
                y=alt.Y("supplier_country:N", sort="-x", title="ประเทศ"),
                tooltip=["supplier_country", alt.Tooltip("revenue:Q", format="$,.2f")]
            ).properties(height=300), use_container_width=True)

    # Tab 5: Customers
    with t5:
        st.subheader("Top ลูกค้าที่มียอดซื้อสูงสุด")
        cust_df = df_filtered.groupby(["customer_label", "customer_city"], as_index=False).agg(
            total_spend=("revenue", "sum"),
            orders_count=("order_id", "nunique"),
            items_bought=("quantity", "sum")
        ).sort_values("total_spend", ascending=False).head(10)

        st.dataframe(
            cust_df.style.format({"total_spend": "${:,.2f}", "orders_count": "{:,}", "items_bought": "{:,}"}),
            use_container_width=True
        )

if __name__ == "__main__":
    main()