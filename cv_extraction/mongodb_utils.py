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


def normalize_mongodb_uri(uri: str) -> str:
    """
    Normalize MongoDB URI to ensure proper format.
    
    For mongodb+srv:// connections, TLS is automatically enabled by PyMongo.
    This function ensures the URI has:
    1. Database name (if missing, uses MONGODB_DB_NAME from settings)
    2. Connection options (retryWrites=true&w=majority)
    
    Examples:
    - mongodb+srv://user:pass@host.net/ -> mongodb+srv://user:pass@host.net/cv_platform?retryWrites=true&w=majority
    - mongodb+srv://user:pass@host.net -> mongodb+srv://user:pass@host.net/cv_platform?retryWrites=true&w=majority
    - mongodb+srv://user:pass@host.net/cv_platform -> mongodb+srv://user:pass@host.net/cv_platform?retryWrites=true&w=majority
    """
    if not uri:
        return uri
    
    # Strip whitespace and remove quotes if present
    uri = uri.strip().strip('"').strip("'")
    
    # Validate URI starts with correct scheme
    if not (uri.startswith('mongodb://') or uri.startswith('mongodb+srv://')):
        logger.error(f'Invalid MongoDB URI scheme: {uri[:50]}... (must start with mongodb:// or mongodb+srv://)')
        raise ValueError(f"Invalid URI scheme: URI must begin with 'mongodb://' or 'mongodb+srv://'. Got: {uri[:50]}...")
    
    # For mongodb+srv://, ensure it has database name and query parameters
    if uri.startswith('mongodb+srv://'):
        # Check if URI ends with just / (no database name)
        if uri.endswith('/'):
            # Remove trailing / and add database name
            db_name = settings.MONGODB_DB_NAME
            uri = uri.rstrip('/') + f'/{db_name}'
        # Check if URI has @ but no / after it (no database name)
        elif '@' in uri and '/' not in uri.split('@')[1].split('?')[0]:
            # No database name, add it
            db_name = settings.MONGODB_DB_NAME
            # Insert database name before ? if present, or at the end
            if '?' in uri:
                uri = uri.split('?')[0] + f'/{db_name}?' + uri.split('?')[1]
            else:
                uri = uri + f'/{db_name}'
        
        # Ensure query parameters are present
        if '?' not in uri:
            # Add standard Atlas connection parameters
            uri = uri + '?retryWrites=true&w=majority'
        else:
            # Has query params, check if retryWrites is missing
            query_part = uri.split('?')[1]
            if 'retryWrites' not in query_part.lower():
                uri = uri + '&retryWrites=true&w=majority'
    
    return uri


class MongoDBManager:
    """Singleton MongoDB connection manager."""
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client instance with timeout settings."""
        if cls._client is None:
            # Get MongoDB URI and ensure it has proper format
            raw_uri = settings.MONGODB_URI
            logger.debug(f'Raw MongoDB URI from settings: {raw_uri[:50]}... (length: {len(raw_uri)})')
            
            # Validate and normalize the URI
            try:
                mongodb_uri = normalize_mongodb_uri(raw_uri)
                logger.debug(f'Normalized MongoDB URI: {mongodb_uri[:50]}...')
            except ValueError as e:
                logger.error(f'Failed to normalize MongoDB URI: {str(e)}')
                logger.error(f'Raw URI value: {repr(raw_uri)}')
                raise
            
            # Ensure connection string has proper SSL/TLS parameters for Atlas
            # For mongodb+srv://, SSL is required by default
            connection_params = {
                'serverSelectionTimeoutMS': 15000,  # 15 seconds - increased for SSL handshake
                'connectTimeoutMS': 15000,  # 15 seconds connection timeout
                'socketTimeoutMS': 15000,  # 15 seconds socket timeout
                'maxPoolSize': 10,
                'retryWrites': True,
                'retryReads': True,
                'connect': False,  # Don't wait for connection on init - connect lazily
            }
            
            # For mongodb+srv:// (Atlas), ensure TLS is properly configured
            # PyMongo automatically enables TLS for +srv connections, but we can be explicit
            if mongodb_uri.startswith('mongodb+srv://'):
                # Ensure TLS is enabled (default for +srv, but explicit is better)
                connection_params['tls'] = True
                connection_params['tlsAllowInvalidCertificates'] = False
                # Use system default CA certificates
                connection_params['tlsCAFile'] = None
            
            try:
                cls._client = MongoClient(mongodb_uri, **connection_params)
                logger.info(f'MongoDB client created successfully (URI: {mongodb_uri[:20]}...)')
            except Exception as e:
                logger.error(f'Failed to create MongoDB client: {str(e)}')
                logger.error(f'MongoDB URI format: {mongodb_uri[:50]}... (truncated for security)')
                # Reset connection on failure
                cls._client = None
                raise
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
        error_msg = str(e)
        logger.error(f'MongoDB error in save_cv_profile: {error_msg}')
        # Reset connection on any MongoDB error
        MongoDBManager.reset_connection()
        # If it's an SSL error, provide more helpful message
        if 'SSL' in error_msg or 'TLS' in error_msg or 'handshake' in error_msg.lower():
            logger.error('SSL/TLS handshake failed. This may be due to:')
            logger.error('1. Python 3.13 SSL compatibility issues')
            logger.error('2. Network/firewall blocking SSL connections')
            logger.error('3. MongoDB Atlas SSL configuration')
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

