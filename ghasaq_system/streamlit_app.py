import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd

# ===== تحميل المتغيرات =====
load_dotenv()
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

if not url or not key:
    st.error("❌ تأكد من وجود url و key في ملف .env")
    st.stop()

supabase: Client = create_client(url, key)

# ===== الواجهة =====
st.set_page_config(page_title="Main Tasks", layout="wide")
st.title("📋 Main Tasks Management")

# ===== الأعمدة =====
columns = {
    "project_name": st.text_input("Project Name"),
    "number": st.text_input("Number"),
    "task_name": st.text_input("Task Name"),
    "quantity": st.text_input("Quantity"),
    "category": st.text_input("Category"),
    "assigned_to": st.text_input("Assigned To"),
    "description": st.text_area("Description"),
    "from": st.text_input("From"),
    "to": st.text_input("To"),
    "tasks_depends": st.text_input("Tasks Depends"),
    "tasks_block": st.text_input("Tasks Block"),
    "end_date": st.text_input("End Date"),
    "plan_b": st.text_input("Plan B"),
    "check": st.text_input("Check"),
    "team_id": st.text_input("Team ID")
}

# ===== الأزرار =====
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Add"):
        data = {key: value for key, value in columns.items()}
        supabase.table(TABLE_NAME).insert(data).execute()
        st.success("✅ Task Added")

with col2:
    edit_id = st.text_input("ID to Edit")
    if st.button("✏️ Edit"):
        data = {key: value for key, value in columns.items()}
        supabase.table(TABLE_NAME).update(data).eq("id", edit_id).execute()
        st.success("✏️ Task Edited")

with col3:
    delete_id = st.text_input("ID to Delete")
    if st.button("🗑️ Delete"):
        supabase.table(TABLE_NAME).delete().eq("id", delete_id).execute()
        st.success("🗑️ Task Deleted")

# ===== عرض الجدول =====
st.subheader("📊 Current Tasks")
response = supabase.table(TABLE_NAME).select("*").execute()
data = response.data

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.info("لا توجد بيانات حالياً.")
except Exception as e: st.error("❌ حدث خطأ أثناء تحميل البيانات: {e}")



