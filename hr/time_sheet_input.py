import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client
from streamlit_cookies_manager import EncryptedCookieManager
from zoneinfo import ZoneInfo  # ⬅ إضافة المكتبة

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
cookie_login_time_raw = cookies.get("login_time")

# نحول وقت الكوكيز من سترنج إلى datetime (مع التعامل مع المناطق الزمنية)
cookie_login_time = None
if cookie_login_time_raw:
    try:
        cookie_login_time = datetime.fromisoformat(cookie_login_time_raw)
        # لو الـ datetime اللي جاي من isoformat مفيهوش tzinfo، نضيف توقيت القاهرة افتراضياً
        if cookie_login_time.tzinfo is None:
            cookie_login_time = cookie_login_time.replace(tzinfo=ZoneInfo("Africa/Cairo"))
    except Exception:
        cookie_login_time = None

# التحقق من صلاحية الكوكيز
def cookie_expired():
    # لو مفيش وقت مسجل أو النوع مش datetime => اعتبر الكوكي منتهي الصلاحية
    if not cookie_login_time or not isinstance(cookie_login_time, datetime):
        return True
    try:
        return datetime.now(ZoneInfo("Africa/Cairo")) - cookie_login_time > timedelta(days=7)
    except Exception:
        return True

# تسجيل الخروج
if st.sidebar.button("🔒 تسجيل الخروج"):
    cookies["user"] = ""
    cookies["login_time"] = ""
    cookies.save()
    st.success("✅ تم تسجيل الخروج")
    st.stop()

# دالة تسجيل الدخول (واجهة)
def login():
    st.title("🔐 تسجيل الدخول")
    username = st.text_input("ادخل اسمك بالعربي")
    password = st.text_input("ادخل الكود السري", type="password")
    if st.button("دخول"):
        if username in users and users[username] == password:
            cookies["user"] = username
            cookies["login_time"] = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
            cookies.save()
            st.success(f"مرحبًا {username} 👋")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو الكود غير صحيح")

# دالة تسجيل الدخول في Supabase
def add_time_in(name):
    now_iso = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    today_cairo = datetime.now(ZoneInfo("Africa/Cairo")).date()
    data = {
        "name": name,
        "date": str(today_cairo),
        "from": now_iso,
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
    now_iso = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    today_cairo = datetime.now(ZoneInfo("Africa/Cairo")).date()
    try:
        response = supabase.table(TABLE_NAME) \
            .select("id") \
            .eq("name", name) \
            .eq("date", str(today_cairo)) \
            .order("id", desc=True) \
            .limit(1) \
            .execute()
        if response and getattr(response, "data", None):
            row_id = response.data[0]["id"]
            supabase.table(TABLE_NAME).update({"to": now_iso}).eq("id", row_id).execute()
            st.success(f"{name} ⛔ تم تسجيل الانصراف")
        else:
            st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")
    except Exception as e:
        st.error("حدث خطأ أثناء تسجيل الانصراف")
        st.write(e)

# -------------------------------
# التشغيل الفعلي
if not cookie_user or cookie_expired():
    # لو مفيش مستخدم مسجل أو الكوكي منتهي -> نعرض صفحة تسجيل الدخول
    login()
else:
    st.title(f"📋 واجهة الحضور والانصراف - {cookie_user}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"{cookie_user} ✅ IN"):
            # لو لسبب ما الكوكيز مش موجودة (حالة نادرة) نسجله الآن قبل الاضافة
            if not cookies.get("user"):
                cookies["user"] = cookie_user
                cookies["login_time"] = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
                cookies.save()
            add_time_in(cookie_user)
    with col2:
        if st.button(f"{cookie_user} ⛔ OUT"):
            add_time_out(cookie_user)

