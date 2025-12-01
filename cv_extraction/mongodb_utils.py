"""
MongoDB connection and utility functions.
"""
import pymongo
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, PyMongoError
from django.conf import settings
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Singleton MongoDB connection manager."""
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client instance with timeout settings."""
        if cls._client is None:
            # Get MongoDB URI and ensure it has proper format
            mongodb_uri = settings.MONGODB_URI
            
            # Add timeout settings to prevent hanging
            # Use shorter timeouts to fail fast rather than hang
            # Don't test connection on init - let first query handle it with timeout
            cls._client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 seconds - fail fast
                connectTimeoutMS=5000,  # 5 seconds connection timeout
                socketTimeoutMS=5000,  # 5 seconds socket timeout
                maxPoolSize=10,
                retryWrites=True,
                retryReads=True,
                # Don't wait for connection on init - connect lazily
                connect=False
            )
        return cls._client
    
    @classmethod
    def get_database(cls):
        """Get MongoDB database instance."""
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGODB_DB_NAME]
        return cls._db
    
    @classmethod
    def get_cv_collection(cls):
        """Get CV collection."""
        try:
            db = cls.get_database()
            return db['cv_profiles']
        except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
            logger.error(f'MongoDB collection access failed: {str(e)}')
            # Reset connection on failure
            cls._client = None
            cls._db = None
            raise
    
    @classmethod
    def close_connection(cls):
        """Close MongoDB connection."""
        if cls._client:
            try:
                cls._client.close()
            except:
                pass
            cls._client = None
            cls._db = None
    
    @classmethod
    def reset_connection(cls):
        """Reset MongoDB connection (useful after errors)."""
        cls.close_connection()


def save_cv_profile(user_id: int, cv_data: Dict) -> str:
    """
    Save CV profile to MongoDB.
    
    Args:
        user_id: Django User ID
        cv_data: Dictionary containing CV data matching CVExtract schema
    
    Returns:
        MongoDB document ID as string
    """
    try:
        collection = MongoDBManager.get_cv_collection()
        
        document = {
            'user_id': user_id,
            'full_name': cv_data.get('full_name', ''),
            'email': cv_data.get('email', ''),
            'phone': cv_data.get('phone', ''),
            'summary': cv_data.get('summary', ''),
            'skills': cv_data.get('skills', []),
            'education': cv_data.get('education', []),
            'experience': cv_data.get('experience', []),
            'certifications': cv_data.get('certifications', []),
            'languages': cv_data.get('languages', []),
            'gpa': cv_data.get('gpa'),
            'major': cv_data.get('major', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        # Check if profile already exists for this user
        existing = collection.find_one({'user_id': user_id}, max_time_ms=3000)
        if existing:
            document['updated_at'] = datetime.utcnow()
            collection.update_one(
                {'user_id': user_id},
                {'$set': document},
                max_time_ms=3000
            )
            return str(existing['_id'])
        else:
            result = collection.insert_one(document)
            return str(result.inserted_id)
    except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
        logger.error(f'MongoDB error in save_cv_profile: {str(e)}')
        MongoDBManager.reset_connection()
        raise
    except Exception as e:
        logger.error(f'Unexpected error in save_cv_profile: {str(e)}')
        raise


def get_cv_profile(user_id: int) -> Optional[Dict]:
    """Get CV profile for a user."""
    try:
        collection = MongoDBManager.get_cv_collection()
        # Use shorter timeout to prevent worker timeout
        profile = collection.find_one({'user_id': user_id}, max_time_ms=3000)  # 3 second timeout
        if profile:
            profile['_id'] = str(profile['_id'])
        return profile
    except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
        # Log error but don't crash - return None if MongoDB is unavailable
        logger.warning(f'MongoDB connection error in get_cv_profile: {str(e)}')
        MongoDBManager.reset_connection()
        return None
    except Exception as e:
        logger.error(f'Unexpected error in get_cv_profile: {str(e)}')
        return None


def get_all_cv_profiles() -> List[Dict]:
    """Get all CV profiles."""
    try:
        collection = MongoDBManager.get_cv_collection()
        profiles = list(collection.find(max_time_ms=3000))
        for profile in profiles:
            profile['_id'] = str(profile['_id'])
        return profiles
    except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
        logger.warning(f'MongoDB connection error in get_all_cv_profiles: {str(e)}')
        MongoDBManager.reset_connection()
        return []
    except Exception as e:
        logger.error(f'Unexpected error in get_all_cv_profiles: {str(e)}')
        return []


def search_cv_profiles(query: Dict) -> List[Dict]:
    """
    Search CV profiles with filters.
    
    Args:
        query: MongoDB query dictionary
    
    Returns:
        List of matching profiles
    """
    try:
        collection = MongoDBManager.get_cv_collection()
        profiles = list(collection.find(query, max_time_ms=3000))
        for profile in profiles:
            profile['_id'] = str(profile['_id'])
        return profiles
    except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
        logger.warning(f'MongoDB connection error in search_cv_profiles: {str(e)}')
        MongoDBManager.reset_connection()
        return []
    except Exception as e:
        logger.error(f'Unexpected error in search_cv_profiles: {str(e)}')
        return []


def delete_cv_profile(user_id: int) -> bool:
    """Delete CV profile for a user."""
    try:
        collection = MongoDBManager.get_cv_collection()
        result = collection.delete_one({'user_id': user_id})
        return result.deleted_count > 0
    except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
        logger.warning(f'MongoDB connection error in delete_cv_profile: {str(e)}')
        MongoDBManager.reset_connection()
        return False
    except Exception as e:
        logger.error(f'Unexpected error in delete_cv_profile: {str(e)}')
        return False


def delete_cv_profile_by_id(profile_id: str) -> bool:
    """Delete CV profile by MongoDB ID."""
    from bson import ObjectId
    try:
        collection = MongoDBManager.get_cv_collection()
        result = collection.delete_one({'_id': ObjectId(profile_id)})
        return result.deleted_count > 0
    except (ServerSelectionTimeoutError, ConnectionFailure, PyMongoError) as e:
        logger.warning(f'MongoDB connection error in delete_cv_profile_by_id: {str(e)}')
        MongoDBManager.reset_connection()
        return False
    except Exception:
        return False

