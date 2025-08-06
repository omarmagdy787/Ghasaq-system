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

# بيانات الموظفين (كلمة سر + user_id)
employees = {
    "زياد": {"password": "1234", "user_id": "uid_ziad"},
    "عمر": {"password": "5678", "user_id": "uid_omar"},
    "علي": {"password": "abcd", "user_id": "uid_ali"},
    "يوسف": {"password": "efgh", "user_id": "uid_youssef"},
}

# الوظائف
def add_time_in(name, user_id):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    data = {
        "name": name,
        "user_id": user_id,
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

def add_time_out(name, user_id):
    now = datetime.now(ZoneInfo("Africa/Cairo")).isoformat()
    response = supabase.table(TABLE_NAME).select("id").eq("name", name).eq("user_id", user_id).eq("date", str(date.today())).order("id", desc=True).limit(1).execute()
    if response.data:
        row_id = response.data[0]["id"]
        supabase.table(TABLE_NAME).update({"to": now}).eq("id", row_id).execute()
        st.success(f"{name} ⛔ تم تسجيل الانصراف")
    else:
        st.warning(f"⚠️ لا يوجد دخول مسجل اليوم لـ {name}")

# عرض العنوان
st.title("📋 واجهة الحضور والانصراف")

# زرارين لكل شخص
for person, info in employees.items():
    with st.expander(f"{person}"):
        password_input = st.text_input(f"ادخل كلمة السر لـ {person}", type="password", key=f"pw_{person}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"{person} ✅ IN", key=f"in_{person}"):
                if password_input == info["password"]:
                    add_time_in(person, info["user_id"])
                else:
                    st.error("❌ كلمة السر غير صحيحة")
        with col2:
            if st.button(f"{person} ⛔ OUT", key=f"out_{person}"):
                if password_input == info["password"]:
                    add_time_out(person, info["user_id"])
                else:
                    st.error("❌ كلمة السر غير صحيحة")


