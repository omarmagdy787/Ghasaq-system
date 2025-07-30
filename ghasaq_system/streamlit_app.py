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
    return pd.DataFrame(response.data)

df = load_data()

# الأعمدة
main_columns = ["id","project_name", "task_name", "assigned_to", "from", "to", "end_date", "check"]
sub_columns = ["quantity", "category", "description", "tasks_depends", "tasks_block", "plan_b"]

# بناء خيارات AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection(selection_mode="single", use_checkbox=True)  # ✅ تفعيل الاختيار
for col in df.columns:
    gb.configure_column(col, hide=(col not in main_columns))
grid_options = gb.build()


response = AgGrid(df, gridOptions=grid_options, update_mode='SELECTION_CHANGED')

selected_rows = response["selected_rows"]

if not selected_rows.empty:
    selected_row = selected_rows.iloc[0].to_dict()
    st.write("Selected Row:", selected_row)


if selected_rows is not None and len(selected_rows) > 0:
    selected_row = selected_rows[0]
    with st.expander("📋 تفاصيل فرعية (تظهر عند اختيار صف)"):
        st.write(f"**📦 الكمية:** {selected_row.get('quantity', '—')}")
        st.write(f"**🏷️ الفئة:** {selected_row.get('category', '—')}")
        st.write(f"**📝 الوصف:** {selected_row.get('description', '—')}")
        st.write(f"**🔗 يعتمد على:** {selected_row.get('tasks_depends', '—')}")
        st.write(f"**⛔ محجوب بسبب:** {selected_row.get('tasks_block', '—')}")
        st.write(f"**🛠️ خطة بديلة:** {selected_row.get('plan_b', '—')}")
else:
    st.info("👈 اختر صفًا من الجدول عن طريق المربع الجانبي لعرض التفاصيل الفرعية.")







