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
        padding: 20px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .main-title { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-subtitle { font-size: 1rem; color: #94A3B8; margin-top: 8px; line-height: 1.5; }
    
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
        "dim_supplier": "stg_suppliers", "dim_payment": "stg_payments",
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
@st.cache_data(ttl=600)
def load_dashboard_data():
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
    if not df.empty:
        df['region'] = df['region'].str.strip()
        df['category'] = df['category'].str.strip()
        df['customer_city'] = df['customer_city'].str.strip()
        df['supplier_country'] = df['supplier_country'].str.strip()

        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        df['Year'] = df['order_date'].dt.year.fillna(0).astype(int).astype(str)
        df['Quarter'] = 'Q' + df['order_date'].dt.quarter.fillna(0).astype(int).astype(str)
        df['Month'] = df['order_date'].dt.to_period('M').astype(str)
        df['Year_Q'] = df['Year'] + "-" + df['Quarter']
    return df

df_raw = load_dashboard_data()

if df_raw.empty:
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
# 3. Main Header & High-Level Metrics
# =========================================================
st.markdown("""
    <div class="main-header">
        <div class="main-title">📈 Retail Analytics Dashboard (ระบบวิเคราะห์ข้อมูลการขายปลีก)</div>
        <div class="main-subtitle">
           ระบบวิเคราะห์เชิงลึกข้อมูลการขาย สิทธิประโยชน์ ลูกค้า และห่วงโซ่อุปทาน (Enterprise Business Intelligence)
""", unsafe_allow_html=True)

# ฟังก์ชันสำหรับย่อตัวเลข (M = หลักล้าน, K = หลักพัน)
def format_metric(num):
    if num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return f"{num:,.0f}"

tot_rev = df_raw['revenue'].sum()
tot_ord = df_raw['order_id'].nunique()
tot_units = df_raw['units_sold'].sum()
aov_val = tot_rev / tot_ord if tot_ord > 0 else 0
tot_cust = df_raw['customer_id'].nunique()
tot_ref = df_raw['refund_amount'].sum()

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Revenue", f"${format_metric(tot_rev)}")
m2.metric("Orders", f"{format_metric(tot_ord)}")
m3.metric("Units Sold", f"{format_metric(tot_units)}")
m4.metric("AOV", f"${format_metric(aov_val)}")
m5.metric("Active Customers", f"{format_metric(tot_cust)}")
m6.metric("Total Refunds", f"${format_metric(tot_ref)}")

st.markdown("<br>", unsafe_allow_html=True)

# Master Filter Options
all_regions = ["ทั้งหมด (All Regions)"] + sorted(df_raw['region'].unique().tolist())
all_years = ["ทุกปี (All Years)"] + sorted(df_raw['Year'].unique().tolist())
all_countries = ["ทุกประเทศ (All)"] + sorted(df_raw['supplier_country'].unique().tolist())
all_cities = sorted(df_raw['customer_city'].unique().tolist())
all_cats_sorted = sort_categories(df_raw['category'].unique().tolist())

# =========================================================
# 4. Core Business Domain Tabs
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Revenue Trends",
    "👥 Customer Insights",
    "📦 Product Performance",
    "🚚 Supply Chain"
])

