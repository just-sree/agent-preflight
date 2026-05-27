import json
import sqlite3

from agent_preflight.audit import AuditWriter, SQLiteAuditWriter
from agent_preflight.models import ActionPayload


def test_audit_writer_writes_jsonl_and_returns_audit_id(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    writer = AuditWriter(audit_path)
    payload = ActionPayload(
        action_name="lookup_user",
        metadata={"source": "test"},
    )

    audit_id = writer.write(payload, result_allowed=True, reason="Allowed by default")

    assert audit_id
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["audit_id"] == audit_id
    assert record["action_name"] == "lookup_user"
    assert record["allowed"] is True
    assert record["reason"] == "Allowed by default"
    assert record["metadata"] == {"source": "test"}


def test_audit_writer_sanitizes_non_serializable_metadata(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    writer = AuditWriter(audit_path)
    payload = ActionPayload(
        action_name="lookup_user",
        metadata={"source": {"not_serializable": object()}},
    )

    audit_id = writer.write(payload, result_allowed=True, reason="Allowed by default")

    record = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert record["audit_id"] == audit_id
    assert isinstance(record["metadata"]["source"], str)


def test_sqlite_audit_writer_creates_database(tmp_path):
    audit_path = tmp_path / "audit.db"
    writer = SQLiteAuditWriter(audit_path)
    payload = ActionPayload(action_name="lookup_user")

    writer.write(payload, result_allowed=True, reason="Allowed by default")

    assert audit_path.exists()


def test_sqlite_audit_writer_creates_table(tmp_path):
    audit_path = tmp_path / "audit.db"
    writer = SQLiteAuditWriter(audit_path)
    payload = ActionPayload(action_name="lookup_user")

    writer.write(payload, result_allowed=True, reason="Allowed by default")

    with sqlite3.connect(audit_path) as connection:
        table_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'audit_records'
            """
        ).fetchone()[0]

    assert table_count == 1


def test_sqlite_audit_writer_writes_one_record(tmp_path):
    audit_path = tmp_path / "audit.db"
    writer = SQLiteAuditWriter(audit_path)
    payload = ActionPayload(
        action_name="lookup_user",
        metadata={"source": "test"},
    )

    audit_id = writer.write(payload, result_allowed=True, reason="Allowed by default")

    with sqlite3.connect(audit_path) as connection:
        row = connection.execute(
            """
            SELECT audit_id, action_name, allowed, reason, metadata_json
            FROM audit_records
            """
        ).fetchone()

    assert row[0] == audit_id
    assert row[1] == "lookup_user"
    assert row[2] == 1
    assert row[3] == "Allowed by default"
    assert json.loads(row[4]) == {"source": "test"}


def test_sqlite_audit_writer_returns_audit_id(tmp_path):
    audit_path = tmp_path / "audit.db"
    writer = SQLiteAuditWriter(audit_path)
    payload = ActionPayload(action_name="lookup_user")

    audit_id = writer.write(payload, result_allowed=True, reason="Allowed by default")

    assert audit_id
