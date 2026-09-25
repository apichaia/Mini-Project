import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# Page Setup & Styling
# =========================================================
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .main-title { font-size: 1.6rem; font-weight: 700; margin: 0; }
    .main-subtitle { font-size: 0.95rem; color: #94A3B8; margin-top: 6px; line-height: 1.4; }
    
    /* ปรับขนาดตัวอักษรของ Metric ให้สั้นกระชับไม่ล้นกรอบ */
    [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "dev.duckdb"

# =========================================================
# 1. Database ETL Initialization
# =========================================================
@st.cache_resource
def init_database():
    conn = duckdb.connect(str(DB_PATH))
    
    def recreate_table(table_name, select_sql):
        try:
            conn.execute(f'CREATE OR REPLACE TABLE main."{table_name}" AS {select_sql};')
        except Exception:
            pass

    def get_csv_path(filename):
        paths_to_check = [
            PROJECT_ROOT.parent / "datasets" / filename,
            PROJECT_ROOT / "datasets" / filename,
            PROJECT_ROOT / filename
        ]
        for p in paths_to_check:
            if p.exists():
                return p.as_posix()
        return None

    csv_mapping = {
        "categories.csv": "stg_categories", "customers.csv": "stg_customers",
        "employees.csv": "stg_employees", "order_items.csv": "stg_order_items",
        "orders.csv": "stg_orders", "payments.csv": "stg_payments",
        "products.csv": "stg_products", "promotions.csv": "stg_promotions",
        "returns.csv": "stg_returns", "shipments.csv": "stg_shipments",
        "stores.csv": "stg_stores", "suppliers.csv": "stg_suppliers"
    }
    
    for csv_file, table_name in csv_mapping.items():
        found_path = get_csv_path(csv_file)
        if found_path:
            recreate_table(table_name, f"SELECT * FROM read_csv_auto('{found_path}')")

    dim_mappings = {
        "dim_category": "stg_categories", "dim_customer": "stg_customers",
        "dim_employee": "stg_employees", "dim_product": "stg_products",
        "dim_promotion": "stg_promotions", "dim_store": "stg_stores",
        "dim_supplier": "stg_suppliers",
    }
    for dim_table, stg_table in dim_mappings.items():
        recreate_table(dim_table, f'SELECT * FROM main."{stg_table}"')

    recreate_table("fact_returns", 'SELECT * FROM main.stg_returns')
    recreate_table("fact_sales", """
        SELECT 
            oi.order_item_id, oi.order_id, oi.product_id,
            oi.qty AS units_sold, oi.price AS unit_price,
            (oi.qty * oi.price) AS revenue,
            o.customer_id, o.store_id, o.promotion_id, o.order_date
        FROM main.stg_order_items oi
        LEFT JOIN main.stg_orders o ON oi.order_id = o.order_id
    """)
    recreate_table("fact_shipments", """
        SELECT 
            sh.shipment_id, sh.order_id, sh.shipment_status,
            o.store_id,
            COALESCE('Store ' || CAST(o.store_id AS VARCHAR), 'Unknown Store') AS store_name,
            o.order_date,
            COALESCE(TRIM(st.region), 'Unspecified') AS region
        FROM main.stg_shipments sh
        LEFT JOIN main.stg_orders o ON sh.order_id = o.order_id
        LEFT JOIN main.dim_store st ON o.store_id = st.store_id
    """)
    recreate_table("fact_payments", """
        SELECT 
            p.payment_id, p.order_id, p.amount AS payment_amount,
            o.customer_id, o.order_date,
            COALESCE(TRIM(st.region), 'Unspecified') AS region,
            COALESCE(TRIM(c.city), 'Unspecified') AS customer_city
        FROM main.stg_payments p
        LEFT JOIN main.stg_orders o ON p.order_id = o.order_id
        LEFT JOIN main.dim_store st ON o.store_id = st.store_id
        LEFT JOIN main.dim_customer c ON o.customer_id = c.customer_id
    """)
    conn.close()

init_database()

def run_query(query):
    try:
        conn = duckdb.connect(str(DB_PATH), read_only=True)
        df = conn.execute(query).fetch_df()
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# =========================================================
# 2. Data Loading & Data Cleaning
# =========================================================
def enrich_date_features(df, date_col='order_date'):
    if not df.empty and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['Year'] = df[date_col].dt.year.fillna(0).astype(int).astype(str)
        df['Quarter'] = 'Q' + df[date_col].dt.quarter.fillna(0).astype(int).astype(str)
        df['Month'] = df[date_col].dt.to_period('M').astype(str)
        df['Year_Q'] = df['Year'] + "-" + df['Quarter']
    return df

@st.cache_data(ttl=600)
def load_sales_returns_data():
    query = """
        SELECT 
            s.order_item_id, s.order_id, s.order_date, s.units_sold, s.revenue,
            COALESCE(TRIM(st.region), 'Unspecified') AS region,
            s.customer_id, COALESCE(TRIM(c.city), 'Unspecified') AS customer_city,
            s.product_id, COALESCE(TRIM(cat.category_name), 'Unspecified') AS category,
            COALESCE(CAST(p.discount AS VARCHAR) || '% Discount', 'No Discount') AS promotion_name,
            COALESCE(TRIM(sup.country), 'Unspecified') AS supplier_country,
            COALESCE(r.refund, 0) AS refund_amount
        FROM main.fact_sales s
        LEFT JOIN main.dim_store st ON s.store_id = st.store_id
        LEFT JOIN main.dim_customer c ON s.customer_id = c.customer_id
        LEFT JOIN main.dim_product pr ON s.product_id = pr.product_id
        LEFT JOIN main.dim_category cat ON pr.category_id = cat.category_id
        LEFT JOIN main.dim_promotion p ON s.promotion_id = p.promotion_id
        LEFT JOIN main.dim_supplier sup ON pr.supplier_id = sup.supplier_id
        LEFT JOIN main.fact_returns r ON s.order_item_id = r.order_item_id
    """
    df = run_query(query)
    return enrich_date_features(df)

@st.cache_data(ttl=600)
def load_shipments_data():
    df = run_query("SELECT * FROM main.fact_shipments")
    if not df.empty:
        if 'store_name' not in df.columns:
            df['store_name'] = "Store " + df['store_id'].astype(str) if 'store_id' in df.columns else "Unknown Store"
        if 'region' not in df.columns: df['region'] = "Unspecified"
        if 'shipment_status' not in df.columns: df['shipment_status'] = "Unknown"
    return enrich_date_features(df)

@st.cache_data(ttl=600)
def load_payments_data():
    df = run_query("SELECT * FROM main.fact_payments")
    if not df.empty:
        if 'region' not in df.columns: df['region'] = "Unspecified"
        if 'customer_city' not in df.columns: df['customer_city'] = "Unspecified"
    return enrich_date_features(df)

df_sales_raw = load_sales_returns_data()
df_ships_raw = load_shipments_data()
df_pays_raw = load_payments_data()

if df_sales_raw.empty:
    st.error("⚠️ ไม่พบข้อมูลในระบบ")
    st.stop()

# Theme Settings
px.defaults.template = "plotly_white"
COLOR_PALETTE = ["#6366F1", "#0EA5E9", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]
px.defaults.color_discrete_sequence = COLOR_PALETTE

def sort_categories(cat_list):
    def extract_num(val):
        nums = [int(s) for s in val.split('_') if s.isdigit()]
        return nums[0] if nums else 999
    return sorted(cat_list, key=extract_num)

# =========================================================
# 3. Dynamic Sidebar Hierarchies
# =========================================================
st.sidebar.markdown("### 📅 Time Filters")

years = ["All"] + sorted(df_sales_raw['Year'].unique().tolist())
sel_year = st.sidebar.selectbox("Year", years)

df_sales = df_sales_raw.copy()
if sel_year != "All":
    df_sales = df_sales[df_sales['Year'] == sel_year]

quarters = ["All"] + sorted(df_sales['Quarter'].unique().tolist())
sel_quarter = st.sidebar.selectbox("Quarter", quarters)
if sel_quarter != "All":
    df_sales = df_sales[df_sales['Quarter'] == sel_quarter]

months = ["All"] + sorted(df_sales['Month'].unique().tolist())
sel_month = st.sidebar.selectbox("Month", months)
if sel_month != "All":
    df_sales = df_sales[df_sales['Month'] == sel_month]

st.sidebar.markdown("### 🌍 Location Filters")

countries = ["All"] + sorted(df_sales['supplier_country'].unique().tolist())
sel_country = st.sidebar.selectbox("Country (Supplier)", countries)
if sel_country != "All":
    df_sales = df_sales[df_sales['supplier_country'] == sel_country]

cities = ["All"] + sorted(df_sales['customer_city'].unique().tolist())
sel_city = st.sidebar.selectbox("City (Customer)", cities)
if sel_city != "All":
    df_sales = df_sales[df_sales['customer_city'] == sel_city]

regions = ["All"] + sorted(df_sales['region'].unique().tolist())
sel_region = st.sidebar.selectbox("Region (Store)", regions)
if sel_region != "All":
    df_sales = df_sales[df_sales['region'] == sel_region]

df_ships = df_ships_raw.copy()
df_pays = df_pays_raw.copy()

if sel_year != "All":
    if not df_ships.empty and 'Year' in df_ships.columns: df_ships = df_ships[df_ships['Year'] == sel_year]
    if not df_pays.empty and 'Year' in df_pays.columns: df_pays = df_pays[df_pays['Year'] == sel_year]
if sel_quarter != "All":
    if not df_ships.empty and 'Quarter' in df_ships.columns: df_ships = df_ships[df_ships['Quarter'] == sel_quarter]
    if not df_pays.empty and 'Quarter' in df_pays.columns: df_pays = df_pays[df_pays['Quarter'] == sel_quarter]
if sel_month != "All":
    if not df_ships.empty and 'Month' in df_ships.columns: df_ships = df_ships[df_ships['Month'] == sel_month]
    if not df_pays.empty and 'Month' in df_pays.columns: df_pays = df_pays[df_pays['Month'] == sel_month]
if sel_region != "All":
    if not df_ships.empty and 'region' in df_ships.columns: df_ships = df_ships[df_ships['region'] == sel_region]
    if not df_pays.empty and 'region' in df_pays.columns: df_pays = df_pays[df_pays['region'] == sel_region]
if sel_city != "All":
    if not df_pays.empty and 'customer_city' in df_pays.columns: df_pays = df_pays[df_pays['customer_city'] == sel_city]

# =========================================================
# 4. Main Header & Compact KPI Metrics
# =========================================================
st.markdown("""
    <div class="main-header">
        <div class="main-title">📈 Retail Analytics Dashboard (ระบบวิเคราะห์ข้อมูลการขายปลีก)</div>
        <div class="main-subtitle">
           ระบบวิเคราะห์เชิงลึกข้อมูลการขาย สิทธิประโยชน์ ลูกค้า และห่วงโซ่อุปทาน (Enterprise Business Intelligence)
        </div>
    </div>
""", unsafe_allow_html=True)

# ฟังก์ชันแสดงผลตัวเลขแบบย่อสั้นพิเศษ ไม่ให้ดันกรอบจนเป็นจุดไข่ปลา
def format_metric(num):
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}K"
    return f"{num:,.0f}"

tot_rev = df_sales['revenue'].sum()
tot_ord = df_sales['order_id'].nunique()
tot_units = df_sales['units_sold'].sum()
aov_val = tot_rev / tot_ord if tot_ord > 0 else 0
tot_cust = df_sales['customer_id'].nunique()
tot_ref = df_sales['refund_amount'].sum()

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Revenue", f"${format_metric(tot_rev)}")
m2.metric("Orders", f"{format_metric(tot_ord)}")
m3.metric("Units Sold", f"{format_metric(tot_units)}")
m4.metric("AOV", f"${format_metric(aov_val)}")
m5.metric("Active Customers", f"{format_metric(tot_cust)}")
m6.metric("Total Refunds", f"${format_metric(tot_ref)}")

st.markdown("<br>", unsafe_allow_html=True)

all_cats_sorted = sort_categories(df_sales['category'].unique().tolist())

# =========================================================
# 5. Core Business Domain Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Revenue Trends",
    "👥 Customer Insights",
    "📦 Product Performance",
    "🚚 Supply Chain & Returns",
    "⚙️ Logistics & Finance"
])

