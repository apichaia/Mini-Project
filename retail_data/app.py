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


# =========================================================
# Database Path
# =========================================================

# dev.duckdb อยู่โฟลเดอร์เดียวกับ app.py
PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "dev.duckdb"


# =========================================================
# Tables That We Want To Display
# =========================================================

# -------------------------
# Staging Tables (12)
# -------------------------

STAGING_TABLES = [
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
]


# -------------------------
# Dimension Tables (7)
# -------------------------

DIMENSION_TABLES = [
    "dim_customer",
    "dim_date",
    "dim_employee",
    "dim_product",
    "dim_promotion",
    "dim_store",
    "dim_supplier",
]


# -------------------------
# Fact Tables (4)
# -------------------------

FACT_TABLES = [
    "fact_payments",
    "fact_returns",
    "fact_sales",
    "fact_shipments",
]


# =========================================================
# Connect To DuckDB
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

        st.error(
            f"Database connection error: {e}"
        )

        return None


# =========================================================
# Run Query
# =========================================================

def run_query(query):

    conn = get_connection()

    if conn is None:
        return pd.DataFrame()

    try:

        return conn.execute(query).fetch_df()

    except Exception as e:

        st.error(
            f"Error running query: {e}"
        )

        return pd.DataFrame()


# =========================================================
# Check Database
# =========================================================

if not DB_PATH.exists():

    st.error(
        f"""
        ❌ ไม่พบไฟล์ dev.duckdb

        Path:
        `{DB_PATH}`

        กรุณาตรวจสอบว่า dev.duckdb
        อยู่โฟลเดอร์เดียวกับ app.py
        """
    )

    st.stop()


# =========================================================
# Get Tables From Database
# =========================================================

tables_df = run_query(
    """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main'
    """
)


if tables_df.empty:

    st.error(
        "❌ ไม่พบตารางใน Schema main"
    )

    st.stop()


# รายชื่อตารางที่มีอยู่จริงใน DB
db_tables = set(
    tables_df["table_name"].tolist()
)


# =========================================================
# Check Which Required Tables Exist
# =========================================================

available_staging = [
    table
    for table in STAGING_TABLES
    if table in db_tables
]


available_dimension = [
    table
    for table in DIMENSION_TABLES
    if table in db_tables
]


available_fact = [
    table
    for table in FACT_TABLES
    if table in db_tables
]


# =========================================================
# All Tables That We Want To Show
# =========================================================

all_tables = (
    available_staging
    + available_dimension
    + available_fact
)


# =========================================================
# Get Row Count
# =========================================================

def get_row_count(table_name):

    conn = get_connection()

    if conn is None:
        return 0

    try:

        # ป้องกันปัญหาชื่อตาราง
        safe_table = table_name.replace(
            '"',
            '""'
        )

        result = conn.execute(
            f'''
            SELECT COUNT(*)
            FROM main."{safe_table}"
            '''
        ).fetchone()

        if result is None:
            return 0

        return result[0]

    except Exception as e:

        st.warning(
            f"ไม่สามารถนับ Row ของ {table_name}: {e}"
        )

        return 0


# =========================================================
# Create Table Statistics
# =========================================================

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


    row_count = get_row_count(table)


    table_stats.append(
        {
            "type": table_type,
            "table_name": table,
            "row_count": row_count
        }
    )


stats_df = pd.DataFrame(
    table_stats
)


# =========================================================
# App Title & Style
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="main-title">'
    '📊 retail_data'
    '</div>',
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

st.sidebar.title(
    "🗂️ Table Browser"
)


# ---------------------------------------------------------
# Table Group
# ---------------------------------------------------------

table_groups = {

    "Staging Tables": available_staging,

    "Dimension Tables": available_dimension,

    "Fact Tables": available_fact,

    "All Tables": all_tables

}


selected_group = st.sidebar.selectbox(
    "Select Table Group",
    [
        "Staging Tables",
        "Dimension Tables",
        "Fact Tables",
        "All Tables"
    ]
)


# ---------------------------------------------------------
# Tables In Selected Group
# ---------------------------------------------------------

selected_group_tables = table_groups[
    selected_group
]


if selected_group_tables:

    selected_table = st.sidebar.selectbox(
        "Select a table to inspect",
        selected_group_tables
    )

else:

    selected_table = None

    st.sidebar.warning(
        "ไม่พบตารางในกลุ่มนี้"
    )


# =========================================================
# Sidebar Quick Stats
# =========================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "Quick Stats"
)


st.sidebar.markdown(
    f"**Staging Tables:** "
    f"{len(available_staging)} / 12"
)


st.sidebar.markdown(
    f"**Dimension Tables:** "
    f"{len(available_dimension)} / 7"
)


st.sidebar.markdown(
    f"**Fact Tables:** "
    f"{len(available_fact)} / 4"
)


