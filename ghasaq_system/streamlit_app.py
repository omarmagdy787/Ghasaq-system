import streamlit as st
from supabase import create_client
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
supabase = create_client(url, key)
TABLE_NAME = "main_tasks"

st.title("📋 Main Tasks Dashboard")

# تحميل البيانات من Supabase
@st.cache_data
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data
    return pd.DataFrame(data)

df = load_data()

# تقسيم الأعمدة إلى أساسية وفرعية
main_columns = ["project_name", "number", "task_name", "category", "assigned_to", "from", "to", "end_date", "check"]
sub_columns = ["quantity", "description", "tasks_depends", "tasks_block", "plan_b", "team_id"]

# عرض الجدول الأساسي
st.subheader("🧾 المهام الرئيسية")
gb = GridOptionsBuilder.from_dataframe(df[main_columns])
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()

grid_response = AgGrid(
    df[main_columns],
    gridOptions=grid_options,
    height=300,
    width="100%",
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    theme="streamlit"
)

if not selected_row.empty:

# لو تم اختيار صف، نعرض التفاصيل
if selected_row:
    st.markdown("---")
    st.subheader("📌 التفاصيل")
    row_data = selected_row[0]
    full_row = df[df["number"] == row_data["number"]].iloc[0]

    for col in sub_columns:
        st.write(f"**{col}**: {full_row[col]}")





