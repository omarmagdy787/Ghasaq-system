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

# جلب البيانات من Supabase
@st.cache_data
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data
    return pd.DataFrame(data)

df = load_data()

st.title("📋 جدول البيانات")

# إعداد الجدول باستخدام AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination()
gb.configure_side_bar()
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()

# عرض الجدول
response = AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    width='100%',
    theme='material'
)

# عرض الصف المختار بشكل جدول منفصل
selected_rows = response["selected_rows"]

if selected_rows:
    selected_row = selected_rows[0]  # dict

    st.markdown("### ✅ الصف المختار:")
    st.dataframe(pd.DataFrame([selected_row]))









