import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

from datetime import date, datetime
from supabase import create_client, Client
from zoneinfo import ZoneInfo  # لإضافة توقيت مصر

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# ----------------- تحميل إعدادات تسجيل الدخول -----------------
with open("hr/config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# تسجيل الدخول
login_info = authenticator.login("Login", location='main')
if login_info:
    name = login_info["name"]
    authentication_status = login_info["authentication_status"]
    username = login_info["username"]
else:
    name = authentication_status = username = None

if authentication_status == False:
    st.error("Username or password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

# ----------------- لو سجل الدخول بنجاح -----------------
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name} 👋")

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

    # رسم الأزرار لكل شخص حسب الاسم المسجل فقط
    if name in people:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"{name} ✅ IN"):
                add_time_in(name)
        with col2:
            if st.button(f"{name} ⛔ OUT"):
                add_time_out(name)
    else:
        st.warning("❌ لا يوجد زرار مسجّل لك في النظام")