# ---------------------------------------------------------
# TAB 1: Sales, Revenue & Growth
# ---------------------------------------------------------
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Monthly Revenue Trend")
        f_reg1 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t1_c1")
        df_c1 = df_raw.copy()
        if f_reg1 != "ทั้งหมด (All Regions)":
            df_c1 = df_c1[df_c1['region'] == f_reg1]
            
        q1 = df_c1.groupby(['Month', 'region'])['revenue'].sum().reset_index()
        fig1 = px.line(q1, x='Month', y='revenue', color='region', markers=True, title="Monthly Revenue")
        fig1.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.markdown("##### 📌 Annual Revenue Breakdown")
        f_reg2 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t1_c2")
        df_c2 = df_raw.copy()
        if f_reg2 != "ทั้งหมด (All Regions)":
            df_c2 = df_c2[df_c2['region'] == f_reg2]
            
        q2 = df_c2.groupby(['Year', 'region'])['revenue'].sum().reset_index()
        fig2 = px.bar(q2, x='Year', y='revenue', color='region', barmode='group', text_auto='.2s', title="Annual Revenue")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig2, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Quarterly Revenue")
        f_yr3 = st.selectbox("เลือกปี:", all_years, key="sb_t1_c3")
        df_c3 = df_raw.copy()
        if f_yr3 != "ทุกปี (All Years)":
            df_c3 = df_c3[df_c3['Year'] == f_yr3]
            
        q3 = df_c3.groupby(['Year_Q', 'region'])['revenue'].sum().reset_index()
        fig3 = px.bar(q3, x='Year_Q', y='revenue', color='region', barmode='group', title="Quarterly Revenue")
        fig3.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig3, width="stretch")

    with col4:
        st.markdown("##### 📌 Quarterly AOV Trend")
        f_reg4 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t1_c4")
        df_c4 = df_raw.copy()
        if f_reg4 != "ทั้งหมด (All Regions)":
            df_c4 = df_c4[df_c4['region'] == f_reg4]
            
        q4 = df_c4.groupby(['Year_Q', 'region']).agg(rev=('revenue', 'sum'), ord=('order_id', 'nunique')).reset_index()
        q4['AOV'] = q4['rev'] / q4['ord']
        fig4 = px.line(q4, x='Year_Q', y='AOV', color='region', markers=True, title="Quarterly AOV")
        fig4.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig4, width="stretch")

# ---------------------------------------------------------
# TAB 2: Customer & Regional Analysis
# ---------------------------------------------------------
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Customer Cities Revenue")
        c1_sub1, c1_sub2 = st.columns(2)
        with c1_sub1:
            f_yr_t2_1 = st.selectbox("เลือกปี:", all_years, key="sb_t2_c1_y")
        with c1_sub2:
            f_city_t2_1 = st.multiselect("เลือกเมืองเปรียบเทียบ:", all_cities, default=all_cities[:4], key="ms_t2_c1")
            
        df_t2_1 = df_raw.copy()
        if f_yr_t2_1 != "ทุกปี (All Years)":
            df_t2_1 = df_t2_1[df_t2_1['Year'] == f_yr_t2_1]
        if f_city_t2_1:
            df_t2_1 = df_t2_1[df_t2_1['customer_city'].isin(f_city_t2_1)]
            
        q_t2_1 = df_t2_1.groupby(['customer_city', 'Year'])['revenue'].sum().reset_index()
        fig_t2_1 = px.bar(q_t2_1, x='revenue', y='customer_city', color='Year', barmode='group', orientation='h', title="Revenue by Selected Cities")
        fig_t2_1.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickprefix="$", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_t2_1, width="stretch")

    with col2:
        st.markdown("##### 📌 Monthly Active Purchasers")
        f_reg_t2_2 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t2_c2")
        df_t2_2 = df_raw.copy()
        if f_reg_t2_2 != "ทั้งหมด (All Regions)":
            df_t2_2 = df_t2_2[df_t2_2['region'] == f_reg_t2_2]
            
        q_t2_2 = df_t2_2.groupby(['Month', 'region'])['customer_id'].nunique().reset_index(name='active_customers')
        fig_t2_2 = px.line(q_t2_2, x='Month', y='active_customers', color='region', markers=True, title="Active Purchasers Trend")
        fig_t2_2.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_t2_2, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Monthly Order Volume")
        f_reg_t2_3 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t2_c3")
        df_t2_3 = df_raw.copy()
        if f_reg_t2_3 != "ทั้งหมด (All Regions)":
            df_t2_3 = df_t2_3[df_t2_3['region'] == f_reg_t2_3]
            
        q_t2_3 = df_t2_3.groupby(['Month', 'region'])['order_id'].nunique().reset_index(name='order_count')
        fig_t2_3 = px.bar(q_t2_3, x='Month', y='order_count', color='region', barmode='group', title="Monthly Orders")
        fig_t2_3.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_t2_3, width="stretch")

    with col4:
        st.markdown("##### 📌 Customer AOV by City")
        c4_sub1, c4_sub2 = st.columns(2)
        with c4_sub1:
            f_yr_t2_4 = st.selectbox("เลือกปี (AOV):", all_years, key="sb_t2_c4_y")
        with c4_sub2:
            f_city_t2_4 = st.multiselect("เลือกเมือง (AOV):", all_cities, default=all_cities[:4], key="ms_t2_c4")
        
        df_t2_4 = df_raw.copy()
        if f_yr_t2_4 != "ทุกปี (All Years)":
            df_t2_4 = df_t2_4[df_t2_4['Year'] == f_yr_t2_4]
        if f_city_t2_4:
            df_t2_4 = df_t2_4[df_t2_4['customer_city'].isin(f_city_t2_4)]
            
        q_t2_4 = df_t2_4.groupby(['customer_city', 'Year']).agg(rev=('revenue', 'sum'), ord=('order_id', 'nunique')).reset_index()
        q_t2_4['Customer_AOV'] = q_t2_4['rev'] / q_t2_4['ord']
        
        fig_t2_4 = px.bar(q_t2_4, x='customer_city', y='Customer_AOV', color='Year', barmode='group', title="AOV by Selected Cities")
        fig_t2_4.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig_t2_4, width="stretch")

