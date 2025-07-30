import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

# بيانات تجريبية — استبدلها ببيانات Supabase
data = [
    {"task number": 1, "task name": "Install", "description": "Install window", "from": "Ahmed", "to": "Ali", "check": "No"},
    {"task number": 2, "task name": "Paint", "description": "Paint door", "from": "Ali", "to": "Omar", "check": "Yes"},
]
df = pd.DataFrame(data)

# إعداد شكل الجدول
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(
    wrapText=True,
    autoHeight=True,
    resizable=True
)
gb.configure_grid_options(
    domLayout='autoHeight',
    suppressHorizontalScroll=True
)
gb.configure_column("check", cellEditor='agSelectCellEditor', cellEditorParams={"values": ["Yes", "No"]}, editable=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)
gridOptions = gb.build()

# عرض الجدول
st.markdown("## 📋 جدول المهام")
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    height=400,
    theme="alpine",  # themes: 'streamlit', 'light', 'dark', 'blue', 'fresh', 'material'
)




