import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# تحميل متغيرات البيئة
load_dotenv()

url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"

# إنشاء عميل Supabase
supabase: Client = create_client(url, key)

st.set_page_config(layout="wide")

st.markdown("## 🌟 Task Management")

# ------------- عرض الجدول باستخدام AgGrid -------------
st.markdown("### 📊 Current Tasks")
try:
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data

    if data:
        df = pd.DataFrame(data)

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=300,
            use_container_width=True
        )

        selected_row = grid_response['selected_rows']
        if selected_row:
            selected = selected_row[0]  # أول صف مختار

            # حفظ البيانات في session_state
            st.session_state['selected_id'] = selected['id']
            st.session_state['from'] = selected['from']
            st.session_state['to'] = selected['to']
            st.session_state['task'] = selected['task']
        else:
            # تفريغ الـ session_state لو مفيش صف متعلم عليه
            st.session_state['selected_id'] = None
            st.session_state['from'] = ""
            st.session_state['to'] = ""
            st.session_state['task'] = ""

    else:
        st.info("لا توجد بيانات حالياً.")
        df = pd.DataFrame(columns=["id", "from", "to", "task"])

except Exception as e:
    st.error(f"❌ خطأ أثناء عرض البيانات: {e}")


# ------------- خانات الإدخال -------------

st.markdown("### ✍️ Add / Edit Task")

col1, col2 = st.columns(2)

with col1:
    from_text = st.text_input("From", value=st.session_state.get('from', ""))
    to_text = st.text_input("To", value=st.session_state.get('to', ""))
with col2:
    task_text = st.text_area("Task", value=st.session_state.get('task', ""))


# ------------- الأزرار -------------
btn1, btn2 = st.columns(2)

with btn1:
    if st.button("➕ Add Task"):
        if from_text and to_text and task_text:
            try:
                supabase.table(TABLE_NAME).insert({
                    "from": from_text,
                    "to": to_text,
                    "task": task_text
                }).execute()
                st.success("✅ تمت إضافة المهمة بنجاح.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ أثناء إضافة المهمة: {e}")
        else:
            st.warning("⚠️ الرجاء ملء جميع الحقول.")

with btn2:
    if st.button("✏️ Edit Task"):
        if st.session_state.get('selected_id') is not None:
            try:
                supabase.table(TABLE_NAME).update({
                    "from": from_text,
                    "to": to_text,
                    "task": task_text
                }).eq("id", st.session_state['selected_id']).execute()
                st.success("✅ تم تعديل المهمة بنجاح.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ أثناء تعديل المهمة: {e}")
        else:
            st.warning("⚠️ الرجاء تحديد مهمة من الجدول أولاً.")



