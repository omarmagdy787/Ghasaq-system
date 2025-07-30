import streamlit as st
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
import pandas as pd

# ---------- إعداد Supabase ----------
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"
supabase = create_client(url, key)

# ---------- تحديث تلقائي كل دقيقة ----------
st_autorefresh(interval=60 * 1000, key="refresh")

# ---------- العنوان ----------
st.markdown("<h2 style='text-align: center;'>Outsourcing Tasks</h2>", unsafe_allow_html=True)

# ---------- جلب البيانات من Supabase ----------
response = supabase.table(TABLE_NAME).select("*").execute()
data = response.data

# ---------- تحويل إلى DataFrame ----------
df = pd.DataFrame(data)

# ---------- فلترة فقط المهام التي فيها category = outsourcing ----------
if not df.empty and "category" in df.columns:
    df_outsourcing = df[df["category"] == "outsourcing"]

    # تحديد الأعمدة المطلوبة فقط
    required_columns = ["number", "task_name", "description", "from", "to", "check"]
    available_columns = [col for col in required_columns if col in df_outsourcing.columns]
    df_outsourcing = df_outsourcing[available_columns]

    # عرض الجدول
    st.dataframe(df_outsourcing, use_container_width=True)
else:
    st.warning("لا توجد بيانات أو العمود 'category' غير موجود.")

