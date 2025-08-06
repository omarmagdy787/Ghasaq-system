import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client
from streamlit_cookies_manager import EncryptedCookieManager
import json

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# إعداد الكوكيز
cookies = EncryptedCookieManager(
    prefix="timesheet_",
    password="omar"  # ← كلمة السر هنا تم تعديلها
)
if not cookies.ready():
    st.stop()

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "time_sheet"
supabase: Client = create_client(url, key)

# بيانات المستخدمين
users = {
    "زياد": "1111",
    "عمر": "2222",
    "علي": "3333",
    "يوسف": "4444"
}

# التحقق من الجلسة من الكوكيز
cookie_user = cookies.get("user")
cookie_time = cookies.get("login_time")

# دالة التحقق من انتهاء الأسبوع
def session_expired():
    if not cookie_time:
        return True
    last_login = datetime.fromisoformat(cookie_time)
    return datetime.now() - last_login > timedelta(days=7)

# تسجيل الخروج اليدوي
if st.sidebar.button("🔒 تسجيل الخروج"):
    cookies.delete("user")
    cookies.delete("login_time")
    st.success("تم تسجيل الخروج")
    st.experimental_rerun()

# دالة تسجيل الدخول
def login():
    st.title("🔐 تسجيل الدخول")
    username = st.text_input("ادخل اسمك بالعربي")
    password = st.text_input("ادخل الكود السري", type="password")
    if st.button("دخول"):
        if username in users and users[username] == password:
            cookies.set("user", username)
            cookies.set("login_time", datetime.now().isoformat())
            st.success(f"مرحبًا {username} 👋")
            st.experimental_rerun()
        else:
            st.error("❌ اسم المستخدم أو الكود غير صحيح")

# دالة تسجيل الدخول في Supabase
def add_time_in(name):
    now = datetime.now().isoformat()
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

# دالة تسجيل الخروج في Supabase
def add_time_out(name):
    now = datetime.now().isoformat()
    response = supabase.table(TABLE_NAME).select("id").eq("name", name).eq("date", str(date.today())).order("id", desc=True).limit(1).execute()
    if response.data:
        row_id = response.data[0]["id"]
        supabase.table(TABLE_NAME).update({"to": now}).eq("id", row_id).execute()
        st.success(f"{name} ⛔ تم تسجيل الانصراف")
    else:
        st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")

# --------------------------------
# التشغيل الفعلي

if not cookie_user or session_expired():
    login()
else:
    current_user = cookie_user
    st.title(f"📋 واجهة الحضور والانصراف - {current_user}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"{current_user} ✅ IN"):
            add_time_in(current_user)
    with col2:
        if st.button(f"{current_user} ⛔ OUT"):
            add_time_out(current_user)
