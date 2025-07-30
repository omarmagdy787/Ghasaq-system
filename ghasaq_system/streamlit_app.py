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
selected_row = pd.DataFrame(grid_response["selected_rows"])

if not selected_row.empty:
    with st.expander("📋 تفاصيل فرعية (تظهر عند الضغط)"):
        st.write(f"**📦 الكمية:** {selected_row.iloc[0]['quantity']}")
        st.write(f"**🏷️ الفئة:** {selected_row.iloc[0]['category']}")
        st.write(f"**📝 الوصف:** {selected_row.iloc[0]['description']}")
        st.write(f"**🔗 يعتمد على:** {selected_row.iloc[0]['tasks_depends']}")
        st.write(f"**⛔ محجوب بسبب:** {selected_row.iloc[0]['tasks_block']}")
        st.write(f"**🛠️ خطة بديلة:** {selected_row.iloc[0]['plan_b']}")



