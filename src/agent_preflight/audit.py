from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid

from agent_preflight.models import ActionPayload, AuditRecord


class AuditWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def write(self, payload: ActionPayload, result_allowed: bool, reason: str) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        audit_id = str(uuid.uuid4())
        record = AuditRecord(
            audit_id=audit_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            action_name=payload.action_name,
            allowed=result_allowed,
            reason=reason,
            metadata=sanitize_metadata(payload.metadata),
        )

        with self.path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(record.model_dump()) + "\n")

        return audit_id


class SQLiteAuditWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def write(self, payload: ActionPayload, result_allowed: bool, reason: str) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        audit_id = str(uuid.uuid4())
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        metadata_json = json.dumps(sanitize_metadata(payload.metadata))

        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_records (
                    audit_id TEXT PRIMARY KEY,
                    timestamp_utc TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    allowed INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT INTO audit_records (
                    audit_id,
                    timestamp_utc,
                    action_name,
                    allowed,
                    reason,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    timestamp_utc,
                    payload.action_name,
                    int(result_allowed),
                    reason,
                    metadata_json,
                ),
            )

        return audit_id


def sanitize_metadata(metadata: dict) -> dict:
    sanitized = metadata.copy()
    for key, value in sanitized.items():
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            sanitized[key] = str(value)
    return sanitized
