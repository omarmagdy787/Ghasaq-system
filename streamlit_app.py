import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd

# ===== تحميل ملف .env =====
load_dotenv()

url = os.getenv("url")
key = os.getenv("key")
TABLE_NAME = "main_tasks"

# ===== التحقق من البيانات =====
if not url or not key:
    st.error("❌ تأكد من وجود url و key في ملف .env")
    st.stop()

# ===== إنشاء الاتصال =====
supabase: Client = create_client(url, key)

# ===== تحميل الفرق =====
@st.cache_data
def load_teams():
    try:
        response = supabase.table("teams").select("id, name").execute()
        results = response.data
        return {team["name"]: team["id"] for team in results}
    except Exception as e:
        st.error(f"تعذر تحميل الفرق: {e}")
        return {}

teams_dict = load_teams()

# ===== تحميل الأعمدة =====
@st.cache_data
def get_columns():
    try:
        response = supabase.table(TABLE_NAME).select("*").limit(1).execute()
        data = response.data

        if data and isinstance(data, list) and len(data) > 0:
            return list(data[0].keys())
        else:
            # نجيب الأعمدة من التعريف نفسه كـ fallback
            st.warning("⚠️ لا توجد بيانات حاليًا، جاري جلب الأعمدة من التعريف.")
            # جلب الأعمدة من التعريف (لو supabase بتدعم describe)
            # أو fallback يدوي:
            return ["id", "title", "description", "status", "team_id"]  # ✏️ عدلها حسب أعمدة جدولك

    except Exception as e:
        st.error("تعذر جلب الأعمدة من Supabase")
        st.exception(e)
        st.stop()

columns = get_columns()

# ===== إدخال البيانات =====
st.title("📋 نظام المهام")

with st.form("task_form"):
    inputs = {}
    for col in columns:
        if col == "team_id":
            continue
        inputs[col] = st.text_input(col)

    team_name = st.selectbox("الفريق", list(teams_dict.keys()))
    submitted = st.form_submit_button("إضافة")

    if submitted:
        values = {col: inputs[col] for col in inputs}
        values["team_id"] = teams_dict.get(team_name)
        try:
            supabase.table(TABLE_NAME).insert(values).execute()
            st.success("✅ تم إضافة المهمة بنجاح")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Insert Error: {e}")

# ===== عرض البيانات =====
st.subheader("📑 المهام المسجلة")
try:
    response = supabase.table(TABLE_NAME).select("*").execute()
    data = response.data

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        selected_row = st.selectbox("اختر مهمة للتعديل أو الحذف (بـ ID)", df[columns[0]].tolist())

        with st.expander("✏️ تعديل / 🗑️ حذف"):
            edit_data = {}
            for col in columns:
                if col == "team_id":
                    continue
                old_val = df[df[columns[0]] == selected_row][col].values[0]
                edit_data[col] = st.text_input(f"{col} (قديم: {old_val})", value=old_val)

            new_team = st.selectbox("الفريق الجديد", list(teams_dict.keys()), index=0)
            update_btn = st.button("تعديل")
            delete_btn = st.button("حذف")

            if update_btn:
                updates = {col: edit_data[col] for col in edit_data}
                updates["team_id"] = teams_dict.get(new_team)
                try:
                    supabase.table(TABLE_NAME).update(updates).eq(columns[0], selected_row).execute()
                    st.success("✅ تم التعديل بنجاح")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Update Error: {e}")

            if delete_btn:
                try:
                    supabase.table(TABLE_NAME).delete().eq(columns[0], selected_row).execute()
                    st.success("🗑️ تم حذف المهمة بنجاح")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Delete Error: {e}")

    else:
        st.info("لا توجد مهام بعد.")

except Exception as e:
    st.error(f"Load Error: {e}")


