import streamlit as st
from datetime import date, datetime
from supabase import create_client, Client
from zoneinfo import ZoneInfo  # توقيت مصر

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "time_sheet"
supabase: Client = create_client(url, key)

# الوظائف
def add_time_in(name):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    data = {
        "name": name,
        "date": str(date.today()),
        "from": now,
        "project": "Default"
    }

    try:
        supabase.table(TABLE_NAME).insert(data).execute()
        st.success(f"{name} ✅ تم تسجيل وقت الدخول")
    except Exception as e:
        st.error("خطأ أثناء تسجيل الدخول")
        st.write(e)

def add_time_out(name):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    response = supabase.table(TABLE_NAME).select("id").eq("name", name).eq("date", str(date.today())).order("id", desc=True).limit(1).execute()
    if response.data:
        row_id = response.data[0]["id"]
        supabase.table(TABLE_NAME).update({"to": now}).eq("id", row_id).execute()
        st.success(f"{name} ⛔ تم تسجيل الانصراف")
    else:
        st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")

# عرض العنوان
st.title("📋 واجهة الحضور والانصراف")

# أسماء الأشخاص
people = ["زياد", "عمر", "علي", "يوسف"]

# زرارين لكل شخص
for person in people:
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"{person} ✅ IN"):
            add_time_in(person)
    with col2:
        if st.button(f"{person} ⛔ OUT"):
            add_time_out(person)
    else:
        st.warning("❌ لا يوجد زرار مسجّل لك في النظام")


