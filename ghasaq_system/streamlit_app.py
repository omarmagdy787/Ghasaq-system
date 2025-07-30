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
supabase: Client = create_client(url, key)

# العناوين المستخدمة في الإدخال
columns = [
    "project_name", "number", "task_name", "quantity", "category",
    "assigned_to", "from", "to", "tasks_depends", "tasks_block",
    "end_date", "plan_b", "check", "team_id", "description"
]

st.title("🧠 Task Management System")

# تخزين حالة الإدخال (جديد أو تعديل)
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

# ====== الخانات ============
st.markdown("### ✍️ Task Input")
inputs = {}
cols = st.columns(3)
for i, column in enumerate(columns):
    with cols[i % 3]:
        inputs[column] = st.text_input(column.replace("_", " ").title(), value="", key=f"{column}_input")

# ====== الزرار ============
col1, col2 = st.columns([1, 6])
with col1:
    if st.session_state.selected_row is None:
        if st.button("➕ Add Task"):
            # إضافة مهمة جديدة
            task_data = {col: inputs[col] for col in columns}
            supabase.table(TABLE_NAME).insert(task_data).execute()
            st.success("✅ Task added successfully.")
    else:
        if st.button("📝 Update Task"):
            # تعديل مهمة
            task_data = {col: inputs[col] for col in columns}
            task_id = st.session_state.selected_row["id"]
            supabase.table(TABLE_NAME).update(task_data).eq("id", task_id).execute()
            st.success("✅ Task updated successfully.")
            st.session_state.selected_row = None

# ====== عرض الجدول ============
st.markdown("### 📋 Tasks Table")
response = supabase.table(TABLE_NAME).select("*").execute()
data = response.data

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # اختيار صف
    selected_index = st.selectbox("اختر رقم الصف للتعديل", options=range(len(df)), format_func=lambda i: f"{i + 1} - {df.iloc[i]['task_name']}")
    selected_row = df.iloc[selected_index]
    
    if st.button("✏️ Edit Selected Row"):
        st.session_state.selected_row = selected_row

        # تعبئة الخانات بالقيم
        for col in columns:
            st.session_state[f"{col}_input"] = str(selected_row.get(col, ""))

else:
    st.info("لا توجد مهام حالياً.")
