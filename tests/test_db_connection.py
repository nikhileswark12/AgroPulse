from types import SimpleNamespace

from flask import Flask

import utils.db_connection as db_connection


class FakeDatabase:
    def __init__(self, name):
        self.name = name


class FakeClient:
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.closed = False
        self.commands = []
        self.admin = SimpleNamespace(command=self._command)

    def _command(self, name):
        self.commands.append(name)
        return {"ok": 1}

    def __getitem__(self, name):
        return FakeDatabase(name)

    def close(self):
        self.closed = True


def test_database_uses_active_flask_config_and_reconnects_on_change(monkeypatch):
    clients = []

    def fake_client(uri, **kwargs):
        client = FakeClient(uri, **kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(db_connection, "MongoClient", fake_client)
    database = db_connection.Database()
    database.close()
    app = Flask(__name__)
    app.config.update(MONGO_URI="mongodb://first/", DATABASE_NAME="agropulse_test")

    try:
        with app.app_context():
            first_db = database.get_db()
            assert first_db.name == "agropulse_test"
            app.config["DATABASE_NAME"] = "agropulse_isolated_test"
            second_db = database.get_db()
            assert second_db.name == "agropulse_isolated_test"

        assert len(clients) == 2
        assert clients[0].closed is True
        assert clients[1].closed is False
    finally:
        database.close()
