import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd

# تحميل متغيرات البيئة
load_dotenv()

url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

if not url or not key:
    st.error("❌ تأكد من وجود url و key في ملف .env")
    st.stop()

supabase: Client = create_client(url, key)

st.title("Outsourcing Dashboard")

# زر لتحديث البيانات
if st.button("🔄 تحديث البيانات"):
    st.cache_data.clear()

# تحميل البيانات من Supabase وتخزينها مؤقتًا
@st.cache_data
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    df = pd.DataFrame(response.data)
    return df

df = load_data()

# فلترة البيانات: نعرض فقط اللي category = outsourcing
outsourcing_df = df[df["category"] == "outsourcing"]

# عرض البيانات
st.dataframe(outsourcing_df, use_container_width=True)

