import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ========== إعداد Supabase ==========
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

if not url or not key:
    st.error("❌ تأكد من وجود url و key في ملف .env")
    st.stop()

supabase: Client = create_client(url, key)

# ========== واجهة التطبيق ==========
st.set_page_config(page_title="Task Manager", layout="wide")
st.title("📋 Task Manager System")

# ========== الأعمدة ==========
columns = [
    "project_name", "number", "task_name", "quantity", "category",
    "assigned_to", "description", "from", "to", "tasks_depends",
    "tasks_block", "end_date", "plan_b", "check", "team_id"
]

# ========== مدخلات المستخدم ==========
with st.form("task_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        project_name = st.text_input("📌 Project Name")
        number = st.text_input("🔢 Number")
        task_name = st.text_input("📝 Task Name")
        quantity = st.text_input("📦 Quantity")
        category = st.text_input("📚 Category")

    with col2:
        assigned_to = st.text_input("👤 Assigned To")
        description = st.text_area("🧾 Description")
        from_date = st.date_input("📅 From Date")
        to_date = st.date_input("📅 To Date")
        end_date = st.date_input("📅 End Date")

    with col3:
        tasks_depends = st.text_input("🔗 Tasks Depends On")
        tasks_block = st.text_input("⛔ Tasks Block")
        plan_b = st.text_input("🗂 Plan B")
        check = st.text_input("✅ Check")
        team_id = st.text_input("🆔 Team ID")

    submitted = st.form_submit_button("➕ Add Task")

    if submitted:
        data = {
            "project_name": project_name,
            "number": number,
            "task_name": task_name,
            "quantity": quantity,
            "category": category,
            "assigned_to": assigned_to,
            "description": description,
            "from": str(from_date),
            "to": str(to_date),
            "tasks_depends": tasks_depends,
            "tasks_block": tasks_block,
            "end_date": str(end_date),
            "plan_b": plan_b,
            "check": check,
            "team_id": team_id
        }
        try:
            supabase.table(TABLE_NAME).insert(data).execute()
            st.success("✅ Task Added Successfully!")
        except Exception as e:
            st.error(f"❌ Error adding task: {e}")

# ========== عرض البيانات ==========
st.markdown("### 📊 Current Tasks")
try:
    result = supabase.table(TABLE_NAME).select("*").execute()
    tasks = result.data
    df = pd.DataFrame(tasks)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد مهام حالياً.")
except Exception as e:
    st.error(f"❌ حدث خطأ أثناء تحميل البيانات: {e}")



