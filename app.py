
import os
import json
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import random

# Initialize Flask
app = Flask(__name__)
CORS(app)

# ============================================
# 14 SERVICES DEFINITIONS
# ============================================

SERVICES = {
    1: {
        "name_ar": "تغيير صورة المقيم",
        "name_en": "Change Residence Photo",
        "description": "تغيير صورة بطاقة الإقامة",
        "required_fields": ["صورة"],
        "steps": 2
    },
    2: {
        "name_ar": "تغيير الاسم الأول",
        "name_en": "Change First Name",
        "description": "تغيير الاسم الأول في الوثائق",
        "required_fields": ["الاسم الجديد"],
        "steps": 3
    },
    3: {
        "name_ar": "شراء لوحة",
        "name_en": "Buy License Plate",
        "description": "شراء لوحة ترخيص جديدة",
        "required_fields": ["رقم اللوحة", "صورة اللوحة"],
        "steps": 3
    },
    4: {
        "name_ar": "إشعار بوقوف خاطئ",
        "name_en": "Illegal Parking Report",
        "description": "الإبلاغ عن وقوف خاطئ",
        "required_fields": ["رقم اللوحة", "صورة اللوحة", "الموقع"],
        "steps": 3
    },
    5: {
        "name_ar": "إشعار حادث",
        "name_en": "Accident Report",
        "description": "الإبلاغ عن حادث مروري",
        "required_fields": ["رقم اللوحة", "وصف الحادث"],
        "steps": 3
    },
    6: {
        "name_ar": "شهادة خلو سوابق",
        "name_en": "Criminal Record Certificate",
        "description": "الحصول على شهادة خلو سوابق",
        "required_fields": [],
        "steps": 2
    },
    7: {
        "name_ar": "تصحيح الحالة الاجتماعية",
        "name_en": "Marital Status Update",
        "description": "تغيير أو تحديث الحالة الاجتماعية",
        "required_fields": ["الحالة الجديدة"],
        "steps": 3
    },
    8: {
        "name_ar": "تجديد الرخصة",
        "name_en": "License Renewal",
        "description": "تجديد رخصة السيارة",
        "required_fields": ["مدة التجديد", "العنوان"],
        "steps": 5
    },
    9: {
        "name_ar": "بيع مركبة",
        "name_en": "Sell Vehicle",
        "description": "بيع السيارة",
        "required_fields": ["رقم اللوحة", "بيانات المشتري", "السعر", "الممشى"],
        "steps": 4
    },
    10: {
        "name_ar": "شراء مركبة",
        "name_en": "Buy Vehicle",
        "description": "شراء مركبة جديدة",
        "required_fields": ["بيانات السيارة"],
        "steps": 3
    },
    11: {
        "name_ar": "تسليم مركبة",
        "name_en": "Vehicle Delivery",
        "description": "تسليم أو استلام مركبة",
        "required_fields": ["بيانات المركبة"],
        "steps": 2
    },
    12: {
        "name_ar": "إلغاء تفويض",
        "name_en": "Cancel Authorization",
        "description": "إلغاء تفويض محقق",
        "required_fields": ["بيانات السيارة"],
        "steps": 2
    },
    13: {
        "name_ar": "خدمة كفو",
        "name_en": "Kafo Service",
        "description": "خدمة توصيل الوثائق",
        "required_fields": ["نوع النشاط"],
        "steps": 2
    },
    14: {
        "name_ar": "نقل ملكية سلاح",
        "name_en": "Weapon Ownership Transfer",
        "description": "نقل ملكية السلاح",
        "required_fields": ["بيانات السلاح", "بيانات المالك الجديد"],
        "steps": 3
    }
}

# ============================================
# KEYWORDS MAP (GLOBAL - FIXED)
# ============================================

