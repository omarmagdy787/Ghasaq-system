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

st.set_page_config(page_title="Ghasaq System", layout="wide")
st.title("📋 Ghasaq System")

# ================= جلب البيانات لتعبئة الخانات عند الاختيار =================
edit_response = supabase.table(TABLE_NAME).select("*").execute()
edit_data = edit_response.data

task_options = {f"{item['id']} - {item['task_name']}": item for item in edit_data} if edit_data else {}

# ================= اختيار ID =================
st.markdown("### ✏️ تعديل مهمة موجودة")
selected_label = st.selectbox("اختر المهمة للتعديل", [""] + list(task_options.keys()))
selected_task = task_options[selected_label] if selected_label else {}

# ========== إنشاء الأعمدة للخانات ==========
col1, col2, col3 = st.columns([0.5, 0.5, 1])

with col1:
    project_name = st.text_input("Project Name", value=selected_task.get("project_name", ""))
    number = st.text_input("Task Number", value=selected_task.get("number", ""))
    task_name = st.text_input("Task Name", value=selected_task.get("task_name", ""))
    quantity = st.text_input("Quantity", value=selected_task.get("quantity", ""))
    category = st.text_input("Category", value=selected_task.get("category", ""))

with col2:
    assigned_to = st.text_input("Assigned To", value=selected_task.get("assigned_to", ""))
    from_text = st.text_input("From", value=selected_task.get("from", ""))
    to_text = st.text_input("To", value=selected_task.get("to", ""))
    tasks_depends = st.text_input("Tasks Depends On", value=selected_task.get("tasks_depends", ""))
    tasks_block = st.text_input("Tasks Blocked By", value=selected_task.get("tasks_block", ""))

with col3:
    raw_date = selected_task.get("end_date")
    safe_end_date = pd.to_datetime(raw_date, errors="coerce") if raw_date else pd.Timestamp.today()
    end_date = st.date_input("End Date", value=safe_end_date)
    plan_b = st.text_input("Plan B", value=selected_task.get("plan_b", ""))
    check = st.selectbox("Check", ["Yes", "No"], index=["Yes", "No"].index(selected_task.get("check", "Yes")))
    team_id = st.text_input("Team ID", value=selected_task.get("team_id", ""))
    description = st.text_area("Description", value=selected_task.get("description", ""), height=100)

# ========== أزرار الإضافة والتحديث ==========
st.markdown("---")
col_update, col_add = st.columns([1, 1])

with col_update:
    if st.button("🔄 تحديث المهمة") and selected_task:
        try:
            supabase.table(TABLE_NAME).update({
                "project_name": project_name,
                "number": number,
                "task_name": task_name,
                "quantity": quantity,
                "category": category,
                "assigned_to": assigned_to,
                "from": from_text,
                "to": to_text,
                "tasks_depends": tasks_depends,
                "tasks_block": tasks_block,
                "end_date": end_date.isoformat(),
                "plan_b": plan_b,
                "check": check,
                "team_id": team_id,
                "description": description
            }).eq("id", selected_task["id"]).execute()
            st.success("✅ تم تحديث المهمة بنجاح")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"❌ خطأ أثناء التحديث: {e}")

with col_add:
    if st.button("💾 إضافة المهمة"):
        try:
            supabase.table(TABLE_NAME).insert({
                "project_name": project_name,
                "number": number,
                "task_name": task_name,
                "quantity": quantity,
                "category": category,
                "assigned_to": assigned_to,
                "from": from_text,
                "to": to_text,
                "tasks_depends": tasks_depends,
                "tasks_block": tasks_block,
                "end_date": end_date.isoformat(),
                "plan_b": plan_b,
                "check": check,
                "team_id": team_id,
                "description": description
            }).execute()
            st.success("✅ تم حفظ المهمة بنجاح")
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحفظ: {e}")

# ========== عرض الجدول ==========
st.markdown("### 📊 Current Tasks")
try:
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات حالياً.")
except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")