# ---------------------------------------------------------
# TAB 1: Revenue Trends
# ---------------------------------------------------------
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Monthly Revenue Trend")
        q_m_rev = df_sales.groupby(['Month', 'region'])['revenue'].sum().reset_index()
        if not q_m_rev.empty:
            fig1 = px.line(q_m_rev, x='Month', y='revenue', color='region', markers=True)
            fig1.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("##### 📌 Annual Revenue Breakdown")
        q_a_rev = df_sales.groupby(['Year', 'region'])['revenue'].sum().reset_index()
        if not q_a_rev.empty:
            fig2 = px.bar(q_a_rev, x='Year', y='revenue', color='region', barmode='group', text_auto='.2s')
            fig2.update_traces(textposition="outside")
            fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
            st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Quarterly AOV Trend")
        q_q_aov = df_sales.groupby(['Year_Q', 'region']).agg(rev=('revenue', 'sum'), ord=('order_id', 'nunique')).reset_index()
        if not q_q_aov.empty:
            q_q_aov['AOV'] = q_q_aov['rev'] / q_q_aov['ord']
            fig4 = px.line(q_q_aov, x='Year_Q', y='AOV', color='region', markers=True)
            fig4.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
            st.plotly_chart(fig4, use_container_width=True)
    with col4:
        st.empty()

