# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from services.llm_service import LLMService, ServiceDetector
from services.rag_service import RAGService
from services.workflow_handler import WorkflowHandler

# Initialize Flask app
app = Flask(__name__)
env = os.getenv('ENVIRONMENT', 'development')
app.config.from_object(config[env])
CORS(app)

# Initialize services
try:
    llm_service = LLMService(app.config)
    rag_service = RAGService(app.config)
    workflow_handler = WorkflowHandler()
    print("✅ All services initialized successfully")
except Exception as e:
    print(f"❌ Error initializing services: {e}")
    llm_service = None

# Store conversation context
conversation_context = {}

@app.route('/', methods=['GET'])
def index():
    """Serve frontend"""
    return send_from_directory('..', 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": "initialized" if llm_service else "error",
            "rag": "initialized",
            "workflow": "initialized"
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        user_id = data.get('user_id', 'guest')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Empty message"}), 400
        
        # Get user session
        session = workflow_handler.get_session(user_id)
        
        # Detect service from user input
        detected_service = ServiceDetector.detect_service(message)
        
        if not session.get("service"):
            session["service"] = detected_service
        
        # Add to history
        session["history"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build context
        context_history = "\n".join([
            f"{h['role']}: {h['content']}"
            for h in session["history"][-5:]  # Last 5 messages
        ])
        
        # Get RAG context
        rag_context = rag_service.retrieve_context(message)
        
        # Generate response
        if llm_service:
            response = llm_service.generate_response(
                user_input=message,
                context=context_history,
                service_type=session["service"]
            )
        else:
            response = "معذرة، خدمة اللغة الطبيعية غير متاحة حالياً"
        
        # Handle workflow-specific responses
        workflow_response = handle_workflow(detected_service, message, session)
        if workflow_response:
            response = workflow_response.get("response", response)
        
        # Add to history
        session["history"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "message": response,
            "service": session["service"],
            "session_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "detected_service": detected_service,
                "service_info": workflow_handler.get_service_info(detected_service),
                "workflow_response": workflow_response
            }
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get list of available services"""
    services = [
        {
            "id": 1,
            "name_ar": "تغيير صورة الاقامة",
            "name_en": "Change Residence Photo",
            "icon": "📷"
        },
        {
            "id": 2,
            "name_ar": "تغيير الاسم الاول",
            "name_en": "Change First Name",
            "icon": "📝"
        },
        {
            "id": 3,
            "name_ar": "شراء لوحة",
            "name_en": "Buy License Plate",
            "icon": "🔢"
        },
        {
            "id": 4,
            "name_ar": "اشعار بوقوف خاطئ",
            "name_en": "Report Wrong Parking",
            "icon": "🚗"
        },
        {
            "id": 5,
            "name_ar": "اشعار حادث/خدش",
            "name_en": "Report Accident",
            "icon": "⚠️"
        },
        {
            "id": 6,
            "name_ar": "اصدار شهادة خلو سوابق",
            "name_en": "Issue Clean Record",
            "icon": "📜"
        },
        {
            "id": 7,
            "name_ar": "تصحيح الحالة الاجتماعية",
            "name_en": "Update Marital Status",
            "icon": "💍"
        },
        {
            "id": 8,
            "name_ar": "تجديد الرخصة",
            "name_en": "Renew License",
            "icon": "🔄"
        },
        {
            "id": 9,
            "name_ar": "بيع مركبة",
            "name_en": "Sell Vehicle",
            "icon": "🚙"
        },
        {
            "id": 10,
            "name_ar": "شراء مركبة",
            "name_en": "Buy Vehicle",
            "icon": "🛒"
        },
        {
            "id": 11,
            "name_ar": "تسليم مركبة",
            "name_en": "Deliver Vehicle",
            "icon": "✋"
        },
        {
            "id": 12,
            "name_ar": "الغاء تفويض مركبة",
            "name_en": "Cancel Authorization",
            "icon": "🚫"
        },
        {
            "id": 13,
            "name_ar": "خدمة كفو",
            "name_en": "Kafo Service",
            "icon": "🚚"
        },
        {
            "id": 14,
            "name_ar": "نقل ملكية سلاح",
            "name_en": "Transfer Weapon",
            "icon": "🔫"
        }
    ]
    return jsonify(services)

@app.route('/api/session/<user_id>', methods=['GET', 'DELETE'])
def manage_session(user_id):
    """Manage user sessions"""
    if request.method == 'DELETE':
        workflow_handler.reset_session(user_id)
        return jsonify({"status": "session reset"})
    
    session = workflow_handler.get_session(user_id)
    return jsonify({
        "user_id": user_id,
        "service": session.get("service"),
        "step": session.get("step"),
        "history_length": len(session.get("history", []))
    })

def handle_workflow(service_type, user_input, session):
    """Handle service-specific workflows"""
    handlers = {
        "photo_change": workflow_handler.handle_photo_change,
        "name_change": workflow_handler.handle_name_change,
        "license_renewal": workflow_handler.handle_license_renewal,
        "vehicle_sale": workflow_handler.handle_vehicle_sale,
        "parking_report": workflow_handler.handle_parking_report,
    }
    
    handler = handlers.get(service_type)
    if handler:
        return handler(user_input, session)
    return None

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = app.config['FLASK_ENV'] == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)