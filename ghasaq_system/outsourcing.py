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

st.title("Outsourcing Dashboard")

# تحميل البيانات من Supabase
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    df = pd.DataFrame(response.data)
    return df

# تحديث تلقائي كل 10 ثواني
countdown = 10  # بالثواني
st.write(f"🔄 سيتم تحديث البيانات خلال: {countdown} ثانية")
time.sleep(countdown)
st.experimental_rerun()  # إعادة تحميل الصفحة تلقائيًا

# تحميل البيانات
df = load_data()

# فلترة البيانات لعرض فقط اللي category = outsourcing
outsourcing_df = df[df["category"] == "outsourcing"]

# عرض البيانات
st.dataframe(outsourcing_df, use_container_width=True)


