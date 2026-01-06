"""
AutoAgentHire Database Module
Complete database architecture for the job automation platform
"""

# Connection and Session Management
from backend.database.connection import (
    engine,
    SessionLocal,
    get_db,
    get_db_session,
    init_db,
    drop_db,
    db_manager,
    DatabaseManager
)

# Complete Models
from backend.database.models_complete import (
    Base,
    User,
    Resume,
    AgentRun,
    Application,
    AgentLog,
    JobCache,
    FileStorage,
    AnalyticsEvent
)

# CRUD Repositories
from backend.database.crud import (
    UserRepository,
    ResumeRepository,
    AgentRunRepository,
    ApplicationRepository,
    AgentLogRepository,
    JobCacheRepository,
    FileStorageRepository,
    AnalyticsRepository
)

# Vector Store
from backend.database.vector_store import (
    VectorStoreManager,
    vector_store,
    get_embedding,
    calculate_job_match_score,
    find_matching_jobs
)

# File Storage
from backend.database.file_storage import (
    FileStorageManager,
    file_storage,
    save_resume,
    save_screenshot,
    get_file
)

__all__ = [
    # Connection
    'engine',
    'SessionLocal', 
    'get_db',
    'get_db_session',
    'init_db',
    'drop_db',
    'db_manager',
    'DatabaseManager',
    
    # Models
    'Base',
    'User',
    'Resume',
    'AgentRun',
    'Application',
    'AgentLog',
    'JobCache',
    'FileStorage',
    'AnalyticsEvent',
    
    # Repositories
    'UserRepository',
    'ResumeRepository',
    'AgentRunRepository',
    'ApplicationRepository',
    'AgentLogRepository',
    'JobCacheRepository',
    'FileStorageRepository',
    'AnalyticsRepository',
    
    # Vector Store
    'VectorStoreManager',
    'vector_store',
    'get_embedding',
    'calculate_job_match_score',
    'find_matching_jobs',
    
    # File Storage
    'FileStorageManager',
    'file_storage',
    'save_resume',
    'save_screenshot',
    'get_file',
]