# ---------------------------------------------------------
# TAB 3: Product & Promotion Performance
# ---------------------------------------------------------
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Category Revenue by Region")
        c3_sub1, c3_sub2 = st.columns(2)
        with c3_sub1:
            f_reg_t3_1 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t3_c1_r")
        with c3_sub2:
            f_cat_t3_1 = st.multiselect("เลือกหมวดหมู่:", all_cats_sorted, default=all_cats_sorted[:5], key="ms_t3_c1")
            
        df_t3_1 = df_raw.copy()
        if f_reg_t3_1 != "ทั้งหมด (All Regions)":
            df_t3_1 = df_t3_1[df_t3_1['region'] == f_reg_t3_1]
        if f_cat_t3_1:
            df_t3_1 = df_t3_1[df_t3_1['category'].isin(f_cat_t3_1)]
            
        q_t3_1 = df_t3_1.groupby(['category', 'region'])['revenue'].sum().reset_index()
        q_t3_1['cat_sorted'] = pd.Categorical(q_t3_1['category'], categories=all_cats_sorted, ordered=True)
        q_t3_1 = q_t3_1.sort_values('cat_sorted')

        fig_t3_1 = px.bar(q_t3_1, x='category', y='revenue', color='region', barmode='group', title="Revenue by Selected Categories")
        fig_t3_1.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$", xaxis_tickangle=-45)
        st.plotly_chart(fig_t3_1, width="stretch")

    with col2:
        st.markdown("##### 📌 Units Sold by Category")
        c3_sub3, c3_sub4 = st.columns(2)
        with c3_sub3:
            f_reg_t3_2 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t3_c2_r")
        with c3_sub4:
            f_cat_t3_2 = st.multiselect("เลือกหมวดหมู่:", all_cats_sorted, default=all_cats_sorted[:5], key="ms_t3_c2")
            
        df_t3_2 = df_raw.copy()
        if f_reg_t3_2 != "ทั้งหมด (All Regions)":
            df_t3_2 = df_t3_2[df_t3_2['region'] == f_reg_t3_2]
        if f_cat_t3_2:
            df_t3_2 = df_t3_2[df_t3_2['category'].isin(f_cat_t3_2)]
            
        q_t3_2 = df_t3_2.groupby(['category', 'region'])['units_sold'].sum().reset_index()
        q_t3_2['cat_sorted'] = pd.Categorical(q_t3_2['category'], categories=all_cats_sorted, ordered=True)
        q_t3_2 = q_t3_2.sort_values('cat_sorted')

        fig_t3_2 = px.bar(q_t3_2, x='category', y='units_sold', color='region', barmode='group', title="Units Sold by Selected Categories")
        fig_t3_2.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-45)
        st.plotly_chart(fig_t3_2, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Promotion Revenue Impact")
        f_reg_t3_3 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t3_c3")
        df_t3_3 = df_raw.copy()
        if f_reg_t3_3 != "ทั้งหมด (All Regions)":
            df_t3_3 = df_t3_3[df_t3_3['region'] == f_reg_t3_3]
            
        q_t3_3 = df_t3_3.groupby(['promotion_name', 'region'])['revenue'].sum().reset_index()
        fig_t3_3 = px.bar(q_t3_3, x='revenue', y='promotion_name', color='region', barmode='group', orientation='h', title="Promotion Revenue")
        fig_t3_3.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickprefix="$")
        st.plotly_chart(fig_t3_3, width="stretch")

    with col4:
        st.markdown("##### 📌 Discount Tier Performance")
        f_yr_t3_4 = st.selectbox("เลือกปี:", all_years, key="sb_t3_c4")
        df_t3_4 = df_raw.copy()
        if f_yr_t3_4 != "ทุกปี (All Years)":
            df_t3_4 = df_t3_4[df_t3_4['Year'] == f_yr_t3_4]
            
        q_t3_4 = df_t3_4.groupby(['Year', 'promotion_name'])['revenue'].sum().reset_index()
        fig_t3_4 = px.bar(q_t3_4, x='Year', y='revenue', color='promotion_name', barmode='group', title="Discount Tier Revenue")
        fig_t3_4.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig_t3_4, width="stretch")

