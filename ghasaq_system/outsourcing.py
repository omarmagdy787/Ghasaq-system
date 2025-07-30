from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import pandas as pd

# بيانات تجريبية
df = pd.DataFrame({
    "task number": [1, 2, 3],
    "task name": ["Install", "Paint", "Test"],
    "description": ["Install door", "Paint frame", "Test sliding"],
    "from": ["Ali", "Ahmed", "Sara"],
    "to": ["Omar", "Laila", "Tamer"],
    "check": ["No", "Yes", "No"]
})

# بناء إعدادات الجدول
gb = GridOptionsBuilder.from_dataframe(df)

# نخلي الأعمدة تاخد حجمها تلقائي
gb.configure_default_column(resizable=True, autoHeight=True, wrapText=True)
gb.configure_grid_options(domLayout='autoHeight')  # يخلي الجدول يزبط ارتفاعه حسب المحتوى

# نفعّل التحجيم التلقائي للأعمدة
gb.configure_grid_options(suppressHorizontalScroll=False)  # نخلي فيه Scroll لو الأعمدة كتير

# إعداد الـ AgGrid
grid_options = gb.build()

# عرض الجدول
AgGrid(
    df,
    gridOptions=grid_options,
    fit_columns_on_grid_load=True,  # الأعمدة تتظبط أول ما الجدول يظهر
    height=400,                     # ممكن تغيره لو الجدول كبير
    enable_enterprise_modules=False,
    theme="balham",                 # theme حلو وخفيف
    update_mode="MODEL_CHANGED",
    reload_data=True
)

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




