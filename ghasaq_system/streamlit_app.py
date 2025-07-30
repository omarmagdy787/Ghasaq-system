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
        # إعداد خيارات الجدول
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(
            resizable=True,
            wrapText=True,         # 🔁 يلف النص داخل الخلية
            autoHeight=True,       # ⬆️ يجعل ارتفاع الصف يناسب المحتوى
            editable=False,
        )
        gb.configure_grid_options(domLayout='normal')  # 🧱 يعرض الجدول بكامل الطول الطبيعي

        grid_options = gb.build()

        AgGrid(
            df,
            gridOptions=grid_options,
            height=700,  # 📏 ارتفاع الجدول بالكامل
            fit_columns_on_grid_load=True,  # 🪄 يناسب الأعمدة تلقائيًا
            use_container_width=True,       # ↔️ يعرض الجدول بعرض الشاشة
            theme="material",               # 🎨 شكل أنيق
        )
    else:
        st.info("لا توجد بيانات حالياً.")
except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")




