import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import datetime

# ==========================================
# 1. การตั้งค่าหน้าจอ
# ==========================================
st.set_page_config(page_title="Retail Executive Dashboard", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: 700; color: #1E88E5; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px 5px 0px 0px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #1E88E5; color: white; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Retail Executive Dashboard</div>', unsafe_allow_html=True)
st.caption("แดชบอร์ดสรุปผลการดำเนินงาน ตอบโจทย์ Business Questions 16 ข้อ")

# ==========================================
# 2. ฟังก์ชันเตรียมข้อมูล (Data Preparation)
# ==========================================
@st.cache_data
def load_data():
    """
    จำลองข้อมูลที่ผ่านการ Join มาแล้วจาก Fact & Dimension Tables
    (ในใช้งานจริง สามารถดึงจาก DuckDB หรือ Merge CSV 12 ไฟล์ที่นี่ได้เลย)
    """
    np.random.seed(42)
    n_rows = 5000
    dates = pd.date_range(start="2022-01-01", end="2024-12-31", freq='H')
    
    df = pd.DataFrame({
        'Order_ID': np.arange(1, n_rows + 1),
        'Order_Date': np.random.choice(dates, n_rows),
        'Customer_ID': np.random.randint(100, 500, n_rows),
        'Customer_City': np.random.choice(['Bangkok', 'Chiang Mai', 'Phuket', 'Khon Kaen', 'Pattaya'], n_rows),
        'Region': np.random.choice(['North', 'South', 'Central', 'Northeast'], n_rows),
        'Category': np.random.choice(['Electronics', 'Clothing', 'Furniture', 'Food', 'Toys'], n_rows),
        'Revenue': np.random.uniform(500, 10000, n_rows),
        'Units_Sold': np.random.randint(1, 20, n_rows),
        'Promotion_Name': np.random.choice(['No Promo', 'Summer Sale', 'Black Friday', 'New Year'], n_rows, p=[0.5, 0.2, 0.1, 0.2]),
        'Supplier_Country': np.random.choice(['Thailand', 'China', 'Japan', 'USA'], n_rows),
        'Refund_Amount': np.random.choice([0, 0, 0, 500, 1000, 2000], n_rows) # ส่วนใหญ่ไม่มีการคืนเงิน
    })
    
    # Extract Date Parts สำหรับการวิเคราะห์
    df['Year'] = df['Order_Date'].dt.year
    df['Quarter'] = 'Q' + df['Order_Date'].dt.quarter.astype(str)
    df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)
    df['Month_Num'] = df['Order_Date'].dt.month
    return df

df = load_data()

# ==========================================
# 3. Sidebar Filters (ตัวกรองข้อมูลหลัก)
# ==========================================
st.sidebar.header("🎯 ตัวกรองข้อมูล (Filters)")

# Filter: Year
year_list = sorted(df['Year'].unique().tolist())
selected_years = st.sidebar.multiselect("เลือกปี (Year)", year_list, default=year_list)

# Filter: Region
region_list = sorted(df['Region'].unique().tolist())
selected_regions = st.sidebar.multiselect("เลือกภูมิภาค (Region)", region_list, default=region_list)

# Filter: Category
category_list = sorted(df['Category'].unique().tolist())
selected_categories = st.sidebar.multiselect("เลือกหมวดหมู่สินค้า (Category)", category_list, default=category_list)

# Apply Filters
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Region'].isin(selected_regions)) &
    (df['Category'].isin(selected_categories))
]

if filtered_df.empty:
    st.warning("⚠️ ไม่มีข้อมูลตามเงื่อนไขที่เลือก กรุณาปรับ Filter ใหม่")
    st.stop()

# ==========================================
# 4. KPI Banners (สรุปตัวเลขด้านบน)
# ==========================================
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = filtered_df['Revenue'].sum()
total_orders = filtered_df['Order_ID'].nunique()
aov = total_revenue / total_orders if total_orders > 0 else 0
total_customers = filtered_df['Customer_ID'].nunique()
total_refund = filtered_df['Refund_Amount'].sum()

col1.metric("💰 Total Revenue", f"฿{total_revenue:,.0f}")
col2.metric("📦 Total Orders", f"{total_orders:,}")
col3.metric("🛒 AOV (Avg Order Value)", f"฿{aov:,.0f}")
col4.metric("👥 Active Customers", f"{total_customers:,}")
col5.metric("🔄 Total Refunds", f"฿{total_refund:,.0f}")

