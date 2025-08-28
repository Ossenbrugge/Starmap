"""
User repository for managing user data access
"""

import logging
from typing import Optional, Dict, Any
from auth import User

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for user data operations"""

    def __init__(self):
        # In a real application, this would connect to a database
        # For now, we'll use a simple in-memory store with the existing auth system
        self._users = {}
        self._load_default_users()

    def _load_default_users(self):
        """Load default users (in production, this would come from database)"""
        from auth import AuthManager

        try:
            # Get users from existing AuthManager
            # Use a simple default secret key for now to avoid circular imports
            auth_manager = AuthManager('felgenland-union-secure-key-2025-change-in-production')
            self._users = auth_manager.users.copy()
            logger.info(f"Loaded {len(self._users)} users into repository")
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            self._users = {}

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            for user in self._users.values():
                if user.id == user_id:
                    return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return self._users.get(username)
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None

    def create_user(self, username: str, password_hash: str, role: str = 'user') -> Optional[User]:
        """Create a new user"""
        try:
            if username in self._users:
                logger.warning(f"User {username} already exists")
                return None

            # Generate next available ID
            user_id = max([user.id for user in self._users.values()] + [0]) + 1

            user = User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                role=role
            )

            self._users[username] = user
            logger.info(f"Created user {username} with ID {user_id}")
            return user

        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None

    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            user = self._users.get(username)
            if not user:
                return False

            # Update allowed fields
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            logger.info(f"Updated user {username}")
            return True

        except Exception as e:
            logger.error(f"Error updating user {username}: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        """Delete user"""
        try:
            if username in self._users:
                del self._users[username]
                logger.info(f"Deleted user {username}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            return False

    def list_users(self) -> list:
        """List all users (for admin purposes)"""
        try:
            return list(self._users.keys())
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        try:
            user = self._users.get(username)
            if user and user.check_password(password):
                return user
            return None

        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None

# Global user repository instance
user_repository = UserRepository()
