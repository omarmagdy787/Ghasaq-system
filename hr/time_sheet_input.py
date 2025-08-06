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

def debug_response(response, data_sent):
    st.write("🔢 Status Code:", response.status_code)
    try:
        st.write("🧾 Response JSON:\n", response.json())
    except Exception:
        st.write("🧾 Response Text:\n", response.text)
    st.write("📤 Data Sent:\n", data_sent)
    st.write("🧾 Headers:\n", response.request.headers)
    st.write("📥 Request URL:\n", response.request.url)

# وظيفة تسجيل وقت الدخول مع كشف الأخطاء
def add_time_in(name, user_id, token):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    data = {
        "name": name,
        "user_id": user_id,  # مهم للـ RLS
        "date": str(date.today()),
        "from": now,
        "project": "Default"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": anon_key,
        "Content-Type": "application/json"
    }
    post_url = f"{url}/rest/v1/time_sheet"  # تأكد اسم الجدول هنا
    st.write(f"📡 إرسال البيانات إلى: {post_url}")

    response = requests.post(post_url, json=data, headers=headers)

    if response.status_code == 201:
        st.success(f"{name} ✅ تم تسجيل وقت الدخول")
    else:
        st.error("❌ خطأ أثناء تسجيل الدخول")
        debug_response(response, data)

# تسجيل وقت الانصراف مع كشف الأخطاء
def add_time_out(name, token):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": anon_key,
    }

    get_url = f"{url}/rest/v1/time_sheet?select=id&name=eq.{name}&date=eq.{date.today()}&order=id.desc&limit=1"
    st.write(f"📡 طلب آخر تسجيل دخول اليوم من: {get_url}")

    response = requests.get(get_url, headers=headers)

    if response.status_code == 200 and response.json():
        row_id = response.json()[0]["id"]
        patch_url = f"{url}/rest/v1/time_sheet?id=eq.{row_id}"
        st.write(f"📡 تحديث سجل الانصراف على: {patch_url}")

        update_response = requests.patch(patch_url, json={"to": now}, headers=headers)

        if update_response.status_code == 204:
            st.success(f"{name} ⛔ تم تسجيل الانصراف")
        else:
            st.error("❌ خطأ أثناء تسجيل الانصراف")
            debug_response(update_response, {"to": now})
    else:
        st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")
        debug_response(response, {})

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
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if auth_response and auth_response.session:
                st.session_state.session = auth_response.session
                st.session_state.user = auth_response.user
                st.success("✅ تم تسجيل الدخول")
                st.experimental_rerun()
            else:
                st.error("❌ فشل تسجيل الدخول")
else:
    user = st.session_state.user
    access_token = st.session_state.session.access_token
    user_id = user.id
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


