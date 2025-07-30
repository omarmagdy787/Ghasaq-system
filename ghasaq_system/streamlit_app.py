import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from supabase import create_client
import os

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
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gridOptions = gb.build()
        AgGrid(df, gridOptions=gridOptions, height=400, fit_columns_on_grid_load=True)
    else:
        st.info("لا توجد بيانات حالياً.")
except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")


        # إعداد الخيارات
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_default_column(editable=False, groupable=True)
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        gridOptions = gb.build()

        # عرض الجدول
        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            fit_columns_on_grid_load=True,
            theme="alpine",  # "streamlit", "light", "dark", "blue", "fresh"
            update_mode="SELECTION_CHANGED",
            enable_enterprise_modules=False,
            height=400,
            width="100%",
        )

        selected = grid_response["selected_rows"]
        if selected:
            st.success(f"🟢 تم تحديد الصف: {selected[0]}")
    else:
        st.info("لا توجد بيانات حالياً.")
except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")




