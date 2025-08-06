import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "time_sheet"
supabase: Client = create_client(url, key)

# بيانات الدخول (ممكن تيجي لاحقًا من Supabase)
users = {
    "زياد": "1111",
    "عمر": "2222",
    "علي": "3333",
    "يوسف": "4444"
}

# تهيئة حالة الجلسة
if "user" not in st.session_state:
    st.session_state["user"] = None
if "login_time" not in st.session_state:
    st.session_state["login_time"] = None

# دالة التحقق من مرور أسبوع
def session_expired():
    if st.session_state["login_time"] is None:
        return True
    return datetime.now() - st.session_state["login_time"] > timedelta(days=7)

# تسجيل الخروج اليدوي
if st.sidebar.button("🔒 تسجيل الخروج"):
    st.session_state["user"] = None
    st.session_state["login_time"] = None
    st.success("تم تسجيل الخروج")

# دالة تسجيل الدخول
def login():
    st.title("🔐 تسجيل الدخول")
    username = st.text_input("ادخل اسمك بالعربي")
    password = st.text_input("ادخل الكود السري", type="password")
    if st.button("دخول"):
        if username in users and users[username] == password:
            st.session_state["user"] = username
            st.session_state["login_time"] = datetime.now()
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

# -------------------------
# التشغيل الفعلي

# لو الجلسة انتهت أو لم يبدأ
if st.session_state["user"] is None or session_expired():
    login()
else:
    current_user = st.session_state["user"]
    st.title(f"📋 واجهة الحضور والانصراف - {current_user}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"{current_user} ✅ IN"):
            add_time_in(current_user)
    with col2:
        if st.button(f"{current_user} ⛔ OUT"):
            add_time_out(current_user)
