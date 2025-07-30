import streamlit as st
from supabase import create_client
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

# إعداد الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"
supabase = create_client(url, key)

# قراءة البيانات
response = supabase.table(TABLE_NAME).select("*").eq("category", "outsourcing").execute()
data = response.data

if not data:
    st.warning("لا يوجد بيانات في التصنيف outsourcing.")
else:
    df = pd.DataFrame(data)

    # الاحتفاظ بالأعمدة المطلوبة فقط
    df = df ["number", "task_name", "description", "from", "to", "check"]

    # إعداد جدول AgGrid للتعديل
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("check", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['yes', 'no']})
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=400
    )

    updated_df = grid_response["data"]
    changed_rows = grid_response["data"]
    st.markdown("---")

    if st.button("💾 تحديث التعديلات"):
        for index, row in updated_df.iterrows():
            task_number = row["task number"]
            new_check_value = row["check"]

            # تحديث القيمة في Supabase بناءً على task number
            supabase.table(TABLE_NAME).update({"check": new_check_value}).eq("task number", task_number).execute()

        st.success("✅ تم تحديث التعديلات بنجاح.")


