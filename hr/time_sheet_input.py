import streamlit as st
from datetime import date, datetime
from supabase import create_client
from zoneinfo import ZoneInfo
import requests

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

# الاتصال بـ Supabase
url = st.secrets["url"]
anon_key = st.secrets["key"]
supabase = create_client(url, anon_key)

# وظيفة تسجيل الدخول
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
def add_time_in(name, user_id, token):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    data = {
        "name": name,
        "user_id": user_id,  # مهم علشان RLS
        "date": str(date.today()),
        "from": now,
        "project": "Default"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": anon_key,
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{url}/rest/v1/time_sheet",
        json=data,
        headers=headers,
    )
    if response.status_code == 201:
        st.success(f"{name} ✅ تم تسجيل وقت الدخول")
    else:
        st.error("❌ خطأ أثناء تسجيل الدخول")
        st.markdown("### 🐞 تفاصيل الخطأ:")
        st.write("🔢 Status Code:", response.status_code)
        st.write("🧾 Response JSON:", response.json())
        st.write("📤 Data Sent:", data)
        st.write("🧾 Headers:", headers)

# تسجيل وقت الانصراف
def add_time_out(name, token):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": anon_key,
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"{url}/rest/v1/time_sheet?select=id&name=eq.{name}&date=eq.{date.today()}&order=id.desc&limit=1",
        headers=headers,
    )
    if response.status_code == 200 and response.json():
        row_id = response.json()[0]["id"]
        update_response = requests.patch(
            f"{url}/rest/v1/time_sheet?id=eq.{row_id}",
            json={"to": now},
            headers=headers,
        )
        if update_response.status_code == 204:
            st.success(f"{name} ⛔ تم تسجيل الانصراف")
        else:
            st.error("❌ خطأ أثناء تسجيل الانصراف")
            st.markdown("### 🐞 تفاصيل الخطأ:")
            st.write("🔢 Status Code:", update_response.status_code)
            st.write("🧾 Response JSON:", update_response.json())
            st.write("📤 Data Sent:", {"to": now})
            st.write("🧾 Headers:", headers)
    else:
        st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")
        st.write("🔍 تفاصيل البحث:", response.status_code, response.text)

# -----------------------------
# واجهة المستخدم

if "session" not in st.session_state:
    st.session_state.session = None
if "user" not in st.session_state:
    st.session_state.user = None

st.title("📋 واجهة الحضور والانصراف")

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
            add_time_in(name, user_id, access_token)

    with col2:
        if st.button("⛔ OUT"):
            add_time_out(name, access_token)

    if st.button("🚪 تسجيل الخروج"):
        st.session_state.session = None
        st.session_state.user = None
        st.experimental_rerun()

        st.session_state.user = None
        st.experimental_rerun()



