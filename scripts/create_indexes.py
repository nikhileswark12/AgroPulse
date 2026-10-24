import logging
import pymongo
from flask import current_app, has_app_context
from pymongo.errors import PyMongoError
from utils.db_connection import get_db
from config import BaseConfig

logger = logging.getLogger("agropulse.indexes")


def create_indexes():
    database = get_db()
    config = current_app.config if has_app_context() else vars(BaseConfig)
    failures = []
    users = database.users

    for user in users.find({}, {"_id": 1, "email": 1, "email_normalized": 1}):
        email = user.get("email")
        if isinstance(email, str) and email.strip():
            normalized = email.strip().casefold()
            if user.get("email_normalized") != normalized:
                users.update_one({"_id": user["_id"]}, {"$set": {"email_normalized": normalized}})

    index_tasks = [
        ("users", lambda: users.create_index([("email_normalized", pymongo.ASCENDING)], unique=True, partialFilterExpression={"email_normalized": {"$type": "string"}}, name="uq_users_email_normalized")),
        (config.get("PREDICTION_HISTORY_COLLECTION", "prediction_history"), lambda: _create_history_indexes(database[config.get("PREDICTION_HISTORY_COLLECTION", "prediction_history")])),
        (config.get("PRICES_COLLECTION", "prices"), lambda: _create_price_indexes(database[config.get("PRICES_COLLECTION", "prices")])),
        (config.get("MARKETS_COLLECTION", "markets"), lambda: _create_market_indexes(database[config.get("MARKETS_COLLECTION", "markets")])),
        (config.get("PREDICTIONS_COLLECTION", "predictions"), lambda: database[config.get("PREDICTIONS_COLLECTION", "predictions")].create_index([("crop", pymongo.ASCENDING), ("location", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)]))
    ]

    for collection_name, create in index_tasks:
        try:
            create()
        except PyMongoError:
            failures.append(collection_name)
            logger.exception("Failed to create indexes for %s", collection_name)

    if failures:
        raise RuntimeError("Database index initialization failed for: " + ", ".join(failures))
    logger.info("Database indexes verified")


def _create_history_indexes(collection):
    collection.create_index([("user_id", pymongo.ASCENDING)])
    collection.create_index([("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
    collection.create_index([("created_at", pymongo.DESCENDING)])


def _create_price_indexes(collection):
    collection.create_index([("crop", pymongo.ASCENDING), ("district", pymongo.ASCENDING), ("state", pymongo.ASCENDING)])
    collection.create_index([("date", pymongo.DESCENDING)])
    collection.create_index([("crop", pymongo.ASCENDING), ("date", pymongo.DESCENDING)])


def _create_market_indexes(collection):
    collection.create_index([("district", pymongo.ASCENDING)])
    collection.create_index([("state", pymongo.ASCENDING)])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from app import create_app
    app = create_app()
    with app.app_context():
        create_indexes()
