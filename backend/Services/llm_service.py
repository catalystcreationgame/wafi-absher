# backend/services/llm_service.py
import os
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

class LLMService:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.llm = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the ALLaM model with HuggingFace"""
        try:
            print("🔄 Loading ALLaM-7B model...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.HF_MODEL,
                trust_remote_code=True,
                use_auth_token=self.config.HF_API_KEY
            )
            
            # Load model with quantization for efficiency
            device = 0 if torch.cuda.is_available() and self.config.LLM_DEVICE == 'cuda' else -1
            
            text_gen_pipeline = pipeline(
                "text-generation",
                model=self.config.HF_MODEL,
                tokenizer=self.tokenizer,
                device=device,
                max_new_tokens=self.config.LLM_MAX_TOKENS,
                temperature=self.config.LLM_TEMPERATURE,
                top_p=0.9,
                do_sample=True,
                trust_remote_code=True,
                model_kwargs={
                    "load_in_8bit": True,
                    "device_map": "auto"
                }
            )
            
            self.llm = HuggingFacePipeline(model_pipeline=text_gen_pipeline)
            print("✅ Model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def generate_response(self, user_input, context="", service_type=None):
        """Generate response using the LLM"""
        
        system_prompt = self._get_system_prompt(service_type)
        
        prompt_template = PromptTemplate(
            input_variables=["context", "input"],
            template="""أنت وافي أبشر، مساعد ذكي للخدمات الحكومية السعودية.
            
السياق: {context}

طلب المستخدم: {input}

الرد (باللغة العربية الفصحة والعامية السعودية):"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        try:
            response = chain.run(context=context, input=user_input)
            return response.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "معذرة، حدث خطأ. حاول مرة أخرى."
    
    def _get_system_prompt(self, service_type):
        """Get service-specific system prompt"""
        
        service_prompts = {
            "photo_change": """أنت مساعد للخدمة: تغيير صورة الإقامة.
- اطلب من المستخدم تأكيد الصورة
- تحقق من شروط الصورة (ملونة، خلفية بيضاء، واضحة)
- اطلب تأكيداً نهائياً""",
            
            "name_change": """أنت مساعد للخدمة: تغيير الاسم الأول.
- اطلب الاسم الجديد
- أعد تأكيد التغيير
- اطلب التأكيد النهائي""",
            
            "license_renewal": """أنت مساعد للخدمة: تجديد رخصة القيادة.
- اطلب عدد سنوات التجديد (2، 5، أو 10)
- أعد التأكيد
- اطلب بيانات التوصيل
- وافق على الدفع""",
            
            "vehicle_sale": """أنت مساعد للخدمة: بيع مركبة.
- اطلب بيانات المركبة (اللوحة، النوع، السعر)
- اطلب بيانات المشتري
- أعد التأكيد على كل المعلومات
- اطلب التأكيد النهائي""",
            
            "default": """أنت وافي أبشر، مساعد ذكي سعودي متخصص في الخدمات الحكومية.
- تحدث بالعربية الفصحة والعامية السعودية
- كن ودياً وسريع الاستجابة
- اطلب البيانات بوضوح
- أعد التأكيد على المعلومات المهمة
- استخدم رموز الحالة والأرقام المرجعية"""
        }
        
        return service_prompts.get(service_type, service_prompts["default"])

class ServiceDetector:
    """Detect which service the user is requesting"""
    
    KEYWORDS = {
        "photo_change": ["صورة", "الاقامة", "تصوير", "photo"],
        "name_change": ["اسم", "تغيير", "name", "اول"],
        "plate_purchase": ["لوحة", "رقم اللوحة", "plate", "شراء"],
        "parking_report": ["وقوف", "خاطئ", "parking", "مقفل"],
        "accident_report": ["حادث", "خدش", "accident", "اصطدام"],
        "certificate": ["شهادة", "سوابق", "certificate", "خلو"],
        "marital_status": ["حالة", "اجتماعية", "متزوج", "marital"],
        "license_renewal": ["رخصة", "تجديد", "license", "سواقة"],
        "vehicle_sale": ["بيع", "مركبة", "سيارة", "sell"],
        "vehicle_purchase": ["شراء", "مركبة", "buy"],
        "vehicle_delivery": ["تسليم", "مركبة", "delivery"],
        "vehicle_auth_cancel": ["الغاء", "تفويض", "cancel"],
        "kafo_service": ["كفو", "توصيل", "delivery", "apps"],
        "weapon_transfer": ["سلاح", "نقل", "transfer", "weapon"]
    }
    
    @classmethod
    def detect_service(cls, user_input):
        """Detect service type from user input"""
        input_lower = user_input.lower()
        
        for service, keywords in cls.KEYWORDS.items():
            if any(keyword in input_lower for keyword in keywords):
                return service
        
        return "general"