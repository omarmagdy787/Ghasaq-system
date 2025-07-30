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

# الأعمدة
main_columns = ["project_name", "task_name", "assigned_to", "from", "to", "end_date", "check"]
sub_columns = ["quantity", "category", "description", "tasks_depends", "tasks_block", "plan_b"]

# بناء الخيارات
gb = GridOptionsBuilder.from_dataframe(df)
# إظهار فقط الأعمدة الأساسية
for col in df.columns:
    gb.configure_column(col, hide=(col not in main_columns))

# تمكين الاختيار والصفحات
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_pagination(paginationAutoPageSize=True)
grid_options = gb.build()

# عرض AgGrid
st.subheader("🧾 المهام الرئيسية")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    width="100%",
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    theme="streamlit",
    allow_unsafe_jscode=True,
    reload_data=True
)

# عرض التفاصيل
selected_row = pd.DataFrame(grid_response["selected_rows"])

if not selected_row.empty:
    with st.expander("📋 تفاصيل فرعية (تظهر عند الضغط)"):
        row = selected_row.iloc[0]
        st.write(f"**📦 الكمية:** {row.get('quantity', '—')}")
        st.write(f"**🏷️ الفئة:** {row.get('category', '—')}")
        st.write(f"**📝 الوصف:** {row.get('description', '—')}")
        st.write(f"**🔗 يعتمد على:** {row.get('tasks_depends', '—')}")
        st.write(f"**⛔ محجوب بسبب:** {row.get('tasks_block', '—')}")
        st.write(f"**🛠️ خطة بديلة:** {row.get('plan_b', '—')}")
else:
    st.info("👈 اختر صفًا من الجدول لعرض التفاصيل الفرعية.")





