import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from supabase import create_client

# إعداد الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"
supabase = create_client(url, key)

st.markdown("### 📊 Current Tasks")

# --- تحميل البيانات ---
@st.cache_data(ttl=60)
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

df = load_data()

# --- أزرار التحكم ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🔄 تحديث البيانات"):
        st.cache_data.clear()
        st.experimental_rerun()

with col2:
    if st.button("➕ إضافة صف"):
        with st.form("add_form", clear_on_submit=True):
            new_title = st.text_input("Task Title")
            new_status = st.selectbox("Status", ["Pending", "Done"])
            submitted = st.form_submit_button("إضافة")
            if submitted:
                supabase.table(TABLE_NAME).insert({
                    "title": new_title,
                    "status": new_status
                }).execute()
                st.success("✅ تمت الإضافة")
                st.cache_data.clear()
                st.experimental_rerun()

with col3:
    selected_row = None
    st.session_state["selected_row"] = None
    st.write("")  # padding
    if st.button("✏️ تعديل صف"):
        if "selected_row" in st.session_state and st.session_state["selected_row"] is not None:
            row_data = st.session_state["selected_row"]
            with st.form("edit_form"):
                new_title = st.text_input("Title", value=row_data["title"])
                new_status = st.selectbox("Status", ["Pending", "Done"], index=["Pending", "Done"].index(row_data["status"]))
                submitted = st.form_submit_button("تعديل")
                if submitted:
                    supabase.table(TABLE_NAME).update({
                        "title": new_title,
                        "status": new_status
                    }).eq("id", row_data["id"]).execute()
                    st.success("✅ تم التعديل")
                    st.cache_data.clear()
                    st.experimental_rerun()
        else:
            st.warning("يرجى تحديد صف أولاً من الجدول بالأسفل.")

with col4:
    st.write("")  # padding
    if st.button("🗑️ حذف صف"):
        if "selected_row" in st.session_state and st.session_state["selected_row"] is not None:
            row_id = st.session_state["selected_row"]["id"]
            supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()
            st.success("✅ تم الحذف")
            st.cache_data.clear()
            st.experimental_rerun()
        else:
            st.warning("يرجى تحديد صف أولاً من الجدول بالأسفل.")

# --- عرض الجدول باستخدام AgGrid مع التحديد ---
if not df.empty:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=400,
        width="100%",
    )

    selected = grid_response["selected_rows"]
    if selected:
        st.session_state["selected_row"] = selected[0]
    else:
        st.session_state["selected_row"] = None
else:
    st.info("لا توجد بيانات حالياً.")

