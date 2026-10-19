import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

# --- 1. إعدادات الصفحة والتصميم العام ---
st.set_page_config(
    page_title="Company HR Hub - المنصة المركزية الإدارية",
    page_icon="🏢",
    layout="centered"
)

# حقن أكواد CSS لتصميم أزرق مؤسساتي فاخر ومتناسق
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
            background-color: #f8fafc;
        }
        
        /* تخصيص الأزرار باللون الأزرق الاحترافي */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            padding: 0.6rem 1rem;
            box-shadow: 0 1px 2px 0 rgba(37, 99, 235, 0.2);
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #1d4ed8;
            color: #ffffff;
        }
        
        /* تنسيق الهيدر */
        .main-header {
            text-align: center;
            padding: 15px 0 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بـ Supabase ---
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    st.error("⚠️ خطأ في الإعدادات: يرجى التأكد من ملف البيئة .env")
    st.stop()

try:
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"❌ تعذر الاتصال بقاعدة البيانات: {e}")
    st.stop()

# --- 3. الهيدر الرسمي الاحترافي ---
st.markdown("""
    <div class='main-header'>
        <h2 style='color: #1e3a8a; font-weight: 700; margin-bottom: 4px;'>Company HR Hub</h2>
        <p style='color: #64748b; font-size: 14px; margin: 0;'>المنصة المركزية الموحدة للتحقق وإدارة سجلات الموظفين بين الفروع</p>
    </div>
    <hr style='margin: 15px 0 25px 0; border-color: #e2e8f0;'>
""", unsafe_allow_html=True)

# --- 4. شاشة تسجيل الدخول ---
if "user_role" not in st.session_state:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #1e3a8a; font-size: 16px; margin-bottom: 15px;'>تسجيل دخول الإدارة</h4>", unsafe_allow_html=True)
            
            email = st.text_input("البريد الإلكتروني للإدارة")
            password = st.text_input("كلمة المرور", type="password")
            
            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
            
            if st.button("تسجيل الدخول", use_container_width=True):
                if not email.strip() or not password:
                    st.warning("يرجى إدخال البريد الإلكتروني وكلمة المرور.")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })

                        if response.user:
                            user_email = email.strip().lower()
                            if "owner" in user_email or "director" in user_email or "admin" in user_email or "general" in user_email:
                                st.session_state["user_role"] = "المدير العام"
                            elif "oran" in user_email:
                                st.session_state["user_role"] = "وهران"
                            elif "eulma" in user_email:
                                st.session_state["user_role"] = "العلمة"
                            else:
                                st.session_state["user_role"] = "مدير معتمد"
                            st.rerun()

                    except Exception:
                        st.error("❌ بيانات الدخول غير صحيحة.")

