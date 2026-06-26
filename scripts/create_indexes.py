import logging
import pymongo
from utils.db_connection import get_db
from config import Config

logger = logging.getLogger('agropulse.indexes')

def create_indexes():
    db = get_db()
    
    # users collection
    try:
        db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
    except Exception as e:
        logger.warning(f"Failed to create index on users: {e}")

    # prediction_history collection
    try:
        col = db[getattr(Config, 'PREDICTION_HISTORY_COLLECTION', 'prediction_history')]
        col.create_index([("user_id", pymongo.ASCENDING)])
        col.create_index([("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
        col.create_index([("created_at", pymongo.DESCENDING)])
    except Exception as e:
        logger.warning(f"Failed to create index on prediction_history: {e}")

    # prices collection
    try:
        col = db[getattr(Config, 'PRICES_COLLECTION', 'prices')]
        col.create_index([("crop", pymongo.ASCENDING), ("district", pymongo.ASCENDING), ("state", pymongo.ASCENDING)])
        col.create_index([("date", pymongo.DESCENDING)])
        col.create_index([("crop", pymongo.ASCENDING), ("date", pymongo.DESCENDING)])
    except Exception as e:
        logger.warning(f"Failed to create index on prices: {e}")

    # markets collection
    try:
        col = db[getattr(Config, 'MARKETS_COLLECTION', 'markets')]
        col.create_index([("district", pymongo.ASCENDING)])
        col.create_index([("state", pymongo.ASCENDING)])
    except Exception as e:
        logger.warning(f"Failed to create index on markets: {e}")

    # predictions collection
    try:
        col = db[getattr(Config, 'PREDICTIONS_COLLECTION', 'predictions')]
        col.create_index([("crop", pymongo.ASCENDING), ("location", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
    except Exception as e:
        logger.warning(f"Failed to create index on predictions: {e}")

    logger.info("Database indexes verified")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from app import create_app
    app = create_app()
    with app.app_context():
        create_indexes()
