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

# ================= اختيار المهمة =================
st.markdown("### ✏ تعديل مهمة موجودة")
selected_label = st.selectbox("اختر المهمة للتعديل", [""] + list(task_options.keys()), key="selected_label")
selected_task = task_options[selected_label] if selected_label else {}

# ========== تحديث session_state بالقيم المختارة ==========
if selected_task:
    for field, value in selected_task.items():
        if field not in st.session_state:
            st.session_state[field] = value

# ========== الحقول ==========
col1, col2, col3,col4,col5  = st.columns([0.5, 0.5, 0.5,0.5,0.5])

with col1:
    project_name = st.text_input("Project Name", value=st.session_state.get("project_name", ""), key="project_name")
    number = st.text_input("Task Number", value=st.session_state.get("number", ""), key="number")
    task_name = st.text_input("Task Name", value=st.session_state.get("task_name", ""), key="task_name")
    
with col2:
    quantity = st.text_input("Quantity", value=st.session_state.get("quantity", ""), key="quantity")
    category = st.text_input("Category", value=st.session_state.get("category", ""), key="category")
    assigned_to = st.text_input("Assigned To", value=st.session_state.get("assigned_to", ""), key="assigned_to")
    
with col3:
    from_text = st.text_input("From", value=st.session_state.get("from", ""), key="from_text")
    to_text = st.text_input("To", value=st.session_state.get("to", ""), key="to_text")
    tasks_depends = st.text_input("Tasks Depends On", value=st.session_state.get("tasks_depends", ""), key="tasks_depends")
    
with col4:
    tasks_block = st.text_input("Tasks Blocked By", value=st.session_state.get("tasks_block", ""), key="tasks_block")
    raw_date = st.session_state.get("end_date", pd.Timestamp.today())
    safe_end_date = pd.to_datetime(raw_date, errors="coerce") if raw_date else pd.Timestamp.today()
    end_date = st.date_input("End Date", value=safe_end_date, key="end_date")
    plan_b = st.text_input("Plan B", value=st.session_state.get("plan_b", ""), key="plan_b")

with col5:
    check = st.selectbox("Check", ["Yes", "No"], index=["Yes", "No"].index(st.session_state.get("check", "Yes")), key="check")
    team_id_input = st.text_input("Team ID", value=st.session_state.get("team_id_input", ""), key="team_id_input")
    team_id = team_id_input if team_id_input.strip() != "" else None
    description = st.text_area("Description", value=st.session_state.get("description", ""), key="description")

# ========== أزرار الإضافة والتحديث والحذف والتفريغ ==========
st.markdown("---")
col_update, col_add, col_delete, col_clear = st.columns([1, 1, 1, 1])

# keys المستخدمة
form_keys = [
    "project_name", "number", "task_name", "quantity", "category",
    "assigned_to", "from_text", "to_text", "tasks_depends", "tasks_block",
    "end_date", "plan_b", "check", "team_id_input", "description", "selected_label"
]

def clear_form():
    for key in form_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

with col_add:
    if st.button("💾 إضافة المهمة"):
        try:
            supabase.table(TABLE_NAME).insert({
                "project_name": project_name or None,
                "number": number or None,
                "task_name": task_name or None,
                "quantity": quantity or None,
                "category": category or None,
                "assigned_to": assigned_to or None,
                "from": from_text or None,
                "to": to_text or None,
                "tasks_depends": tasks_depends or None,
                "tasks_block": tasks_block or None,
                "end_date": end_date.isoformat() if end_date else None,
                "plan_b": plan_b or None,
                "check": check or None,
                "team_id": team_id,
                "description": description or None
            }).execute()
            st.success("✅ تم حفظ المهمة بنجاح")
            clear_form()
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحفظ: {e}")

with col_update:
    if st.button("🔄 تحديث المهمة") and selected_task:
        try:
            supabase.table(TABLE_NAME).update({
                "project_name": project_name or None,
                "number": number or None,
                "task_name": task_name or None,
                "quantity": quantity or None,
                "category": category or None,
                "assigned_to": assigned_to or None,
                "from": from_text or None,
                "to": to_text or None,
                "tasks_depends": tasks_depends or None,
                "tasks_block": tasks_block or None,
                "end_date": end_date.isoformat() if end_date else None,
                "plan_b": plan_b or None,
                "check": check or None,
                "team_id": team_id,
                "description": description or None
            }).eq("id", selected_task["id"]).execute()
            st.success("✅ تم تحديث المهمة بنجاح")
            clear_form()
        except Exception as e:
            st.error(f"❌ خطأ أثناء التحديث: {e}")

with col_delete:
    if st.button("🗑 حذف المهمة") and st.session_state.get("selected_label", ""):
        try:
            task_id = task_options[st.session_state.selected_label]["id"]
            supabase.table(TABLE_NAME).delete().eq("id", task_id).execute()
            st.success("✅ تم حذف المهمة بنجاح")
            clear_form()
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحذف: {e}")

with col_clear:
    if st.button("🧹 تفريغ الحقول"):
        clear_form()

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











