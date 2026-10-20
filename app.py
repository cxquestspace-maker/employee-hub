import streamlit as st
import os
from datetime import date
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Company HR Hub - Executive Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تحميل المتغيرات السرية بشكل آمن محلياً وعلى السحابة
load_dotenv()
try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ لم يتم العثور على مفاتيح الاتصال بقاعدة البيانات. يرجى ضبط Secrets في إعدادات المنصة.")
    st.stop()

# الاتصال بقاعدة بيانات Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. أنماط التصميم المؤسسي وتوجيه المحتوى باللغة العربية (RTL)
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        border-radius: 8px;
        height: 2.8em;
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        text-align: right !important;
    }
    .employee-card {
        background-color: white;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 18px;
        border-right: 6px solid #2563eb;
        border-left: 1px solid #e2e8f0;
        border-top: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        direction: rtl;
    }
    .branch-badge {
        background-color: #e0e7ff;
        color: #3730a3;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        justify-content: flex-start;
    }
</style>
""", unsafe_allow_html=True)

# 4. إدارة حالة الجلسة (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# 5. واجهة تسجيل الدخول المؤسسية
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Company HR Hub</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>المنصة المركزية الموحدة لإدارة الموظفين والتدقيق بين الفروع</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("تسجيل دخول الإدارة")
            email = st.text_input("البريد الإلكتروني للإدارة")
            password = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("تسجيل الدخول الآمن")
            
            if submit:
                if email and password:
                    try:
                        auth_response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.rerun()
                    except Exception as e:
                        st.error("خطأ في بيانات الدخول. يرجى التأكد من البريد أو كلمة المرور.")
                else:
                    st.warning("يرجى ملء جميع الحقول المطلوبة.")
    st.stop()

# 6. تحديد دور المستخدم والفرع التلقائي
user_email = st.session_state.user_email.lower()
is_owner = any(keyword in user_email for keyword in ["owner", "director", "admin", "general"])
current_branch = "وهران" if "oran" in user_email else ("العلمة" if "eulma" in user_email else "الإدارة العامة")

# دالة مساعدة لاستخراج اسم الفرع من بيانات الموظف تلقائياً
def extract_branch(emp):
    dept = str(emp.get("department") or "")
    notes = str(emp.get("notes") or "")
    if "وهران" in dept or "وهران" in notes or "oran" in notes.lower():
        return "فرع وهران"
    elif "العلمة" in dept or "العلمة" in notes or "eulma" in notes.lower():
        return "فرع العلمة"
    return dept if dept else "غير محدد"

# شريط التنقل العلوي
col_user, col_logout = st.columns([5, 1])
with col_user:
    st.markdown(f"👤 مسجل الدخول كـ: **{st.session_state.user_email}** | **الفرع الحالي: {current_branch}**")
with col_logout:
    if st.button("خروج"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

st.markdown("---")

# 7. لوحة تحكم المدير العام الاحترافية (Executive Portal)
if is_owner:
    st.title("📊 لوحة التحكم القيادية التنفيذية")
    st.write("إدارة مركزية متكاملة ومتابعة حية لسجلات الفروع وصلاحيات الإشراف.")

    try:
        res = supabase.table("employees").select("*").execute()
        employees = res.data if res.data else []
        
        oran_count = sum(1 for e in employees if extract_branch(e) == "فرع وهران")
        eulma_count = sum(1 for e in employees if extract_branch(e) == "فرع العلمة")

        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي السجلات المركزية", len(employees))
        m2.metric("سجلات فرع وهران", oran_count)
        m3.metric("سجلات فرع العلمة", eulma_count)
        
        st.markdown("---")

        exec_tab1, exec_tab2, exec_tab3 = st.tabs([
            "📑 التدقيق المركزي للسجلات", 
            "🔍 بحث متقدم في الشبكة", 
            "⚙️ لوحة الإشراف والحذف الآمن"
        ])

        with exec_tab1:
            st.subheader("سجلات الموظفين المسجلة عبر كافة الفروع")
            if employees:
                for emp in employees:
                    b_name = extract_branch(emp)
                    notes_val = emp.get('notes') or "لا توجد ملاحظات إضافية"
                    st.markdown(f"""
                    <div class="employee-card">
                        <span class="branch-badge">🏢 مكان العمل: {b_name}</span>
                        <h3 style="color: #1e3a8a; margin-top: 5px; margin-bottom: 10px;">👤 {emp.get('full_name', 'بدون اسم')}</h3>
                        <p style="margin: 4px 0; color: #334155; font-size: 1rem;"><b>رقم التعريف الوطني (NIN):</b> {emp.get('employee_number', 'غير متوفر')}</p>
                        <p style="margin: 4px 0; color: #334155; font-size: 1rem;"><b>الهاتف:</b> {emp.get('phone', 'غير محدد')}</p>
                        <hr style="margin: 8px 0; border: none; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 4px 0; color: #0f172a; background-color: #f1f5f9; padding: 10px; border-radius: 6px;"><b>تفاصيل السجل والملاحظات:</b><br>{notes_val}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد سجلات مسجلة في النظام حتى الآن.")

        with exec_tab2:
            st.subheader("البحث الشامل في قاعدة البيانات")
            exec_search = st.text_input("ابحث بالاسم أو رقم التعريف الوطني أو الفرع:")
            if exec_search:
                res_s1 = supabase.table("employees").select("*").ilike("full_name", f"%{exec_search}%").execute()
                res_s2 = supabase.table("employees").select("*").ilike("employee_number", f"%{exec_search}%").execute()
                res_s3 = supabase.table("employees").select("*").ilike("notes", f"%{exec_search}%").execute()
                res_s4 = supabase.table("employees").select("*").ilike("department", f"%{exec_search}%").execute()
                
                merged_res = {e['id']: e for e in ((res_s1.data or []) + (res_s2.data or []) + (res_s3.data or []) + (res_s4.data or []))}
                found_list = list(merged_res.values())
                
                if found_list:
                    st.success(f"تم العثور على {len(found_list)} نتيجة مطابقة:")
                    for emp in found_list:
                        b_name = extract_branch(emp)
                        st.markdown(f"""
                        <div class="employee-card">
                            <span class="branch-badge">🏢 مكان العمل: {b_name}</span>
                            <h3 style="color: #1e3a8a; margin-top: 5px; margin-bottom: 10px;">👤 {emp.get('full_name')}</h3>
                            <p style="margin: 4px 0; color: #334155;"><b>رقم التعريف الوطني (NIN):</b> {emp.get('employee_number')}</p>
                            <p style="margin: 4px 0; color: #0f172a; background-color: #f1f5f9; padding: 10px; border-radius: 6px;"><b>الملاحظات والبيانات:</b><br>{emp.get('notes') or 'لا توجد ملاحظات'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد نتائج مطابقة لبحثك.")

        with exec_tab3:
            st.subheader("إدارة وحذف السجلات الخاطئة أو التجريبية")
            st.warning("⚠️ تنبيه إداري: عملية الحذف نهائية ولا يمكن التراجع عنها.")
            
            if employees:
                emp_choices = {
                    f"الاسم: {e.get('full_name', 'بدون اسم')} | مكان العمل: {extract_branch(e)} | NIN: {e.get('employee_number', 'غ/م')}": e.get('id')
                    for e in employees
                }
                
                selected_label = st.selectbox("اختر السجل المراد إدارته وحذفه:", options=list(emp_choices.keys()))
                
                col_del1, col_del2 = st.columns([1, 3])
                with col_del1:
                    confirm_delete = st.checkbox("تأكيد صلاحية الحذف")
                
                if confirm_delete:
                    if st.button("🗑️ حذف السجل نهائياً من النظام", type="primary"):
                        target_id = emp_choices[selected_label]
                        try:
                            supabase.table("employees").delete().eq("id", target_id).execute()
                            st.success("تم حذف السجل بنجاح وتحديث القاعدة المركزية!")
                            st.rerun()
                        except Exception as del_err:
                            st.error(f"حدث خطأ أثناء الحذف: {del_err}")
                else:
                    st.info("يرجى تحديد مربع 'تأكيد صلاحية الحذف' لتفعيل زر الحذف الآمن.")
            else:
                st.info("لا توجد سجلات متاحة للإدارة أو الحذف.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {e}")

# 8. لوحة تحكم مدراء الفروع (Branch Managers View)
else:
    branch_name = current_branch
    st.title(f"🏢 لوحة إدارة فرع {branch_name}")
    
    tab1, tab2, tab3 = st.tabs([
        "🔍 البحث والتحقق السريع", 
        "➕ تسجيل موظف جديد", 
        "✏️ إدارة وتعديل / حذف سجلات الفرع"
    ])
    
    # التبويب الأول: البحث والتحقق
    with tab1:
        st.subheader("التحقق الفوري قبل التوظيف")
        search_term = st.text_input("أدخل الاسم الكامل أو رقم التعريف الوطني للبحث:")
        
        if search_term:
            try:
                res_name = supabase.table("employees").select("*").ilike("full_name", f"%{search_term}%").execute()
                res_num = supabase.table("employees").select("*").ilike("employee_number", f"%{search_term}%").execute()
                
                results_dict = {e['id']: e for e in ((res_name.data or []) + (res_num.data or []))}
                results = list(results_dict.values())
                
                if results:
                    st.warning(f"⚠️ تنبيه: تم العثور على ({len(results)}) سجل سابـق لهذا الموظف في الشبكة المركزية:")
                    for emp in results:
                        b_name = extract_branch(emp)
                        st.markdown(f"""
                        <div class="employee-card">
                            <span class="branch-badge">🏢 مكان العمل السابق: {b_name}</span>
                            <h3 style="color: #1e3a8a; margin-top: 5px; margin-bottom: 10px;">👤 {emp.get('full_name')}</h3>
                            <p style="margin: 4px 0; color: #334155;"><b>رقم التعريف الوطني (NIN):</b> {emp.get('employee_number')}</p>
                            <p style="margin: 4px 0; color: #0f172a; background-color: #f1f5f9; padding: 10px; border-radius: 6px;"><b>تفاصيل السجل والملاحظات:</b><br>{emp.get('notes') or 'لا توجد ملاحظات'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ نظيف: لم يتم العثور على أي سجلات سابقة لهذا الموظف.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء البحث: {e}")

    # التبويب الثاني: تسجيل موظف جديد (الملاحظات اختيارية)
    with tab2:
        st.subheader(f"تسجيل بيانات موظف جديد - فرع {branch_name}")
        st.write("📌 **تنبيه:** الحقول المتبوعة بـ (*) إجبارية. الملاحظات اختيارية.")
        
        with st.form("add_employee_form"):
            full_name = st.text_input("الاسم الكامل للموظف *")
            emp_number = st.text_input("رقم التعريف الوطني (NIN) *")
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("تاريخ بداية العمل *", value=date.today())
            with col_d2:
                end_date = st.date_input("تاريخ نهاية العمل *", value=date.today())
                
            phone = st.text_input("رقم الهاتف (اختياري)")
            notes = st.text_area("سبب مغادرة العمل / ملاحظات إدارية هامة (اختياري)")
            
            submit_emp = st.form_submit_button("حفظ السجل في قاعدة البيانات المركزية")
            
            if submit_emp:
                if not full_name.strip():
                    st.warning("⚠️ يرجى إدخال الاسم الكامل للموظف.")
                elif not emp_number.strip():
                    st.warning("⚠️ يرجى إدخال رقم التعريف الوطني (NIN).")
                else:
                    try:
                        check_exist = supabase.table("employees").select("*").eq("employee_number", emp_number.strip()).execute()
                        
                        if check_exist.data and len(check_exist.data) > 0:
                            existing_emp = check_exist.data[0]
                            st.error(f"⛔ تنبيه تكرار: العامل صاحب رقم التعريف الوطني ({emp_number}) مسجل مسبقاً في النظام باسم '{existing_emp.get('full_name')}'!")
                        else:
                            dept_value = f"فرع {branch_name}"
                            user_notes_text = f" | الملاحظات: {notes.strip()}" if notes.strip() else ""
                            full_notes = f"[{dept_value}] | فترة العمل: من {start_date} إلى {end_date}{user_notes_text}"
                            
                            data = {
                                "full_name": full_name.strip(),
                                "employee_number": emp_number.strip(),
                                "department": dept_value,
                                "phone": phone.strip() if phone else "غير محدد",
                                "notes": full_notes
                            }
                            supabase.table("employees").insert(data).execute()
                            st.success("تم إضافة السجل بنجاح وإتاحته للشبكة المركزية الفورية!")
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء حفظ البيانات: {e}")

    # التبويب الثالث: إدارة وتعديل / حذف سجلات الفرع
    with tab3:
        st.subheader(f"إدارة، تعديل أو حذف سجلات موظفي فرع {branch_name}")
        try:
            res_all = supabase.table("employees").select("*").execute()
            all_emps = res_all.data if res_all.data else []
            
            branch_emps = [e for e in all_emps if extract_branch(e) == f"فرع {branch_name}"]
            
            if branch_emps:
                branch_emp_choices = {
                    f"الاسم: {e.get('full_name')} | NIN: {e.get('employee_number')}": e
                    for e in branch_emps
                }
                
                selected_choice = st.selectbox("اختر العامل للتعديل أو الحذف:", options=list(branch_emp_choices.keys()))
                target_emp = branch_emp_choices[selected_choice]
                
                col_edit, col_del = st.columns(2)
                
                with col_edit:
                    st.write("### ✏️ تعديل السجل والملاحظات")
                    with st.form("edit_branch_employee_form"):
                        edited_name = st.text_input("الاسم الكامل *", value=target_emp.get('full_name', ''))
                        edited_nin = st.text_input("رقم التعريف الوطني (NIN) *", value=target_emp.get('employee_number', ''))
                        edited_phone = st.text_input("رقم الهاتف", value=target_emp.get('phone', ''))
                        edited_notes = st.text_area("تعديل تفاصيل الملاحظات والتواريخ", value=target_emp.get('notes', ''))
                        
                        submit_edit = st.form_submit_button("حفظ التعديلات والتحديث")
                        
                        if submit_edit:
                            if edited_name and edited_nin:
                                try:
                                    update_data = {
                                        "full_name": edited_name.strip(),
                                        "employee_number": edited_nin.strip(),
                                        "phone": edited_phone.strip(),
                                        "notes": edited_notes.strip()
                                    }
                                    supabase.table("employees").update(update_data).eq("id", target_emp['id']).execute()
                                    st.success("تم تحديث بيانات العامل بنجاح!")
                                    st.rerun()
                                except Exception as edit_err:
                                    st.error(f"حدث خطأ أثناء التعديل: {edit_err}")
                            else:
                                st.warning("يرجى ملء الاسم الكامل ورقم التعريف الوطني.")
                
                with col_del:
                    st.write("### 🗑️ حذف العامل من السجل")
                    st.warning("استخدم هذا الخيار في حال عودة العامل للعمل أو إذا تم إدخاله بالخطأ لتتم إزالته من قائمة الموقوفين.")
                    
                    confirm_branch_del = st.checkbox("تأكيد صلاحية حذف العامل من فرعك")
                    if confirm_branch_del:
                        if st.button("حذف العامل نهائياً من المنصة", type="primary"):
                            try:
                                supabase.table("employees").delete().eq("id", target_emp['id']).execute()
                                st.success("تم حذف العامل وإزالته من النظام بنجاح!")
                                st.rerun()
                            except Exception as d_err:
                                st.error(f"حدث خطأ أثناء الحذف: {d_err}")
                    else:
                        st.info("حدد مربع التأكيد أعلاه لتفعيل زر الحذف النهائي.")
            else:
                st.info(f"لا توجد سجلات مسجلة باسم فرع {branch_name} حالياً.")
        except Exception as err:
            st.error(f"حدث خطأ أثناء جلب سجلات الفرع: {err}")