# ---------------------------------------------------------
# TAB 2: Customer Insights
# ---------------------------------------------------------
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Monthly Active Purchasers by City")
        q_act_cust = df_sales.groupby(['Month', 'customer_city'])['customer_id'].nunique().reset_index(name='active_customers')
        if not q_act_cust.empty:
            fig_act = px.line(q_act_cust, x='Month', y='active_customers', color='customer_city', markers=True)
            fig_act.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_act, use_container_width=True)

    with col2:
        st.markdown("##### 📌 Customer AOV by City")
        q_city_aov = df_sales.groupby(['customer_city', 'Year']).agg(rev=('revenue', 'sum'), ord=('order_id', 'nunique')).reset_index()
        if not q_city_aov.empty:
            q_city_aov['Customer_AOV'] = q_city_aov['rev'] / q_city_aov['ord']
            fig_caov = px.bar(q_city_aov, x='customer_city', y='Customer_AOV', color='Year', barmode='group')
            fig_caov.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
            st.plotly_chart(fig_caov, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Monthly Order Volume")
        q_m_ord = df_sales.groupby(['Month', 'region'])['order_id'].nunique().reset_index(name='order_count')
        if not q_m_ord.empty:
            fig_ord = px.bar(q_m_ord, x='Month', y='order_count', color='region', barmode='group')
            fig_ord.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_ord, use_container_width=True)
    with col4:
        st.empty()

