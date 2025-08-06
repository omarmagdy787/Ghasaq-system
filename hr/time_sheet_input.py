import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client
from zoneinfo import ZoneInfo  # توقيت مصر

# إعداد الصفحة
st.set_page_config(page_title="Time Sheet", page_icon="📋")

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

# تحضير session state لكلمات السر
if "passwords" not in st.session_state:
    st.session_state.passwords = {}

# زرارين لكل شخص
for person in people:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"{person} ✅ IN"):
            st.session_state[f"{person}_action"] = "in"

    with col2:
        if st.button(f"{person} ⛔ OUT"):
            st.session_state[f"{person}_action"] = "out"

    action = st.session_state.get(f"{person}_action", None)
    
    if action:
        with st.expander(f"🔒 أدخل كلمة السر لـ {person}"):
            pwd = st.text_input(f"كلمة السر لـ {person}", type="password", key=f"{person}_pwd")
            if st.button("تأكيد", key=f"{person}_confirm"):
                # تحقق من الكلمة السرية وحفظها لمدة أسبوع
                if pwd:  # هنا ممكن تضيف تحقق حقيقي لاحقًا
                    if person not in st.session_state.passwords or \
                       datetime.now() > st.session_state.passwords[person]["expires_at"]:
                        
                        st.session_state.passwords[person] = {
                            "password": pwd,
                            "expires_at": datetime.now() + timedelta(days=7)
                        }

                        if action == "in":
                            add_time_in(person)
                        else:
                            add_time_out(person)

                        # نفض المتغير ده بعد العملية
                        st.session_state[f"{person}_action"] = None
                    else:
                        st.info(f"{person} سجل كلمة السر بالفعل ✅")
                else:
                    st.warning("⚠️ من فضلك أدخل كلمة سر")


