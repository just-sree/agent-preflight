import json

from agent_preflight.audit import AuditWriter
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
