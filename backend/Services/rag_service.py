# backend/services/rag_service.py
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
import json

class RAGService:
    def __init__(self, config):
        self.config = config
        self.embeddings = None
        self.vectorstore = None
        self.initialize_rag()
    
    def initialize_rag(self):
        """Initialize RAG system with vector database"""
        try:
            print("🔄 Initializing RAG system...")
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config.HF_EMBEDDING_MODEL,
                model_kwargs={'device': self.config.LLM_DEVICE}
            )
            
            # Initialize vector store
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./chroma_data"
            )
            
            print("✅ RAG system initialized")
            
        except Exception as e:
            print(f"❌ Error initializing RAG: {e}")
            raise
    
    def load_service_documents(self, workflows_json_path="backend/data/service_workflows.json"):
        """Load workflow documents into vector store"""
        try:
            with open(workflows_json_path, 'r', encoding='utf-8') as f:
                workflows = json.load(f)
            
            documents = []
            for workflow in workflows:
                doc_text = f"""
                Service: {workflow['service']}
                Title: {workflow['workflow_title']}
                Description: {workflow['description']}
                Steps: {json.dumps(workflow['steps'], ensure_ascii=False)}
                """
                
                documents.append(Document(
                    page_content=doc_text,
                    metadata={
                        "service": workflow['service'],
                        "title": workflow['workflow_title'],
                        "video_id": workflow.get('video_id', 'N/A')
                    }
                ))
            
            # Add documents to vector store
            if documents:
                self.vectorstore.add_documents(documents)
                print(f"✅ Loaded {len(documents)} workflow documents")
        
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
    
    def retrieve_context(self, query, k=3):
        """Retrieve relevant context for a query"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            context = "\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
    
    def update_workflow(self, service_name, workflow_data):
        """Update workflow in vector store"""
        doc_text = f"""
        Service: {service_name}
        Data: {json.dumps(workflow_data, ensure_ascii=False)}
        """
        
        self.vectorstore.add_documents([Document(
            page_content=doc_text,
            metadata={"service": service_name, "updated": True}
        )])