# ---------------------------------------------------------
# TAB 3: Product Performance
# ---------------------------------------------------------
with tab3:
    st.markdown("##### 🔍 Filter by Specific Categories")
    f_cat = st.multiselect("เลือกหมวดหมู่สินค้า:", all_cats_sorted, default=all_cats_sorted[:5], key="ms_t3_cat")
    
    df_t3 = df_sales.copy()
    if f_cat:
        df_t3 = df_t3[df_t3['category'].isin(f_cat)]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Category Revenue by Region")
        q_cat_rev = df_t3.groupby(['category', 'region'])['revenue'].sum().reset_index()
        if not q_cat_rev.empty:
            q_cat_rev['cat_sorted'] = pd.Categorical(q_cat_rev['category'], categories=all_cats_sorted, ordered=True)
            q_cat_rev = q_cat_rev.sort_values('cat_sorted')
            fig_cat_rev = px.bar(q_cat_rev, x='category', y='revenue', color='region', barmode='group')
            fig_cat_rev.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$", xaxis_tickangle=-45)
            st.plotly_chart(fig_cat_rev, use_container_width=True)

    with col2:
        st.markdown("##### 📌 Units Sold by Category")
        q_cat_unit = df_t3.groupby(['category', 'region'])['units_sold'].sum().reset_index()
        if not q_cat_unit.empty:
            q_cat_unit['cat_sorted'] = pd.Categorical(q_cat_unit['category'], categories=all_cats_sorted, ordered=True)
            q_cat_unit = q_cat_unit.sort_values('cat_sorted')
            fig_cat_unit = px.bar(q_cat_unit, x='category', y='units_sold', color='region', barmode='group')
            fig_cat_unit.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_tickangle=-45)
            st.plotly_chart(fig_cat_unit, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Promotion Revenue Impact")
        q_promo = df_sales.groupby(['promotion_name', 'region'])['revenue'].sum().reset_index()
        if not q_promo.empty:
            fig_promo = px.bar(q_promo, x='revenue', y='promotion_name', color='region', barmode='group', orientation='h')
            fig_promo.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_tickprefix="$")
            st.plotly_chart(fig_promo, use_container_width=True)
    with col4:
        st.empty()

