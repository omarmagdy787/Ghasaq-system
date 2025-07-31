import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import json

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

# ========== تهيئة session_state للقيم الافتراضية ==========
default_keys = {
    "project_name": "",
    "number": "",
    "task_name": "",
    "quantity": "",
    "category": "",
    "assigned_to": "",
    "from_text": "",
    "to_text": "",
    "tasks_depends": "",
    "tasks_block": "",
    "end_date": date.today(),
    "plan_b": "",
    "check": "Yes",
    "team_id_input": "",
    "description": "",
    "selected_label": ""
}

for key, default in default_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

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
        if field in st.session_state:
            if field == "end_date":
                # تأكد أنه تاريخ
                st.session_state[field] = pd.to_datetime(value).date() if value else date.today()
            else:
                st.session_state[field] = value

# ========== الحقول ==========
col1, col2, col3, col4, col5 = st.columns([0.5, 0.5, 0.5, 0.5, 0.5])

with col1:
    project_name = st.text_input("Project Name", key="project_name")
    number = st.text_input("Task Number", key="number")
    task_name = st.text_input("Task Name", key="task_name")

with col2:
    quantity = st.text_input("Quantity", key="quantity")
    category = st.text_input("Category", key="category")
    assigned_to = st.text_input("Assigned To", key="assigned_to")

with col3:
    from_text = st.text_input("From", key="from_text")
    to_text = st.text_input("To", key="to_text")
    tasks_depends = st.text_input("Tasks Depends On", key="tasks_depends")

with col4:
    tasks_block = st.text_input("Tasks Blocked By", key="tasks_block")
    end_date = st.date_input("End Date", key="end_date")
    plan_b = st.text_input("Plan B", key="plan_b")

with col5:
    check = st.selectbox("Check", ["Yes", "No"], index=["Yes", "No"].index(st.session_state.get("check", "Yes")), key="check")
    team_id_input = st.text_input("Team ID", key="team_id_input")
    team_id = team_id_input if team_id_input.strip() != "" else None

# ========= Task Details Section =========
st.markdown("### 🧾 Task Details")
# استعادة جدول الوصف من session_state أو البدء بجدول فاضي
try:
    description_df = pd.read_json(st.session_state.get("description", "[]"))
except:
    description_df = pd.DataFrame(columns=["Column 1", "Column 2", "Column 3", "Column 4"])
# زر لإضافة صف جديد (داخل الواجهة)
add_col1, add_col2 = st.columns([1, 5])
with add_col1:
    if st.button("➕ صف جديد"):
        new_row = {"Column 1": "", "Column 2": "", "Column 3": "", "Column 4": ""}
        description_df = pd.concat([description_df, pd.DataFrame([new_row])], ignore_index=True)

# إعداد جدول AgGrid مع إمكانية التعديل والاختيار
gb = GridOptionsBuilder.from_dataframe(description_df)
gb.configure_default_column(editable=True)
gb.configure_grid_options(enableRowGroup=True, enableRangeSelection=True)
gb.configure_side_bar()  # يُظهر لوحة تحكم جانبية للفلترة، الترتيب، إلخ
gb.configure_selection("single")  # لتحديد صف واحد فقط
grid_options = gb.build()

# عرض الجدول
grid_response = AgGrid(
    description_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True,
    editable=True,
    height=300
)

# تحديث البيانات بعد التعديل
updated_df = grid_response["data"]
selected_row = grid_response["selected_rows"]

# زر لحذف الصف المحدد
if selected_row:
    if st.button("🗑 حذف الصف المحدد"):
        index_to_remove = description_df[description_df.eq(selected_row[0]).all(axis=1)].index
        updated_df = updated_df.drop(index_to_remove)
        updated_df.reset_index(drop=True, inplace=True)

# حفظ في session
st.session_state["description"] = updated_df.to_json(orient="records")

# ========== أزرار الإضافة والتحديث والحذف والتفريغ ==========
st.markdown("---")
col_update, col_add, col_delete, col_clear = st.columns([1, 1, 1, 1])

form_keys = list(default_keys.keys())

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












