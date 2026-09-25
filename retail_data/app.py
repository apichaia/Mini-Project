import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

# =========================================================
# Page Configuration
# =========================================================
st.set_page_config(
    page_title="retail_data DW Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "dev.duckdb"


# =========================================================
# Expected Tables
# =========================================================

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
    "dim_payment",
]))

FACT_TABLES = list(dict.fromkeys([
    "fact_payments",
    "fact_returns",
    "fact_sales",
    "fact_shipments",
]))

ALL_EXPECTED_TABLES = (
    STAGING_TABLES
    + DIMENSION_TABLES
    + FACT_TABLES
)


# =========================================================
# Database Connection
# =========================================================

@st.cache_resource
def get_connection():
    if not DB_PATH.exists():
        return None

    try:
        return duckdb.connect(
            str(DB_PATH),
            read_only=True
        )
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


# =========================================================
# Check Database
# =========================================================

if not DB_PATH.exists():
    st.error(
        f"❌ ไม่พบไฟล์ dev.duckdb\n\n"
        f"Path: `{DB_PATH}`"
    )
    st.stop()


# =========================================================
# Get Actual Tables From DuckDB
# =========================================================

tables_df = run_query("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main'
    ORDER BY table_name
""")


if tables_df.empty:
    st.error("❌ ไม่พบตารางใน Schema main")
    st.stop()


db_tables = set(
    tables_df["table_name"].tolist()
)


# =========================================================
# Table Status
# =========================================================

def get_table_status(table_name):
    if table_name in db_tables:
        return "Available"
    return "Missing"


def get_table_type(table_name):

    if table_name in STAGING_TABLES:
        return "Staging"

    if table_name in DIMENSION_TABLES:
        return "Dimension"

    if table_name in FACT_TABLES:
        return "Fact"

    return "Other"


# =========================================================
# Row Counter
# =========================================================

@st.cache_data(ttl=300)
def get_row_count(table_name):

    if table_name not in db_tables:
        return 0

    conn = get_connection()

    if conn is None:
        return 0

    try:

        safe_table = table_name.replace('"', '""')

        result = conn.execute(
            f'SELECT COUNT(*) '
            f'FROM main."{safe_table}"'
        ).fetchone()

        return result[0] if result else 0

    except Exception:
        return 0


# =========================================================
# Build Complete Table Statistics
# =========================================================

table_stats = []

for table in ALL_EXPECTED_TABLES:

    table_type = get_table_type(table)
    status = get_table_status(table)

    row_count = (
        get_row_count(table)
        if status == "Available"
        else None
    )

    table_stats.append({
        "Type": table_type,
        "Table Name": table,
        "Status": status,
        "Row Count": row_count
    })


stats_df = pd.DataFrame(table_stats)


# =========================================================
# Statistics
# =========================================================

staging_available = sum(
    table in db_tables
    for table in STAGING_TABLES
)

dimension_available = sum(
    table in db_tables
    for table in DIMENSION_TABLES
)

fact_available = sum(
    table in db_tables
    for table in FACT_TABLES
)

total_available = sum(
    table in db_tables
    for table in ALL_EXPECTED_TABLES
)

total_expected = len(ALL_EXPECTED_TABLES)

missing_tables = [
    table
    for table in ALL_EXPECTED_TABLES
    if table not in db_tables
]


# =========================================================
# UI Styling
# =========================================================

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

.missing-table {
    color: #ff6b6b;
    font-weight: 600;
}

.available-table {
    color: #51cf66;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="main-title">📊 retail_data</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Inspect and preview Staging, Dimension and Fact tables in dev.duckdb'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# Sidebar
# =========================================================

st.sidebar.title("🗂️ Table Browser")


table_groups = {
    "Staging Tables": STAGING_TABLES,
    "Dimension Tables": DIMENSION_TABLES,
    "Fact Tables": FACT_TABLES,
    "All Tables": ALL_EXPECTED_TABLES
}


selected_group = st.sidebar.selectbox(
    "Select Table Group",
    list(table_groups.keys())
)


selected_group_tables = table_groups[selected_group]


selected_table = st.sidebar.selectbox(
    "Select a table to inspect",
    selected_group_tables
)


st.sidebar.markdown("---")


# =========================================================
# Sidebar Quick Stats
# =========================================================

st.sidebar.subheader("Quick Stats")

st.sidebar.markdown(
    f"**Staging Tables:** "
    f"{staging_available} / {len(STAGING_TABLES)}"
)

st.sidebar.markdown(
    f"**Dimension Tables:** "
    f"{dimension_available} / {len(DIMENSION_TABLES)}"
)

st.sidebar.markdown(
    f"**Fact Tables:** "
    f"{fact_available} / {len(FACT_TABLES)}"
)

st.sidebar.markdown(
    f"**Total Tables:** "
    f"{total_available} / {total_expected}"
)

if not stats_df.empty:

    total_rows = stats_df["Row Count"].fillna(0).sum()

    st.sidebar.markdown(
        f"**Total Rows:** {int(total_rows):,}"
    )


# =========================================================
# Tabs
# =========================================================

tab1, tab2 = st.tabs([
    "📋 Database Schema & Overview",
    "🔍 Data Viewer & Metadata"
])


# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader("Database Tables Overview")


    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Staging Tables",
        f"{staging_available} / {len(STAGING_TABLES)}"
    )


    col2.metric(
        "Dimension Tables",
        f"{dimension_available} / {len(DIMENSION_TABLES)}"
    )


    col3.metric(
        "Fact Tables",
        f"{fact_available} / {len(FACT_TABLES)}"
    )


    col4.metric(
        "Total Tables",
        f"{total_available} / {total_expected}"
    )
    
    # -----------------------------------------------------
    # Complete Table List
    # -----------------------------------------------------

    st.markdown("### 📋 Complete Table List")


    display_df = stats_df.copy()


    def format_status(status):

        if status == "Available":
            return "✅ Available"

        return "❌ Missing"


    display_df["Status"] = (
        display_df["Status"]
        .apply(format_status)
    )


    display_df["Row Count"] = (
        display_df["Row Count"]
        .apply(
            lambda x:
            f"{int(x):,}"
            if pd.notna(x)
            else "-"
        )
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # Separate Tables By Type
    # -----------------------------------------------------

    st.markdown("### 🗂️ Tables by Type")


    col1, col2, col3 = st.columns(3)


    # STAGING
    with col1:

        st.markdown("#### 🟦 Staging")

        for table in STAGING_TABLES:

            if table in db_tables:

                st.markdown(
                    f"✅ `{table}`"
                )

            else:

                st.markdown(
                    f"❌ `{table}`"
                )


    # DIMENSION
    with col2:

        st.markdown("#### 🟩 Dimension")

        for table in DIMENSION_TABLES:

            if table in db_tables:

                st.markdown(
                    f"✅ `{table}`"
                )

            else:

                st.markdown(
                    f"❌ `{table}`"
                )


    # FACT
    with col3:

        st.markdown("#### 🟧 Fact")

        for table in FACT_TABLES:

            if table in db_tables:

                st.markdown(
                    f"✅ `{table}`"
                )

            else:

                st.markdown(
                    f"❌ `{table}`"
                )


# =========================================================
# TAB 2
# =========================================================

with tab2:

    if selected_table is None:

        st.info(
            "กรุณาเลือกตารางจาก Sidebar"
        )

    else:

        st.subheader(
            f"Table Details: `{selected_table}`"
        )


        # -------------------------------------------------
        # Table Type
        # -------------------------------------------------

        table_type = get_table_type(
            selected_table
        )


        # -------------------------------------------------
        # Missing Table
        # -------------------------------------------------

        if selected_table not in db_tables:

            st.error(
                f"❌ ไม่พบตาราง `{selected_table}` "
                f"ใน dev.duckdb"
            )

            st.info(
                "ตารางนี้อยู่ในรายการที่ระบบคาดหวัง "
                "แต่ยังไม่มีอยู่จริงในฐานข้อมูล"
            )

            st.write("**Table Information**")

            st.write(
                f"- **Type:** `{table_type}`"
            )

            st.write(
                "- **Status:** `Missing`"
            )

            st.write(
                "- **Rows:** `-`"
            )

            st.write(
                "- **Columns:** `-`"
            )


        # -------------------------------------------------
        # Available Table
        # -------------------------------------------------

        else:

            # ---------------------------------------------
            # Get Columns
            # ---------------------------------------------

            safe_table = selected_table.replace(
                '"',
                '""'
            )


            cols_df = run_query(f"""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'main'
                AND table_name = '{selected_table}'
                ORDER BY ordinal_position
            """)


            # ---------------------------------------------
            # Row Count
            # ---------------------------------------------

            row_count = get_row_count(
                selected_table
            )


            # ---------------------------------------------
            # Layout
            # ---------------------------------------------

            col1, col2 = st.columns([1, 3])


            # ---------------------------------------------
            # Summary
            # ---------------------------------------------

            with col1:

                st.write("### Table Summary")

                st.write(
                    f"- **Type:** `{table_type}`"
                )

                st.write(
                    f"- **Status:** `Available`"
                )

                st.write(
                    f"- **Rows:** `{row_count:,}`"
                )

                st.write(
                    f"- **Columns:** `{len(cols_df)}`"
                )


                st.markdown("---")


                st.write(
                    "### Columns & Types"
                )


                if not cols_df.empty:

                    columns_display = cols_df.rename(
                        columns={
                            "column_name": "Column",
                            "data_type": "Type"
                        }
                    )

                    st.dataframe(
                        columns_display,
                        use_container_width=True,
                        hide_index=True
                    )


            # ---------------------------------------------
            # Data Preview
            # ---------------------------------------------

            with col2:

                st.write(
                    "### Data Preview (First 100 rows)"
                )


                data_df = run_query(
                    f'''
                    SELECT *
                    FROM main."{safe_table}"
                    LIMIT 100
                    '''
                )


                if not data_df.empty:

                    st.dataframe(
                        data_df,
                        use_container_width=True,
                        hide_index=True
                    )


                    csv_data = (
                        data_df
                        .to_csv(index=False)
                        .encode("utf-8")
                    )


                    st.download_button(
                        label=(
                            f"📥 Download "
                            f"`{selected_table}` "
                            f"as CSV"
                        ),
                        data=csv_data,
                        file_name=(
                            f"{selected_table}"
                            f"_preview.csv"
                        ),
                        mime="text/csv"
                    )

                else:

                    st.info(
                        "ตารางนี้ไม่มีข้อมูล"
                    )


# =========================================================
# Footer
# =========================================================

st.markdown("---")

st.caption(
    "retail_data DW Explorer • "
    "DuckDB + Pandas + Streamlit"
)