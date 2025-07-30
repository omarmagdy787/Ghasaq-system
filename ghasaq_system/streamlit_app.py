import streamlit as st
from supabase import create_client
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# إعداد الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

supabase = create_client(url, key)

# استرجاع البيانات من supabase
@st.cache_data
def get_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data
    return pd.DataFrame(data)

st.title("📋 المهام - Dusk System")

df = get_data()

# تحديد الأعمدة الأساسية فقط للعرض في الجدول
main_columns = ["project_name", "number", "task_name", "category", "assigned_to", "end_date", "check"]
df_main = df[main_columns]

# إعداد AG Grid
gb = GridOptionsBuilder.from_dataframe(df_main)
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

# عرض الجدول
grid_response = AgGrid(
    df_main,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=400,
    fit_columns_on_grid_load=True,
    theme='material'
)

selected = grid_response["selected_rows"]

# عرض التفاصيل إذا تم اختيار صف
if selected:
    selected_row = selected[0]
    task_number = selected_row["number"]
    
    # نحصل على السطر الكامل من الداتا الأصلية
    full_row = df[df["number"] == task_number].iloc[0]

    with st.expander("📄 التفاصيل الكاملة"):
        st.markdown(f"""
        **📌 المشروع:** {full_row["project_name"]}  
        **🔢 رقم المهمة:** {full_row["number"]}  
        **📝 اسم المهمة:** {full_row["task_name"]}  
        **📦 الكمية:** {full_row["quantity"]}  
        **📂 التصنيف:** {full_row["category"]}  
        **👷 المعين له:** {full_row["assigned_to"]}  
        **🧾 الوصف:** {full_row["description"]}  
        **📍 من:** {full_row["from"]}  
        **📍 إلى:** {full_row["to"]}  
        **🔗 يعتمد على:** {full_row["tasks_depends"]}  
        **🧱 يعطل:** {full_row["tasks_block"]}  
        **📅 تاريخ النهاية:** {full_row["end_date"]}  
        **🔄 خطة بديلة:** {full_row["plan_b"]}  
        **✅ تحقق:** {full_row["check"]}  
        """)




