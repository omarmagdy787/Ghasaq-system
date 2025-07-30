import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd

# ✅ تحميل متغيرات البيئة
load_dotenv()
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

# ✅ إنشاء عميل Supabase
supabase: Client = create_client(url, key)

# ✅ الأعمدة المستخدمة
COLUMNS = [
    "project_name", "number", "task_name", "quantity", "category",
    "assigned_to", "from", "to", "tasks_depends", "tasks_block",
    "end_date", "plan_b", "check", "team_id", "description"
]

# ✅ إدخال البيانات
st.title("📋 Dusk System - Task Manager")

with st.form("add_task_form"):
    inputs = {}
    for col in COLUMNS:
        if col in ["description", "tasks_depends", "tasks_block"]:
            inputs[col] = st.text_area(col.replace("_", " ").capitalize())
        elif col in ["end_date"]:
            inputs[col] = st.date_input("End Date")
        elif col in ["quantity", "number", "team_id"]:
            inputs[col] = st.number_input(col.replace("_", " ").capitalize(), step=1)
        else:
            inputs[col] = st.text_input(col.replace("_", " ").capitalize())

    submitted = st.form_submit_button("➕ Add Task")
    if submitted:
        try:
            supabase.table(TABLE_NAME).insert([inputs]).execute()
            st.success("✅ Task added successfully!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ✅ عرض البيانات
st.markdown("### 📊 Current Tasks")
try:
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        selected_index = st.number_input("اختر رقم الصف للتعديل", min_value=0, max_value=len(df)-1, step=1)
        selected_row = df.iloc[selected_index]

        st.markdown("### ✏️ Edit Task")
        edited = {}
        for col in COLUMNS:
            default = selected_row.get(col, "")
            if col in ["description", "tasks_depends", "tasks_block"]:
                edited[col] = st.text_area(f"{col}", value=default, key=f"{col}_edit")
            elif col in ["end_date"]:
                edited[col] = st.date_input(f"{col}", value=pd.to_datetime(default), key=f"{col}_edit")
            elif col in ["quantity", "number", "team_id"]:
                edited[col] = st.number_input(f"{col}", value=int(default) if default else 0, key=f"{col}_edit")
            else:
                edited[col] = st.text_input(f"{col}", value=default, key=f"{col}_edit")

        if st.button("💾 Save Changes"):
            try:
                task_id = selected_row["id"]
                supabase.table(TABLE_NAME).update(edited).eq("id", task_id).execute()
                st.success("✅ Task updated successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.info("لا توجد بيانات حالياً.")
except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")
