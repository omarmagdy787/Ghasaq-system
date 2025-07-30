import streamlit as st
from streamlit import st_autorefresh
from supabase import create_client
import pandas as pd

# ⏱️ تحديث تلقائي كل 5 ثواني
st_autorefresh(interval=5000, key="refresh")

# إعداد الاتصال بـ Supabase
url   = st.secrets["url"]
key   = st.secrets["key"]
TABLE = "main_tasks"
supabase = create_client(url, key)

st.title("Outsourcing Dashboard")

# جلب كل البيانات من الجدول
response = supabase.table(TABLE).select("*").execute()
df       = pd.DataFrame(response.data)

# تأكد وجود عمود category ثم فرّغ فقط outsourcing
if "category" in df.columns:
    outsourcing_df = df[df["category"] == "outsourcing"]
    
    # الأعمدة التي نريد عرضها
    required_columns = ["task number", "task name", "description", "from", "to", "check"]
    missing = [c for c in required_columns if c not in outsourcing_df.columns]
    
    if missing:
        st.error(f"❌ الأعمدة التالية غير موجودة في البيانات: {missing}")
    else:
        st.dataframe(outsourcing_df[required_columns], use_container_width=True)
else:
    st.error("❌ البيانات لا تحتوي على عمود 'category'")
