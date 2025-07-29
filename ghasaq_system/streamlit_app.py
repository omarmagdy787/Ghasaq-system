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
col1, col2, col3 = st.columns([0.5, 0.5, 1])
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
    st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")

# ========== تعديل مهمة موجودة ==========
st.markdown("---")
st.subheader("✏️ تعديل مهمة موجودة")

# الحصول على كل المهام لجلب الـ IDs
edit_response = supabase.table(TABLE_NAME).select("*").execute()
edit_data = edit_response.data

if edit_data:
    task_options = {f"{item['id']} - {item['task_name']}": item['id'] for item in edit_data}
    selected_task_label = st.selectbox("اختر المهمة للتعديل", list(task_options.keys()))
    selected_task_id = task_options[selected_task_label]

    # الحصول على بيانات المهمة المختارة
    selected_task = next((item for item in edit_data if item["id"] == selected_task_id), None)

    if selected_task:
        # ملء الخانات تلقائياً
        project_name = st.text_input("Project Name", selected_task["project_name"])
        number = st.text_input("Task Number", selected_task["number"])
        task_name = st.text_input("Task Name", selected_task["task_name"])
        quantity = st.text_input("Quantity", selected_task["quantity"])
        category = st.text_input("Category", selected_task["category"])
        assigned_to = st.text_input("Assigned To", selected_task["assigned_to"])
        from_text = st.text_input("From", selected_task["from"])
        to_text = st.text_input("To", selected_task["to"])
        tasks_depends = st.text_input("Tasks Depends On", selected_task["tasks_depends"])
        tasks_block = st.text_input("Tasks Blocked By", selected_task["tasks_block"])
        end_date_raw = selected_task.get("end_date", "")
        end_date = st.date_input("End Date", pd.to_datetime(end_date_raw) if end_date_raw else pd.Timestamp.today())
        plan_b = st.text_input("Plan B", selected_task["plan_b"])
        check = st.selectbox("Check", ["Yes", "No"], index=0 if selected_task["check"] == "Yes" else 1)
        team_id = st.text_input("Team ID", selected_task["team_id"])
        description = st.text_area("Description", selected_task["description"], height=100)

        if st.button("🔄 تحديث المهمة"):
            try:
                updated_data = {
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
                supabase.table(TABLE_NAME).update(updated_data).eq("id", selected_task_id).execute()
                st.success("✅ تم تحديث المهمة بنجاح")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء التحديث: {e}")
else:
    st.info("لا توجد مهام للتعديل.")



