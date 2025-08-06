import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client
from streamlit_cookies_manager import EncryptedCookieManager

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "time_sheet"
supabase: Client = create_client(url, key)

# بيانات الدخول
users = {
    "زياد": "1111",
    "عمر": "omar",
    "علي": "3333",
    "يوسف": "4444"
}

# الكوكيز
cookies = EncryptedCookieManager(prefix="timesheet_", password="🔐_secret_password_")
if not cookies.ready():
    st.stop()

# قراءة من الكوكيز
cookie_user = cookies.get("user")
cookie_login_time = cookies.get("login_time")

# نحول وقت الكوكيز من سترنج إلى datetime
if cookie_login_time:
    try:
        cookie_login_time = datetime.fromisoformat(cookie_login_time)
    except:
        cookie_login_time = None

# التحقق من صلاحية الكوكيز
def cookie_expired():
    if not cookie_login_time:
        return True
    return datetime.now() - cookie_login_time > timedelta(days=7)

# تسجيل الخروج
if st.sidebar.button("🔒 تسجيل الخروج"):
    cookies.delete("user")
    cookies.delete("login_time")
    cookies.save()
    st.success("✅ تم تسجيل الخروج")
    st.stop()

# دالة تسجيل الدخول
def login():
    st.title("🔐 تسجيل الدخول")
    username = st.text_input("ادخل اسمك بالعربي")
    password = st.text_input("ادخل الكود السري", type="password")
    if st.button("دخول"):
        if username in users and users[username] == password:
            cookies["user"] = username
            cookies["login_time"] = datetime.now().isoformat()
            cookies.save()
            st.success(f"مرحبًا {username} 👋")
            st.rerun()
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

# -------------------------------
# التشغيل الفعلي

if not cookie_user or cookie_expired():
    login()
else:
    st.title(f"📋 واجهة الحضور والانصراف - {cookie_user}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"{cookie_user} ✅ IN"):
            add_time_in(cookie_user)
    with col2:
        if st.button(f"{cookie_user} ⛔ OUT"):
            add_time_out(cookie_user)
