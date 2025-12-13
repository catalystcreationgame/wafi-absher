# backend/services/workflow_handler.py
import json
from datetime import datetime
import random
import string

class WorkflowHandler:
    """Handles multi-turn conversation workflows for each service"""
    
    def __init__(self):
        self.sessions = {}
        self.request_numbers = {}
    
    def generate_request_id(self):
        """Generate unique request ID"""
        return f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    def get_session(self, user_id):
        """Get or create user session"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "service": None,
                "step": 0,
                "data": {},
                "history": [],
                "created_at": datetime.now(),
                "request_id": None
            }
        return self.sessions[user_id]
    
    def handle_photo_change(self, user_input, session):
        """Handle: تغيير صورة الاقامة"""
        step = session.get("step", 0)
        
        if step == 0:
            session["step"] = 1
            return {
                "response": "وافي ابشر 🤖 بيشيك الصوره، الصوره مطابقه للشروط والاحكام، حاب انك تأكد اني اغير الصوره؟",
                "requires_confirmation": True,
                "next_step": "تأكيد التغيير"
            }
        elif step == 1:
            if "ايه" in user_input.lower() or "تمام" in user_input.lower():
                session["step"] = 2
                request_id = self.generate_request_id()
                session["request_id"] = request_id
                return {
                    "response": f"✅ تم تغيير الصوره بنجاح بالرقم: {request_id}",
                    "success": True,
                    "request_id": request_id
                }
            else:
                return {
                    "response": "تمام، تم الالغاء",
                    "cancelled": True
                }
    
    def handle_name_change(self, user_input, session):
        """Handle: تغيير الاسم الاول"""
        step = session.get("step", 0)
        
        if step == 0:
            # Extract new name from user input
            session["new_name"] = user_input.replace("بغيت", "").replace("اغير", "").replace("الى", "").strip()
            session["step"] = 1
            return {
                "response": f"تمام، شيكت الاسم وطلع مطابق للمواصفات، هل تقدر تاكد لي تغيير الاسم الى {session['new_name']}؟",
                "requires_confirmation": True,
                "next_step": "التأكيد النهائي"
            }
        elif step == 1:
            if "ايه" in user_input.lower() or "تأكد" in user_input.lower():
                session["step"] = 2
                request_id = self.generate_request_id()
                session["request_id"] = request_id
                return {
                    "response": f"✅ تمام، تم رفع طلب تغيير الاسم بنجاح بالرقم: {request_id}",
                    "success": True,
                    "request_id": request_id
                }
    
    def handle_license_renewal(self, user_input, session):
        """Handle: تجديد الرخصة"""
        step = session.get("step", 0)
        
        if step == 0:
            session["step"] = 1
            return {
                "response": "تمام، حاب كم المده؟ (سنتين، خمسه سنين، او عشره سنين)",
                "options": ["سنتين", "خمسه", "عشره"],
                "requires_selection": True
            }
        elif step == 1:
            session["duration"] = user_input
            session["step"] = 2
            return {
                "response": f"حبيت ااكد الطلب معك، بغيت تجدد الرخصه لمدة {user_input} صحيح؟ هل اصدر لك فاتوره سداد؟",
                "requires_confirmation": True
            }
        elif step == 2:
            if "ايه" in user_input.lower():
                session["step"] = 3
                invoice_id = self.generate_request_id()
                return {
                    "response": f"✅ تمام، اصدرت لك فاتوره برقم {invoice_id}. في حال سدادها بلغني",
                    "invoice_id": invoice_id,
                    "requires_payment": True
                }
        elif step == 3:
            if "تمام" in user_input.lower() or "سددت" in user_input.lower():
                session["step"] = 4
                return {
                    "response": "🎉 يعطيك العافيه! هل حاب نوصلك اياها؟ (اكتب بيانات العنوان: المنطقه، المدينه، الشارع)",
                    "requires_address": True
                }
    
    def handle_vehicle_sale(self, user_input, session):
        """Handle: بيع مركبة"""
        step = session.get("step", 0)
        
        if step == 0:
            # Parse vehicle info from input
            session["step"] = 1
            return {
                "response": "تمام، البيانات كلها موجوده. حاب ااكد عليها - سيتم رفع طلب بيع مركبه بالبيانات التالية، هل تقدر تاكد؟",
                "requires_confirmation": True
            }
        elif step == 1:
            if "ايه" in user_input.lower():
                request_id = self.generate_request_id()
                session["request_id"] = request_id
                return {
                    "response": f"✅ تم رفع طلب بيع مركبه برقم {request_id}",
                    "success": True,
                    "request_id": request_id
                }
    
    def handle_parking_report(self, user_input, session):
        """Handle: اشعار بوقوف خاطئ"""
        step = session.get("step", 0)
        
        if step == 0:
            session["step"] = 1
            return {
                "response": "ابشر، للتاكيد هذا رقم اللوحه من المرفقات - هل صحيح؟",
                "requires_confirmation": True
            }
        elif step == 1:
            if "ايه" in user_input.lower():
                request_id = self.generate_request_id()
                return {
                    "response": f"✅ تمام، بلغنا صاحب المركبه ورقم الطلب هو {request_id}",
                    "success": True,
                    "request_id": request_id
                }
    
    def get_service_info(self, service_name):
        """Get service information and expected workflow"""
        services_info = {
            "photo_change": {
                "name_ar": "تغيير صورة الاقامة",
                "steps": 2,
                "requires": ["image"],
                "time": "5-10 دقائق"
            },
            "name_change": {
                "name_ar": "تغيير الاسم الاول",
                "steps": 2,
                "requires": ["name"],
                "time": "3-5 دقائق"
            },
            "license_renewal": {
                "name_ar": "تجديد الرخصة",
                "steps": 5,
                "requires": ["duration", "address"],
                "time": "10-15 دقائق"
            },
            "vehicle_sale": {
                "name_ar": "بيع مركبة",
                "steps": 4,
                "requires": ["plate", "price", "buyer_id"],
                "time": "15-20 دقائق"
            }
        }
        
        return services_info.get(service_name, {})
    
    def reset_session(self, user_id):
        """Reset user session"""
        if user_id in self.sessions:
            del self.sessions[user_id]