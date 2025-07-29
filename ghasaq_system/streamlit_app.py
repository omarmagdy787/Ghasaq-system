import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd

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

# ========== تنسيق الأعمدة ==========
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    name = st.text_input("اسم المهمة")
with col2:
    description = st.text_input("الوصف", max_chars=100)
with col3:
    status = st.selectbox("الحالة", ["لم تبدأ", "قيد التنفيذ", "منتهية"])

# ========== الأزرار ==========
col4, col5, col6 = st.columns([1, 1, 1])
with col4:
    if st.button("➕ إضافة"):
        try:
            if name:
                supabase.table(TABLE_NAME).insert({"name": name, "description": description, "status": status}).execute()
                st.success("✅ تم الإضافة بنجاح")
            else:
                st.warning("⚠️ من فضلك أدخل اسم المهمة")
        except Exception as e:
            st.error(f"❌ خطأ أثناء الإضافة: {e}")

with col5:
    if st.button("✏️ تعديل"):
        try:
            if name:
                supabase.table(TABLE_NAME).update({"description": description, "status": status}).eq("name", name).execute()
                st.success("✅ تم التعديل بنجاح")
            else:
                st.warning("⚠️ من فضلك أدخل اسم المهمة للتعديل")
        except Exception as e:
            st.error(f"❌ خطأ أثناء التعديل: {e}")

with col6:
    if st.button("🗑️ حذف"):
        try:
            if name:
                supabase.table(TABLE_NAME).delete().eq("name", name).execute()
                st.success("✅ تم الحذف بنجاح")
            else:
                st.warning("⚠️ من فضلك أدخل اسم المهمة للحذف")
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحذف: {e}")

# ========== عرض البيانات ==========
st.markdown("---")
st.subheader("📄 كل المهام")

try:
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data
    df = pd.DataFrame(data)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ℹ️ لا توجد بيانات حالياً")
except Exception as e:
    st.error(f"❌ حدث خطأ أثناء تحميل البيانات: {e}")