KEYWORDS_MAP = {
    1: ["صورة", "اقامة", "photo", "residence"],
    2: ["اسم", "اسمي", "name"],
    3: ["لوحة", "plate", "رقم"],
    4: ["وقوف", "parking", "خاطئ"],
    5: ["حادث", "accident", "خدش"],
    6: ["شهادة", "سوابق", "certificate"],
    7: ["حالة", "اجتماعية", "marital"],
    8: ["رخصة", "تجديد", "license"],
    9: ["بيع", "مركبة", "sell"],
    10: ["شراء", "مركبة", "buy"],
    11: ["تسليم", "مركبة", "delivery"],
    12: ["الغاء", "تفويض", "cancel"],
    13: ["كفو", "توصيل"],
    14: ["سلاح", "نقل", "weapon"],
}

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_user_by_id(user_id):
    """Get user from database"""
    conn = sqlite3.connect('wafi_users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def save_conversation(user_id, service_type, messages):
    """Save conversation to database"""
    conn = sqlite3.connect('wafi_users.db')
    cursor = conn.cursor()
    conversation_id = f"CONV_{user_id}_{int(datetime.now().timestamp())}"
    cursor.execute('''
    INSERT INTO conversations (conversation_id, user_id, service_type, messages, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (conversation_id, user_id, service_type, json.dumps(messages, ensure_ascii=False), 
          'pending', datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return conversation_id

# ============================================
# ROUTES
# ============================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🇸🇦 وافي أبشر - مساعدك الذكي للخدمات الحكومية",
        "version": "1.0",
        "services": len(SERVICES),
        "status": "running"
    })

@app.route("/api/services", methods=["GET"])
def get_services():
    """Get all 14 services"""
    return jsonify(list(SERVICES.values()))

@app.route("/api/hints", methods=["POST"])
def get_hints():
    """Get smart hints based on user input"""
    data = request.json
    user_input = data.get("input", "").lower()
    
    hints = []
    
    # Match user input to services
    for service_id, keywords in KEYWORDS_MAP.items():
        if any(kw in user_input for kw in keywords):
            service = SERVICES[service_id]
            hints.append({
                "service_id": service_id,
                "service_name": service["name_ar"],
                "required_fields": service["required_fields"],
                "steps": service["steps"]
            })
    
    return jsonify({"hints": hints[:5]})  # Return top 5 hints

@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    data = request.json
    user_id = data.get("user_id", "guest")
    message = data.get("message", "").strip()
    service_type = data.get("service_type", None)
    
    if not message:
        return jsonify({"error": "Empty message"}), 400
    
    # Get user info (optional)
    user = get_user_by_id(user_id) if user_id != "guest" else None
    
    # Generate response (simplified version)
    responses = {
        1: "تمام، بتشيك الصورة الآن. صورتك مطابقة للشروط والأحكام. هل تريد المتابعة؟",
        2: "ابشر، الاسم الجديد مطابق. هل تأكد تغيير الاسم؟",
        3: "معاينة صورة اللوحة تمت بنجاح. تم التأكيد برقم اللوحة. هل تريد المتابعة؟",
        4: "تم الإبلاغ عن الوقوف الخاطئ برقم الطلب XXXX",
        5: "تم استقبال إشعار الحادث. رقم الطلب XXXX",
        6: "تم إصدار شهادة خلو السوابق. يمكنك تحميلها من هنا.",
        7: "الف مبروك الزواج! هل تريد تأكيد التغيير؟",
        8: "كم سنة تريد تجديد الرخصة؟ (سنتين، 5، أم 10 سنوات؟)",
        9: "تمام، تم استقبال طلب البيع برقم XXXX",
        10: "هناك طلب شراء معلق. هل تريد الموافقة؟",
        11: "تم تسليم المركبة برقم XXXX",
        12: "تم إلغاء التفويض برقم XXXX",
        13: "تمام، تم التسجيل في خدمة كفو",
        14: "تمام، تم نقل ملكية السلاح برقم XXXX"
    }
    
    # Detect service (simple keyword matching) - FIXED TO USE KEYWORDS_MAP
    detected_service = None
    if service_type:
        detected_service = service_type
    else:
        for service_id, keywords in KEYWORDS_MAP.items():
            if any(kw in message.lower() for kw in keywords):
                detected_service = service_id
                break
    
    response_text = responses.get(detected_service, "كيف يمكنني مساعدتك؟")
    
    return jsonify({
        "response": response_text,
        "service_detected": detected_service,
        "user": user,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
