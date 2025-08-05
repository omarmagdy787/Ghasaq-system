import streamlit as st
from datetime import date
from supabase import create_client, Client

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# واجهة الإدخال
st.title("📋 واجهة جدول التشغيل")
name = st.text_input("الاسم")
today = st.date_input("التاريخ", value=date.today())