st.markdown("---")

# ==========================================
# 5. Dashboard Tabs (จัดกลุ่มคำถาม 16 ข้อ)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. ยอดขายและพื้นที่ (Sales & Region)", 
    "🛍️ 2. สินค้าและลูกค้า (Products & Customers)", 
    "🤝 3. โปรโมชันและซัพพลายเออร์ (Promos & Suppliers)", 
    "🔙 4. การคืนเงิน (Returns)"
])

# ---------------------------------------------------------
# TAB 1: ยอดขายและพื้นที่ (Q1, Q2, Q7)
# ---------------------------------------------------------
with tab1:
    st.subheader("ยอดขายตามภูมิภาคและช่วงเวลา (Sales Performance)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Q1: ภูมิภาคใดมียอดขายรวมสูงสุดในแต่ละปี?
        st.markdown("**Q1: ยอดขายรวมของแต่ละภูมิภาครายปี**")
        df_q1 = filtered_df.groupby(['Year', 'Region'])['Revenue'].sum().reset_index()
        fig_q1 = px.bar(df_q1, x='Year', y='Revenue', color='Region', barmode='group')
        st.plotly_chart(fig_q1, use_container_width=True)
        
    with col_b:
        # Q7: ภูมิภาคใดมียอดขายสูงสุดในแต่ละไตรมาสของแต่ละปี?
        st.markdown("**Q7: ยอดขายรายไตรมาสแบ่งตามภูมิภาค**")
        df_q7 = filtered_df.groupby(['Year', 'Quarter', 'Region'])['Revenue'].sum().reset_index()
        df_q7['Year_Q'] = df_q7['Year'].astype(str) + "-" + df_q7['Quarter']
        fig_q7 = px.line(df_q7, x='Year_Q', y='Revenue', color='Region', markers=True)
        st.plotly_chart(fig_q7, use_container_width=True)

    # Q2: แต่ละภูมิภาคมียอดขายรวมเท่าไรในแต่ละเดือน?
    st.markdown("**Q2: แนวโน้มยอดขายรายเดือนของแต่ละภูมิภาค**")
    df_q2 = filtered_df.groupby(['Month', 'Region'])['Revenue'].sum().reset_index()
    fig_q2 = px.area(df_q2, x='Month', y='Revenue', color='Region')
    st.plotly_chart(fig_q2, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: สินค้าและลูกค้า (Q3, Q4, Q5, Q6, Q8, Q9, Q10)
# ---------------------------------------------------------
with tab2:
    st.subheader("พฤติกรรมลูกค้าและการซื้อสินค้า (Products & Customers Analysis)")
    
    col_c, col_d = st.columns(2)
    with col_c:
        # Q3 & Q4: หมวดหมู่สินค้าและจำนวน Units Sold
        st.markdown("**Q3 & Q4: ยอดขายและจำนวนสินค้า(Units Sold) ตามหมวดหมู่และภูมิภาค**")
        df_q3 = filtered_df.groupby(['Category', 'Region'])[['Revenue', 'Units_Sold']].sum().reset_index()
        fig_q3 = px.scatter(df_q3, x='Revenue', y='Units_Sold', color='Region', size='Revenue', hover_data=['Category'])
        st.plotly_chart(fig_q3, use_container_width=True)
        
    with col_d:
        # Q8: ลูกค้าในเมืองใดสร้างรายได้สูงสุดในแต่ละปี?
        st.markdown("**Q8: รายได้สูงสุดจากเมืองของลูกค้ารายปี**")
        df_q8 = filtered_df.groupby(['Year', 'Customer_City'])['Revenue'].sum().reset_index()
        fig_q8 = px.bar(df_q8, x='Customer_City', y='Revenue', color='Year', barmode='group')
        st.plotly_chart(fig_q8, use_container_width=True)

    col_e, col_f = st.columns(2)
    with col_e:
        # Q5: จำนวน Order ตาม Region + Month
        st.markdown("**Q5: จำนวนคำสั่งซื้อ (Order Count) รายเดือนแบ่งตามภูมิภาค**")
        df_q5 = filtered_df.groupby(['Month', 'Region'])['Order_ID'].nunique().reset_index(name='Order_Count')
        fig_q5 = px.line(df_q5, x='Month', y='Order_Count', color='Region', markers=True)
        st.plotly_chart(fig_q5, use_container_width=True)
        
    with col_f:
        # Q6 & Q10: AOV ตามภูมิภาคและเมือง
        st.markdown("**Q6 & Q10: มูลค่าเฉลี่ยต่อคำสั่งซื้อ (AOV) แยกตามเมืองลูกค้า**")
        df_q10_rev = filtered_df.groupby(['Customer_City'])['Revenue'].sum()
        df_q10_ord = filtered_df.groupby(['Customer_City'])['Order_ID'].nunique()
        df_q10 = (df_q10_rev / df_q10_ord).reset_index(name='AOV').sort_values('AOV', ascending=False)
        fig_q10 = px.bar(df_q10, x='AOV', y='Customer_City', orientation='h', color='AOV', color_continuous_scale='Blues')
        st.plotly_chart(fig_q10, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: โปรโมชันและซัพพลายเออร์ (Q11, Q12, Q13, Q14, Q16)
# ---------------------------------------------------------
with tab3:
    st.subheader("ประสิทธิภาพพันธมิตรทางธุรกิจและแคมเปญ (Partners & Promotions)")
    
    col_g, col_h = st.columns(2)
    with col_g:
        # Q11 & Q12: ยอดขายตาม Promotion
        st.markdown("**Q11 & Q12: ยอดขายจากแต่ละโปรโมชัน (Promotion Revenue)**")
        df_q11 = filtered_df.groupby(['Promotion_Name', 'Region'])['Revenue'].sum().reset_index()
        fig_q11 = px.bar(df_q11, x='Promotion_Name', y='Revenue', color='Region')
        st.plotly_chart(fig_q11, use_container_width=True)
        
    with col_h:
        # Q13 & Q14: ยอดขายตามประเทศของ Supplier
        st.markdown("**Q13 & Q14: รายได้จำแนกตามประเทศของซัพพลายเออร์ (Supplier Country)**")
        df_q13 = filtered_df.groupby(['Supplier_Country', 'Year'])['Revenue'].sum().reset_index()
        fig_q13 = px.pie(df_q13, names='Supplier_Country', values='Revenue', hole=0.4)
        st.plotly_chart(fig_q13, use_container_width=True)

    # Q16: Supplier แต่ละประเทศมีรายได้จากแต่ละหมวดหมู่เท่าไร
    st.markdown("**Q16: สัดส่วนรายได้จากหมวดหมู่สินค้าจำแนกตามประเทศ Supplier**")
    df_q16 = filtered_df.groupby(['Supplier_Country', 'Category'])['Revenue'].sum().reset_index()
    fig_q16 = px.sunburst(df_q16, path=['Supplier_Country', 'Category'], values='Revenue')
    st.plotly_chart(fig_q16, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: การคืนเงิน (Q15)
# ---------------------------------------------------------
with tab4:
    st.subheader("การคืนเงินและการคืนสินค้า (Refund & Return Analysis)")
    
    col_i, col_j = st.columns([2, 1])
    with col_i:
        # Q15: ภูมิภาคใดมีมูลค่า Refund สูงสุดในแต่ละเดือน
        st.markdown("**Q15: มูลค่าการคืนเงิน (Refund Amount) รายเดือนแบ่งตามภูมิภาค**")
        df_q15 = filtered_df[filtered_df['Refund_Amount'] > 0]
        if not df_q15.empty:
            df_q15_group = df_q15.groupby(['Month', 'Region'])['Refund_Amount'].sum().reset_index()
            fig_q15 = px.line(df_q15_group, x='Month', y='Refund_Amount', color='Region', markers=True, text='Refund_Amount')
            fig_q15.update_traces(textposition="top center")
            st.plotly_chart(fig_q15, use_container_width=True)
        else:
            st.info("ไม่มีข้อมูลการคืนเงินในช่วงเวลาที่เลือก")
            
    with col_j:
        st.markdown("**ตารางสรุป Refund ตามภูมิภาค**")
        if not df_q15.empty:
            df_refund_table = df_q15.groupby('Region')['Refund_Amount'].sum().reset_index().sort_values('Refund_Amount', ascending=False)
            st.dataframe(df_refund_table, use_container_width=True, hide_index=True)
        else:
            st.write("-")