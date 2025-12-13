# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('ENVIRONMENT', 'development')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wafi_absher.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # HuggingFace
    HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    HF_MODEL = 'humain-ai/ALLaM-7B-Instruct-preview'
    HF_EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    
    # LLM Settings
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 512
    LLM_DEVICE = os.getenv('DEVICE', 'cpu')  # cpu, cuda
    
    # RAG Settings
    RAG_CHUNK_SIZE = 512
    RAG_OVERLAP = 50
    RAG_TOP_K = 3
    
    # Session
    SESSION_TIMEOUT = 30  # minutes
    MAX_HISTORY = 50  # messages
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000')

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    LLM_DEVICE = 'cuda'

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}