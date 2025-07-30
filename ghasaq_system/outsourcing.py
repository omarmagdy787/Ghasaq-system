import streamlit as st
from supabase import create_client
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# عمل تحديث تلقائي كل 5 ثواني
st_autorefresh(interval=5000, key="refresh")

# إعداد الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

supabase = create_client(url, key)

# تحميل البيانات
response = supabase.table(TABLE_NAME).select("*").execute()
data = response.data

# تحويل البيانات إلى DataFrame
df = pd.DataFrame(data)

# فلترة على حسب الحالة (مثلاً outsourcing)
outsourcing_df = df[df["status"] == "outsourcing"]

# عرض الجدول
st.dataframe(outsourcing_df)


# عرض البيانات
st.dataframe(outsourcing_df, use_container_width=True)



