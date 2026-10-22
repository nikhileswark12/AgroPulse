import pytest

from config import ProductionConfig


def test_production_config_rejects_default_or_short_secret(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "short-secret")
    monkeypatch.setattr(ProductionConfig, "MONGO_URI", "mongodb+srv://cluster.example.com/agropulse")

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        ProductionConfig.validate()


def test_production_config_rejects_local_mongodb(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "s" * 40)
    monkeypatch.setattr(ProductionConfig, "MONGO_URI", "mongodb://localhost:27017/agropulse")

    with pytest.raises(RuntimeError, match="localhost"):
        ProductionConfig.validate()


def test_production_config_accepts_valid_settings(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "s" * 40)
    monkeypatch.setattr(ProductionConfig, "MONGO_URI", "mongodb+srv://cluster.example.com/agropulse")

    ProductionConfig.validate()
