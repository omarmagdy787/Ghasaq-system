import streamlit as st
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ---------- إعداد Supabase ----------
url = st.secrets["url"]
key = st.secrets["key"]
TABLE_NAME = "main_tasks"
supabase = create_client(url, key)

# ---------- تحديث تلقائي كل دقيقة ----------
st_autorefresh(interval=60 * 1000, key="refresh")

# ---------- العنوان ----------
st.markdown("<h2 style='text-align: center;'>Outsourcing Tasks</h2>", unsafe_allow_html=True)

# ---------- جلب البيانات من Supabase ----------
response = supabase.table(TABLE_NAME).select("*").execute()
data = response.data

# ---------- تحويل إلى DataFrame ----------
df = pd.DataFrame(data)

# ---------- فلترة فقط المهام التي فيها category = outsourcing ----------
if not df.empty and "category" in df.columns:
    df_outsourcing = df[df["category"] == "outsourcing"]

    # تحديد الأعمدة المطلوبة فقط
    required_columns = ["id", "number", "task_name", "description", "from", "to", "check"]
    df_outsourcing = df_outsourcing[required_columns]

    # ---------- إعداد AgGrid ----------
    gb = GridOptionsBuilder.from_dataframe(df_outsourcing)
    gb.configure_column("check", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Yes', 'No']})
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    st.markdown("### ✍️ اضغط على الخلية لتعديل عمود check:")
    grid_response = AgGrid(
        df_outsourcing,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        fit_columns_on_grid_load=True,
        use_container_width=True,
        enable_enterprise_modules=False
    )

    updated_df = grid_response["data"]

    if st.button("🔁 تحديث البيانات"):
        for index, row in updated_df.iterrows():
            supabase.table(TABLE_NAME).update({"check": row["check"]}).eq("id", row["id"]).execute()
        st.success("✅ تم تحديث البيانات بنجاح!")

else:
    st.warning("لا توجد بيانات أو العمود 'category' غير موجود.")




