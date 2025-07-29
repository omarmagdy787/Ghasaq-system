import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
import streamlit.components.v1 as components


# ========== تحميل ملف .env ==========
load_dotenv()

# ========== بيانات Supabase ==========
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

# ========== التحقق من البيانات ==========
if not url or not key:
    st.error("❌ تأكد من وجود url و key في ملف .env")
    st.stop()

# ========== الاتصال بقاعدة البيانات ==========
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Ghasaq System", layout="wide")
st.title("📋 Ghasaq System")
import streamlit as st
# ========== االتنسيق==========
# إنشاء الأعمدة
col1, col2, col3 = st.columns([0.5, 0.5, 0.5])
with col1:
    project_name = st.text_input("Project Name")
    number = st.text_input("Task Number")
    task_name = st.text_input("Task Name")
    quantity = st.text_input("Quantity")
    category = st.text_input("Category")

with col2:
    assigned_to = st.text_input("Assigned To")
    from_text = st.text_input("From")
    to_text = st.text_input("To")
    tasks_depends = st.text_input("Tasks Depends On")
    tasks_block = st.text_input("Tasks Blocked By")

with col3:
    end_date = st.date_input("End Date")
    plan_b = st.text_input("Plan B")
    check = st.selectbox("Check", ["Yes", "No"])
    team_id = st.text_input("Team ID")
    description = st.text_area("Description", height=100)

# ========== زر الحفظ ==========
st.markdown("---")
if st.button("💾 إضافة المهمة"):
    try:
        data = {
            "project_name": project_name,
            "number": number,
            "task_name": task_name,
            "quantity": quantity,
            "category": category,
            "assigned_to": assigned_to,
            "description": description,
            "from": from_text,
            "to": to_text,
            "tasks_depends": tasks_depends,
            "tasks_block": tasks_block,
            "end_date": end_date.isoformat() if end_date else "",
            "plan_b": plan_b,
            "check": check,
            "team_id": team_id if team_id else None
        }
        supabase.table(TABLE_NAME).insert(data).execute()
        st.success("✅ تم حفظ المهمة بنجاح")
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

# ========== عرض الجدول ==========
st.subheader("📊 Current Tasks")
try:
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات حالياً.")

except Exception as e:
    st.error(f"❌ حدث خطأ أثناء تحميل البيانات: {e}")


