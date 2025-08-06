import streamlit as st
from datetime import date, datetime
from supabase import create_client, Client
from zoneinfo import ZoneInfo

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "time_sheet"
supabase: Client = create_client(url, key)

# تسجيل الدخول
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        st.error("فشل تسجيل الدخول")
        st.write(e)
        return None

# تسجيل وقت الدخول
def add_time_in(name, user_id):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    data = {
        "name": name,
        "user_id": user_id,  # مهم جدا لـ RLS policies
        "date": str(date.today()),
        "from": now,
        "project": "Default"
    }
    try:
        res = supabase.table(TABLE_NAME).insert(data).execute()
        if res.status_code == 201:
            st.success(f"{name} ✅ تم تسجيل وقت الدخول")
        else:
            st.error(f"❌ خطأ أثناء تسجيل الدخول: {res.data}")
    except Exception as e:
        st.error("❌ حدث خطأ أثناء تسجيل الدخول")
        st.write(e)

# تسجيل وقت الانصراف
def add_time_out(name, user_id):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    try:
        response = supabase.table(TABLE_NAME)\
            .select("id")\
            .eq("name", name)\
            .eq("user_id", user_id)\
            .eq("date", str(date.today()))\
            .order("id", desc=True)\
            .limit(1).execute()
        
        if response.data:
            row_id = response.data[0]["id"]
            update_response = supabase.table(TABLE_NAME)\
                .update({"to": now})\
                .eq("id", row_id).execute()
            
            if update_response.status_code == 204:
                st.success(f"{name} ⛔ تم تسجيل الانصراف")
            else:
                st.error(f"❌ خطأ أثناء تسجيل الانصراف: {update_response.data}")
        else:
            st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")
    except Exception as e:
        st.error("❌ حدث خطأ أثناء تسجيل الانصراف")
        st.write(e)

# -----------------------------
# واجهة المستخدم

if "session" not in st.session_state:
    st.session_state.session = None
if "user" not in st.session_state:
    st.session_state.user = None

st.title("📋 واجهة الحضور والانصراف")

# لو مش مسجل دخول، نعرض الفورم
if not st.session_state.session:
    with st.form("login_form"):
        st.subheader("🔐 تسجيل الدخول")
        email = st.text_input("📧 البريد الإلكتروني")
        password = st.text_input("🔑 كلمة السر", type="password")
        submitted = st.form_submit_button("تسجيل الدخول")
        if submitted:
            auth_response = login_user(email, password)
            if auth_response and auth_response.session:
                st.session_state.session = auth_response.session
                st.session_state.user = auth_response.user
                st.success("✅ تم تسجيل الدخول")
                st.experimental_rerun()
else:
    user = st.session_state.user
    access_token = st.session_state.session.access_token
    user_id = user.id  # UID من Supabase
    name = user.user_metadata.get("name") or user.email.split("@")[0]

    st.success(f"👋 مرحبًا، {name}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ IN"):
            add_time_in(name, user_id)

    with col2:
        if st.button("⛔ OUT"):
            add_time_out(name, user_id)

    if st.button("🚪 تسجيل الخروج"):
        st.session_state.session = None
        st.session_state.user = None
        st.experimental_rerun()



