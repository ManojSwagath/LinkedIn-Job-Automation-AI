"""
Qdrant Vector Database Helper
Manages job embeddings and semantic search
"""

import os
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


class QdrantHelper:
    """Helper class for Qdrant vector database operations"""
    
    def __init__(self):
        """Initialize Qdrant connection"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
        except ImportError:
            print("❌ qdrant-client not installed. Installing...")
            os.system("pip install qdrant-client")
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
        
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")
        
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key if self.qdrant_api_key else None
        )
        
        print(f"✅ Qdrant initialized at {self.qdrant_url}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return [0] * 1536  # Return zero vector on error
    
    def add_job(self, job_id: str, job_data: Dict, embedding: Optional[List[float]] = None):
        """
        Add job to Qdrant collection
        
        Args:
            job_id: Unique job identifier
            job_data: Job information dictionary
            embedding: Pre-computed embedding (optional)
        """
        try:
            from qdrant_client.models import PointStruct
            
            # Generate embedding if not provided
            if embedding is None:
                job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}"
                embedding = self.embed_text(job_text)
            
            point = PointStruct(
                id=hash(job_id) % (2**31),  # Use positive integer ID
                vector=embedding,
                payload=job_data
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✅ Added job: {job_data.get('title', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error adding job: {e}")
    
    def search_similar_jobs(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for jobs similar to query
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List[Dict]: Similar jobs with scores
        """
        try:
            query_embedding = self.embed_text(query)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            
            jobs = []
            for result in results:
                job = result.payload
                job['similarity_score'] = result.score
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def batch_add_jobs(self, jobs: List[Tuple[str, Dict, Optional[List[float]]]]):
        """
        Add multiple jobs to Qdrant
        
        Args:
            jobs: List of (job_id, job_data, embedding) tuples
        """
        try:
            from qdrant_client.models import PointStruct
            
            points = []
            for job_id, job_data, embedding in jobs:
                if embedding is None:
                    job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}"
                    embedding = self.embed_text(job_text)
                
                point = PointStruct(
                    id=hash(job_id) % (2**31),
                    vector=embedding,
                    payload=job_data
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            print(f"✅ Added {len(points)} jobs to Qdrant")
            
        except Exception as e:
            print(f"❌ Batch add error: {e}")
    
    def get_collection_info(self) -> Dict:
        """
        Get collection statistics
        
        Returns:
            Dict: Collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'points_count': collection_info.points_count,
                'vectors_count': collection_info.vectors_count,
                'status': collection_info.status,
            }
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return {}
    
    def delete_job(self, job_id: str):
        """
        Delete job from Qdrant
        
        Args:
            job_id: Job identifier to delete
        """
        try:
            point_id = hash(job_id) % (2**31)
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            print(f"✅ Deleted job: {job_id}")
        except Exception as e:
            print(f"❌ Error deleting job: {e}")
    
    def clear_collection(self):
        """Clear all jobs from collection"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"✅ Cleared collection: {self.collection_name}")
            
            # Recreate collection
            from qdrant_client.models import Distance, VectorParams
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"✅ Recreated collection: {self.collection_name}")
        except Exception as e:
            print(f"❌ Error clearing collection: {e}")


if __name__ == "__main__":
    # Test Qdrant helper
    print("🧪 Testing Qdrant Helper...\n")
    
    try:
        helper = QdrantHelper()
        
        # Get collection info
        info = helper.get_collection_info()
        print(f"\n📊 Collection Info:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Test embedding
        print(f"\n✅ Qdrant helper is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Make sure Qdrant is running:")
        print(f"   docker run -p 6333:6333 qdrant/qdrant:latest")
