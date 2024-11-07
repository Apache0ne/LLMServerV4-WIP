# storage/tinydb_storage.py

from tinydb import TinyDB, Query
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class TinyDBStorage:
    def __init__(self, db_path: str = 'all_contexts.json'):
        self.db = TinyDB(db_path)
        self.Context = Query()
        logger.info(f"TinyDB storage initialized with database: {db_path}")

    def save(self, name: str, data: Dict[str, Any]) -> None:
        try:
            self.db.upsert(data, self.Context.name == name)
            logger.debug(f"Saved context: {name}")
        except Exception as e:
            logger.error(f"Error saving context {name}: {str(e)}")
            raise

    def load(self, name: str) -> Dict[str, Any]:
        try:
            result = self.db.search(self.Context.name == name)
            if result:
                logger.debug(f"Loaded context: {name}")
                return result[0]
            else:
                logger.warning(f"Context not found: {name}")
                return None
        except Exception as e:
            logger.error(f"Error loading context {name}: {str(e)}")
            raise

    def delete(self, name: str) -> None:
        try:
            self.db.remove(self.Context.name == name)
            logger.debug(f"Deleted context: {name}")
        except Exception as e:
            logger.error(f"Error deleting context {name}: {str(e)}")
            raise

    def load_all(self) -> List[Dict[str, Any]]:
        try:
            all_contexts = self.db.all()
            logger.debug(f"Loaded {len(all_contexts)} contexts")
            return all_contexts
        except Exception as e:
            logger.error(f"Error loading all contexts: {str(e)}")
            raise

    def clear_all(self) -> None:
        try:
            self.db.truncate()
            logger.warning("Cleared all contexts from the database")
        except Exception as e:
            logger.error(f"Error clearing all contexts: {str(e)}")
            raise