# ---------------------------------------------------------
# TAB 4: Supply Chain, Returns & Logistics
# ---------------------------------------------------------
with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Supplier Revenue by Country")
        f_cnt_t4_1 = st.selectbox("เลือกประเทศ Supplier:", all_countries, key="sb_t4_c1")
        df_t4_1 = df_raw.copy()
        if f_cnt_t4_1 != "ทุกประเทศ (All)":
            df_t4_1 = df_t4_1[df_t4_1['supplier_country'] == f_cnt_t4_1]
            
        q_t4_1 = df_t4_1.groupby(['Year', 'supplier_country'])['revenue'].sum().reset_index()
        fig_t4_1 = px.bar(q_t4_1, x='Year', y='revenue', color='supplier_country', barmode='group', title="Supplier Revenue")
        fig_t4_1.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig_t4_1, width="stretch")

    with col2:
        st.markdown("##### 📌 Supplier Revenue by Region")
        f_reg_t4_2 = st.selectbox("เลือกภูมิภาคร้านค้า:", all_regions, key="sb_t4_c2")
        df_t4_2 = df_raw.copy()
        if f_reg_t4_2 != "ทั้งหมด (All Regions)":
            df_t4_2 = df_t4_2[df_t4_2['region'] == f_reg_t4_2]
            
        q_t4_2 = df_t4_2.groupby(['supplier_country', 'region'])['revenue'].sum().reset_index()
        fig_t4_2 = px.bar(q_t4_2, x='supplier_country', y='revenue', color='region', barmode='group', title="Supplier Share by Region")
        fig_t4_2.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        fig_t4_2.update_traces(hovertemplate='Region: %{fullData.name}<br>Revenue: $%{y:,.2f}')
        st.plotly_chart(fig_t4_2, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 📌 Supplier Revenue by Category")
        c4_sub1, c4_sub2 = st.columns(2)
        with c4_sub1:
            f_cnt_t4_3 = st.selectbox("ประเทศ Supplier:", all_countries, key="sb_t4_c3_c")
        with c4_sub2:
            f_cat_t4_3 = st.multiselect("เลือกหมวดหมู่:", all_cats_sorted, default=all_cats_sorted[:5], key="ms_t4_c3")
            
        df_t4_3 = df_raw.copy()
        if f_cnt_t4_3 != "ทุกประเทศ (All)":
            df_t4_3 = df_t4_3[df_t4_3['supplier_country'] == f_cnt_t4_3]
        if f_cat_t4_3:
            df_t4_3 = df_t4_3[df_t4_3['category'].isin(f_cat_t4_3)]
            
        q_t4_3 = df_t4_3.groupby(['supplier_country', 'category'])['revenue'].sum().reset_index()
        fig_t4_3 = px.bar(q_t4_3, x='supplier_country', y='revenue', color='category', barmode='group', title="Supplier Revenue by Categories")
        fig_t4_3.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig_t4_3, width="stretch")

    with col4:
        st.markdown("##### 📌 Monthly Refund Trend")
        f_reg_t4_4 = st.selectbox("เลือกภูมิภาค:", all_regions, key="sb_t4_c4")
        df_t4_4 = df_raw.copy()
        if f_reg_t4_4 != "ทั้งหมด (All Regions)":
            df_t4_4 = df_t4_4[df_t4_4['region'] == f_reg_t4_4]
            
        q_t4_4 = df_t4_4.groupby(['Month', 'region'])['refund_amount'].sum().reset_index()
        fig_t4_4 = px.line(q_t4_4, x='Month', y='refund_amount', color='region', markers=True, title="Monthly Refunds")
        fig_t4_4.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis_tickprefix="$")
        st.plotly_chart(fig_t4_4, width="stretch")