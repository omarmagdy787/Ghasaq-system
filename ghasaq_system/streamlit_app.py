import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from supabase import create_client

# إعداد الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"
supabase = create_client(url, key)

st.markdown("### 📊 Current Tasks")

try:
    # جلب البيانات من Supabase
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data

    df = pd.DataFrame(data)
    if not df.empty:
        # تنظيف البيانات من أي أسطر جديدة
        df_cleaned = df.applymap(lambda x: str(x).replace("\n", " ") if pd.notnull(x) else x)

        # إعداد خيارات الجدول
        gb = GridOptionsBuilder.from_dataframe(df_cleaned)
        gb.configure_default_column(
            resizable=True,
            wrapText=True,
            autoHeight=True,
            editable=False,
        )
        gb.configure_grid_options(domLayout='normal')

        grid_options = gb.build()

        AgGrid(
            df_cleaned,
            gridOptions=grid_options,
            height=700,
            fit_columns_on_grid_load=True,
            use_container_width=True,
            theme="material",
        )
    else:
        st.info("لا توجد بيانات حالياً.")
except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")