# --- 5. لوحة التحكم بعد تسجيل الدخول ---
if "user_role" in st.session_state:
    current_role = st.session_state["user_role"]
    
    # شريط الحالة العلوي
    col_status, col_logout = st.columns([3, 1])
    with col_status:
        if current_role == "المدير العام":
            status_text = "المدير العام (إشراف ومتابعة شاملة)"
        else:
            status_text = f"مدير فرع {current_role}"
            
        st.markdown(f"<div style='background-color: #eff6ff; padding: 10px 15px; border-radius: 8px; color: #1e40af; font-size: 13px; border-right: 4px solid #2563eb;'>النظام النشط: <b>{status_text}</b></div>", unsafe_allow_html=True)
    with col_logout:
        if st.button("تسجيل الخروج", use_container_width=True):
            del st.session_state["user_role"]
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- واجهة المدير العام (إشراف وتقارير شاملة) ---
    if current_role == "المدير العام":
        with st.container(border=True):
            st.subheader("📊 لوحة متابعة الإدارة العليا (السجل المركزي العام)")
            st.write("مرحباً بك. تتيح لك هذه اللوحة تتبع جميع السجلات والقرارات الإدارية الموثقة عبر كافة فروع الشركة.")

            try:
                res = supabase.table("employees").select("*").order("id", desc=True).execute()
                all_records = res.data

                total_count = len(all_records)
                oran_count = sum(1 for r in all_records if "وهران" in str(r.get('notes', '')))
                eulma_count = sum(1 for r in all_records if "العلمة" in str(r.get('notes', '')))

                col_st1, col_st2, col_st3 = st.columns(3)
                with col_st1:
                    st.metric("إجمالي السجلات المركزية", total_count)
                with col_st2:
                    st.metric("سجلات فرع وهران", oran_count)
                with col_st3:
                    st.metric("سجلات فرع العلمة", eulma_count)

                st.markdown("<hr style='margin: 20px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
                st.subheader("📋 كافة السجلات والقرارات المسجلة في الشركة")

                if all_records:
                    for item in all_records:
                        st.markdown(f"""
                            <div style='background-color: #f8fafc; color: #0f172a; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin-top: 10px; font-size: 14px;'>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                                    <span><b>الاسم الكامل:</b> {item.get('full_name')}</span>
                                    <span><b>رقم التعريف:</b> {item.get('employee_number')}</span>
                                </div>
                                <div style='margin-bottom: 6px;'><b>القسم:</b> {item.get('department')} | <b>الهاتف:</b> {item.get('phone')}</div>
                                <div style='color: #1e3a8a; font-weight: 600; background-color: #eff6ff; padding: 8px; border-radius: 4px; margin-top: 6px;'>
                                    {item.get('notes')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد أي سجلات موثقة حتى الآن في النظام.")

            except Exception as e:
                st.error(f"تعذر جلب البيانات: {e}")

    # --- واجهة مدراء الفروع (بحث + توثيق) ---
    else:
        tab_search, tab_add = st.tabs(["🔍 محرك التحقق والبحث", "➕ تسجيل موظف أو قرار جديد"])

        with tab_search:
            with st.container(border=True):
                st.subheader("التحقق من سجلات المتقدمين")
                st.write("أدخل رقم الهوية أو الاسم الكامل للتحقق من وجود أي سجل إداري سابق:")

                search_query = st.text_input("بحث برقم الهوية أو الاسم...", key="search_input_box")

                if st.button("بحث في السجلات", use_container_width=True):
                    if search_query.strip():
                        try:
                            res = supabase.table("employees").select("*").or_(
                                f"employee_number.eq.{search_query.strip()},full_name.ilike.%{search_query.strip()}%"
                            ).execute()

                            records = res.data
                            if records:
                                st.markdown(f"<div style='background-color: #eff6ff; border: 1px solid #bfdbfe; border-right: 4px solid #2563eb; padding: 12px 15px; border-radius: 6px; margin-top: 15px; color: #1e40af; font-size: 14px;'>"
                                            f"📋 <b>تنبيه إداري:</b> تم العثور على ({len(records)}) سجل سابق مرتبط بهذا المتقدم."
                                            f"</div>", unsafe_allow_html=True)
                                
                                for item in records:
                                    st.markdown(f"""
                                        <div style='background-color: #ffffff; color: #0f172a; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-top: 12px; font-size: 14px;'>
                                            <div style='margin-bottom: 8px;'><span style='color: #64748b; margin-left: 8px;'>الاسم الكامل:</span> <b>{item.get('full_name')}</b></div>
                                            <div style='margin-bottom: 8px;'><span style='color: #64748b; margin-left: 8px;'>رقم التعريف:</span> <b>{item.get('employee_number')}</b></div>
                                            <div style='margin-bottom: 8px;'><span style='color: #64748b; margin-left: 8px;'>القسم السابق:</span> {item.get('department')}</div>
                                            <div style='margin-bottom: 8px;'><span style='color: #64748b; margin-left: 8px;'>رقم الهاتف:</span> {item.get('phone')}</div>
                                            <hr style='margin: 10px 0; border-top: 1px solid #f1f5f9;'>
                                            <div><span style='color: #64748b;'>تفاصيل القرار الإداري / الملاحظات:</span></div>
                                            <div style='color: #1e3a8a; font-weight: 600; margin-top: 4px; background-color: #f8fafc; padding: 8px; border-radius: 4px;'>{item.get('notes')}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                
                                st.markdown("<div style='margin-top: 12px; font-size: 12px; color: #64748b;'>ملاحظة: هذا السجل للاسترشاد الداخلي، والقرار النهائي بقبول أو رفض التوظيف يرجع لتقدير مدير الفرع.</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='background-color: #f0fdf4; border: 1px solid #bbf7d0; border-right: 4px solid #16a34a; padding: 12px 15px; border-radius: 6px; margin-top: 15px; color: #166534; font-size: 14px;'>"
                                            f"✅ <b>السجل نظيف:</b> لم يتم العثور على أي موانع أو قرارات سابقة لهذا المتقدم في النظام."
                                            f"</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"حدث خطأ أثناء الاتصال: {e}")
                    else:
                        st.warning("الرجاء إدخال اسم أو رقم للبحث.")

        with tab_add:
            with st.container(border=True):
                st.subheader("توثيق سجل موظف جديد")
                st.write("أدخل بيانات العامل بدقة لإضافتها إلى قاعدة البيانات المركزية المشتركة:")

                with st.form("employee_form_pro", clear_on_submit=True):
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        full_name = st.text_input("الاسم الكامل للموظف")
                        department = st.text_input("القسم أو المنصب الوظيفي")
                    with col_f2:
                        employee_id = st.text_input("رقم الموظف / رقم التعريف الوطنية")
                        phone = st.text_input("رقم الهاتف")
                    
                    notes = st.text_area("تفاصيل القرار الإداري / سبب إنهاء الخدمة")

                    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("حفظ في السجل المركزي", use_container_width=True)

                    if submitted:
                        if full_name.strip() and employee_id.strip():
                            try:
                                branch_note = f"فرع {current_role}: {notes.strip() if notes.strip() else 'تم الإنهاء دون ملاحظات إضافية'}"

                                supabase.table("employees").insert({
                                    "full_name": full_name.strip(),
                                    "employee_number": employee_id.strip(),
                                    "department": department.strip(),
                                    "phone": phone.strip(),
                                    "notes": branch_note
                                }).execute()

                                st.success(f"تم حفظ وتوثيق سجل الموظف ({full_name}) بنجاح.")

                            except Exception as e:
                                st.error(f"تعذر الحفظ. الخطأ: {e}")
                        else:
                            st.warning("⚠️ يرجى إدخال الاسم الكامل ورقم التعريف على الأقل.")