# ---------------------------------------------------------
# TAB 4: Supply Chain & Returns
# ---------------------------------------------------------
with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Supplier Revenue by Country")
        q_sup_rev = df_sales.groupby(['Year', 'supplier_country'])['revenue'].sum().reset_index()
        if not q_sup_rev.empty:
            fig_sup = px.bar(q_sup_rev, x='Year', y='revenue', color='supplier_country', barmode='group')
            fig_sup.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
            st.plotly_chart(fig_sup, use_container_width=True)

    with col2:
        st.markdown("##### 📌 Monthly Refund Trend")
        q_ref_m = df_sales.groupby(['Month', 'region'])['refund_amount'].sum().reset_index()
        if not q_ref_m.empty:
            fig_ref_m = px.line(q_ref_m, x='Month', y='refund_amount', color='region', markers=True)
            fig_ref_m.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
            st.plotly_chart(fig_ref_m, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Refund Amount by Category")
        q_ref_cat = df_sales.groupby(['category', 'region'])['refund_amount'].sum().reset_index()
        q_ref_cat = q_ref_cat[q_ref_cat['refund_amount'] > 0]
        if not q_ref_cat.empty:
            fig_ref_cat = px.bar(q_ref_cat, x='category', y='refund_amount', color='region', barmode='group')
            fig_ref_cat.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$", xaxis_tickangle=-45)
            st.plotly_chart(fig_ref_cat, use_container_width=True)
    with col4:
        st.empty()

# ---------------------------------------------------------
# TAB 5: Logistics & Finance
# ---------------------------------------------------------
with tab5:
    if not df_ships.empty and not df_pays.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📌 Shipment Count by Region & Status")
            if 'region' in df_ships.columns and 'shipment_status' in df_ships.columns:
                q_ship_reg = df_ships.groupby(['region', 'shipment_status']).size().reset_index(name='shipment_count')
                if not q_ship_reg.empty:
                    fig_ship_reg = px.bar(q_ship_reg, x='shipment_status', y='shipment_count', color='region', barmode='group')
                    fig_ship_reg.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_ship_reg, use_container_width=True)
            else:
                st.info("⚠️ ข้อมูลสถานะการจัดส่ง ไม่พร้อมใช้งาน")
            
        with col2:
            st.markdown("##### 📌 Shipment Count by Store & Status")
            if 'store_name' in df_ships.columns and 'shipment_status' in df_ships.columns:
                top_stores = df_ships['store_name'].value_counts().nlargest(10).index
                df_ships_top = df_ships[df_ships['store_name'].isin(top_stores)]
                q_ship_st = df_ships_top.groupby(['store_name', 'shipment_status']).size().reset_index(name='shipment_count')
                if not q_ship_st.empty:
                    fig_ship_st = px.bar(q_ship_st, x='store_name', y='shipment_count', color='shipment_status', barmode='stack')
                    fig_ship_st.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_tickangle=-45)
                    st.plotly_chart(fig_ship_st, use_container_width=True)
            else:
                st.info("⚠️ ข้อมูลสถานะการจัดส่ง ไม่พร้อมใช้งาน")
            
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("##### 📌 Total Payment Amount by Year")
            if 'Year' in df_pays.columns and 'region' in df_pays.columns:
                q_pay_yr = df_pays.groupby(['Year', 'region'])['payment_amount'].sum().reset_index()
                if not q_pay_yr.empty:
                    fig_pay_yr = px.bar(q_pay_yr, x='Year', y='payment_amount', color='region', barmode='group')
                    fig_pay_yr.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_tickprefix="$")
                    st.plotly_chart(fig_pay_yr, use_container_width=True)
            
        with col4:
            st.markdown("##### 📌 Monthly Payment Transactions")
            if 'Month' in df_pays.columns and 'customer_city' in df_pays.columns:
                q_pay_txn = df_pays.groupby(['Month', 'customer_city']).size().reset_index(name='transaction_count')
                if not q_pay_txn.empty:
                    fig_pay_txn = px.line(q_pay_txn, x='Month', y='transaction_count', color='customer_city', markers=True)
                    fig_pay_txn.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_pay_txn, use_container_width=True)
    else:
        st.info("⚠️ ไม่พบข้อมูลที่ตรงกับเงื่อนไข หรือไม่มีข้อมูลในระบบ Logistics & Finance")