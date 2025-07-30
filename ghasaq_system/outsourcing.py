import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
import time

# تحميل متغيرات البيئة
load_dotenv()

url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

if not url or not key:
    st.error("❌ تأكد من وجود url و key في ملف .env")
    st.stop()

supabase: Client = create_client(url, key)

st.set_page_config(page_title="Outsourcing Dashboard", layout="wide")
st.title("Outsourcing Dashboard")

# ⏱️ تفعيل إعادة التحديث كل 60 ثانية
count = st.experimental_get_query_params().get("count", [0])[0]
if int(count) < 9999:  # تحديد عدد مرات التحديث لو حبيت
    st.experimental_set_query_params(count=int(count) + 1)
    time.sleep(60)  # مدة الانتظار قبل التحديث
    st.experimental_rerun()

# تحميل البيانات من Supabase وتخزينها مؤقتًا
@st.cache_data(ttl=60)  # تعمل كاش للبيانات لمدة 60 ثانية فقط
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    df = pd.DataFrame(response.data)
    return df

df = load_data()

# فلترة البيانات: نعرض فقط اللي category = outsourcing
outsourcing_df = df[df["category"] == "outsourcing"]

# عرض البيانات
st.dataframe(outsourcing_df, use_container_width=True)



