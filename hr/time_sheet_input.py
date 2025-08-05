import streamlit as st
from datetime import date, datetime
from supabase import create_client, Client

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "time_sheet"
supabase: Client = create_client(url, key)

# واجهة الإدخال
st.title("📋 واجهة جدول التشغيل")
name = st.text_input("الاسم")
today = st.date_input("التاريخ", value=date.today())

# الوظائف
def add_time_in(name, date_value):
    now = datetime.now().isoformat()
    data = {
        "name": name,
        "date": str(date_value),
        "from": now,
        "project": "Default"  # لو حابب تضيف مشروع افتراضي
    }

    try:
        supabase.table(TABLE_NAME).insert(data).execute()
        st.success("تم تسجيل وقت الدخول بنجاح")
        # st.write(response)  ← تم حذفها
    except Exception as e:
        st.error("حدث خطأ أثناء إضافة وقت الدخول")
        st.write(e)


def add_time_out(name, today):
    now = datetime.now().isoformat()
    response = supabase.table(TABLE_NAME).select("id").eq("name", name).eq("date", str(today)).execute()
    if response.data:
        row_id = response.data[0]["id"]
        supabase.table(TABLE_NAME).update({"to": now}).eq("id", row_id).execute()
        st.success(f"تم تسجيل الانصراف: {now}")
        # st.write(response)  ← لو كنت بتعرضها هنا كمان، شيلها
    else:
        st.warning("لا يوجد صف مسجل لهذا الاسم والتاريخ لتحديثه.")


# الأزرار
col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Time In"):
        if name:
            add_time_in(name, today)
        else:
            st.warning("من فضلك أدخل الاسم أولًا.")

with col2:
    if st.button("⛔ Time Out"):
        if name:
            add_time_out(name, today)
        else:
            st.warning("من فضلك أدخل الاسم أولًا.")
