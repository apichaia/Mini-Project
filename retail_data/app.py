import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="retail_data DW Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "dev.duckdb"

# ---------------------------------------------------------
# Deduplicated Tables List
# ---------------------------------------------------------
STAGING_TABLES = list(dict.fromkeys([
    "stg_categories",
    "stg_customers",
    "stg_employees",
    "stg_order_items",
    "stg_orders",
    "stg_payments",
    "stg_products",
    "stg_promotions",
    "stg_returns",
    "stg_shipments",
    "stg_stores",
    "stg_suppliers",
]))

DIMENSION_TABLES = list(dict.fromkeys([
    "dim_customer",
    "dim_date",
    "dim_employee",
    "dim_product",
    "dim_promotion",
    "dim_store",
    "dim_supplier",
    "dim_categories",
]))

FACT_TABLES = list(dict.fromkeys([
    "fact_payments",
    "fact_returns",
    "fact_sales",
    "fact_shipments",
]))

@st.cache_resource
def get_connection():
    if not DB_PATH.exists():
        return None
    try:
        return duckdb.connect(str(DB_PATH), read_only=True)
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def run_query(query):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        return conn.execute(query).fetch_df()
    except Exception as e:
        st.error(f"Error running query: {e}")
        return pd.DataFrame()

if not DB_PATH.exists():
    st.error(f"❌ ไม่พบไฟล์ dev.duckdb\n\nPath: `{DB_PATH}`")
    st.stop()

tables_df = run_query(
    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
)

if tables_df.empty:
    st.error("❌ ไม่พบตารางใน Schema main")
    st.stop()

db_tables = set(tables_df["table_name"].tolist())

available_staging = [t for t in STAGING_TABLES if t in db_tables]
available_dimension = [t for t in DIMENSION_TABLES if t in db_tables]
available_fact = [t for t in FACT_TABLES if t in db_tables]
all_tables = available_staging + available_dimension + available_fact

# ---------------------------------------------------------
# Cached Row Counter for performance
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def get_row_count(table_name):
    conn = get_connection()
    if conn is None:
        return 0
    try:
        safe_table = table_name.replace('"', '""')
        result = conn.execute(f'SELECT COUNT(*) FROM main."{safe_table}"').fetchone()
        return result[0] if result else 0
    except Exception:
        return 0

table_stats = []
for table in all_tables:
    if table in available_staging:
        table_type = "Staging"
    elif table in available_dimension:
        table_type = "Dimension"
    elif table in available_fact:
        table_type = "Fact"
    else:
        table_type = "Other"

    table_stats.append({
        "type": table_type,
        "table_name": table,
        "row_count": get_row_count(table)
    })

stats_df = pd.DataFrame(table_stats)

# ---------------------------------------------------------
# UI & Styling
# ---------------------------------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #FF69B4;
    margin-bottom: 0.2rem;
}
.subtitle {
    font-size: 1.1rem;
    color: #FFC0CB;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 retail_data</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Inspect and preview Staging, Dimension and Fact tables in dev.duckdb</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Dynamic Sidebar Metrics
# ---------------------------------------------------------
st.sidebar.title("🗂️ Table Browser")

table_groups = {
    "Staging Tables": available_staging,
    "Dimension Tables": available_dimension,
    "Fact Tables": available_fact,
    "All Tables": all_tables
}

selected_group = st.sidebar.selectbox("Select Table Group", list(table_groups.keys()))
selected_group_tables = table_groups[selected_group]
selected_table = st.sidebar.selectbox("Select a table to inspect", selected_group_tables) if selected_group_tables else None

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Stats")
st.sidebar.markdown(f"**Staging Tables:** {len(available_staging)} / {len(STAGING_TABLES)}")
st.sidebar.markdown(f"**Dimension Tables:** {len(available_dimension)} / {len(DIMENSION_TABLES)}")

if not stats_df.empty:
    total_rows = stats_df["row_count"].sum()
    st.sidebar.markdown(f"**Total Rows:** {int(total_rows):,}")

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📋 Database Schema & Overview", "🔍 Data Viewer & Metadata"])

with tab1:
    st.subheader("Database Tables Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Staging Tables", f"{len(available_staging)} / {len(STAGING_TABLES)}")
    col2.metric("Dimension Tables", f"{len(available_dimension)} / {len(DIMENSION_TABLES)}")
    col3.metric("Fact Tables", f"{len(available_fact)} / {len(FACT_TABLES)}")
    col4.metric("Total Tables", f"{len(all_tables)} / {len(STAGING_TABLES) + len(DIMENSION_TABLES) + len(FACT_TABLES)}")

    st.markdown("### Table List & Record Counts")
    if not stats_df.empty:
        display_df = stats_df.rename(columns={"type": "Type", "table_name": "Table Name", "row_count": "Row Count"})
        st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    if selected_table is None:
        st.info("กรุณาเลือกตารางจาก Sidebar")
    else:
        st.subheader(f"Table Details: `{selected_table}`")
        
        table_type = "Staging" if selected_table in available_staging else "Dimension" if selected_table in available_dimension else "Fact" if selected_table in available_fact else "Unknown"
        
        cols_df = run_query(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'main' AND table_name = '{selected_table}'
            ORDER BY ordinal_position
        """)
        
        row_count = get_row_count(selected_table)
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write("**Table Summary**")
            st.write(f"- **Type:** `{table_type}`")
            st.write(f"- **Rows:** `{row_count:,}`")
            st.write(f"- **Columns:** `{len(cols_df)}`")
            st.markdown("---")
            st.write("**Columns & Types**")
            if not cols_df.empty:
                st.dataframe(cols_df.rename(columns={"column_name": "Column", "data_type": "Type"}), use_container_width=True, hide_index=True)

        with col2:
            st.write("**Data Preview (First 100 rows)**")
            safe_table = selected_table.replace('"', '""')
            data_df = run_query(f'SELECT * FROM main."{safe_table}" LIMIT 100')
            
            if not data_df.empty:
                st.dataframe(data_df, use_container_width=True, hide_index=True)
                csv_data = data_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"📥 Download `{selected_table}` as CSV",
                    data=csv_data,
                    file_name=f"{selected_table}_preview.csv",
                    mime="text/csv"
                )
            else:
                st.info("ตารางนี้ไม่มีข้อมูล")

st.markdown("---")
st.caption("retail_data DW Explorer • DuckDB + Pandas + Streamlit")
