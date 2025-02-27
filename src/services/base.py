import logging

from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BaseService")


class BaseService:
    def __init__(self, db_session):
        self.db = db_session

    def commit_changes(self):
        try:
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            return False