st.sidebar.markdown(
    f"**Total Tables:** "
    f"{len(all_tables)} / 23"
)


if not stats_df.empty:

    total_rows = stats_df[
        "row_count"
    ].sum()

    st.sidebar.markdown(
        f"**Total Rows:** "
        f"{total_rows:,}"
    )


# =========================================================
# Main Tabs
# =========================================================

tab1, tab2 = st.tabs(
    [
        "📋 Database Schema & Overview",
        "🔍 Data Viewer & Metadata"
    ]
)


# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader(
        "Database Tables Overview"
    )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Staging Tables",
            f"{len(available_staging)} / 12"
        )


    with col2:

        st.metric(
            "Dimension Tables",
            f"{len(available_dimension)} / 7"
        )


    with col3:

        st.metric(
            "Fact Tables",
            f"{len(available_fact)} / 4"
        )


    with col4:

        st.metric(
            "Total Tables",
            f"{len(all_tables)} / 23"
        )


    # -----------------------------------------------------
    # Table List
    # -----------------------------------------------------

    st.markdown(
        "### Table List & Record Counts"
    )


    if not stats_df.empty:

        display_df = stats_df[
            [
                "type",
                "table_name",
                "row_count"
            ]
        ].rename(
            columns={
                "type": "Type",
                "table_name": "Table Name",
                "row_count": "Row Count"
            }
        )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.warning(
            "ไม่พบตารางที่กำหนดไว้"
        )


    # -----------------------------------------------------
    # Missing Tables
    # -----------------------------------------------------

    missing_staging = [
        table
        for table in STAGING_TABLES
        if table not in db_tables
    ]


    missing_dimension = [
        table
        for table in DIMENSION_TABLES
        if table not in db_tables
    ]


    missing_fact = [
        table
        for table in FACT_TABLES
        if table not in db_tables
    ]


    if (
        missing_staging
        or missing_dimension
        or missing_fact
    ):

        st.warning(
            "⚠️ มีตารางที่กำหนดไว้แต่ไม่พบใน dev.duckdb"
        )


        if missing_staging:

            st.write(
                "**Missing Staging:** "
                + ", ".join(missing_staging)
            )


        if missing_dimension:

            st.write(
                "**Missing Dimension:** "
                + ", ".join(missing_dimension)
            )


        if missing_fact:

            st.write(
                "**Missing Fact:** "
                + ", ".join(missing_fact)
            )


# =========================================================
# TAB 2 - DATA VIEWER
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
        # Determine Table Type
        # -------------------------------------------------

        if selected_table in available_staging:

            table_type = "Staging"

        elif selected_table in available_dimension:

            table_type = "Dimension"

        elif selected_table in available_fact:

            table_type = "Fact"

        else:

            table_type = "Unknown"


        # -------------------------------------------------
        # Get Column Information
        # -------------------------------------------------

        cols_df = run_query(
            f"""
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'main'
              AND table_name = '{selected_table}'
            ORDER BY ordinal_position
            """
        )


        # -------------------------------------------------
        # Get Row Count
        # -------------------------------------------------

        row_count = get_row_count(
            selected_table
        )


        # -------------------------------------------------
        # Layout
        # -------------------------------------------------

        col1, col2 = st.columns(
            [1, 3]
        )


        # =================================================
        # LEFT SIDE
        # =================================================

        with col1:

            st.write(
                "**Table Summary**"
            )


            st.write(
                f"- **Type:** `{table_type}`"
            )


            st.write(
                f"- **Rows:** `{row_count:,}`"
            )


            st.write(
                f"- **Columns:** `{len(cols_df)}`"
            )


            st.markdown("---")


            st.write(
                "**Columns & Types**"
            )


            if not cols_df.empty:

                column_display = cols_df.rename(
                    columns={
                        "column_name": "Column",
                        "data_type": "Type"
                    }
                )


                st.dataframe(
                    column_display,
                    use_container_width=True,
                    hide_index=True
                )


            else:

                st.warning(
                    "ไม่พบข้อมูล Column"
                )


        # =================================================
        # RIGHT SIDE
        # =================================================

        with col2:

            st.write(
                "**Data Preview (First 100 rows)**"
            )


            safe_table = selected_table.replace(
                '"',
                '""'
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


                # -----------------------------------------
                # Download CSV
                # -----------------------------------------

                csv_data = (
                    data_df
                    .to_csv(index=False)
                    .encode("utf-8")
                )


                st.download_button(
                    label=(
                        f"📥 Download "
                        f"`{selected_table}` as CSV"
                    ),
                    data=csv_data,
                    file_name=(
                        f"{selected_table}_preview.csv"
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
    
    "retail_data DW Explorer • DuckDB + Pandas + Streamlit"
)
