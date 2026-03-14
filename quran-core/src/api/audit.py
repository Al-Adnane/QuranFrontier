"""Immutable audit logging."""
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AuditEntry:
    """Single audit log entry."""
    audit_id: str
    timestamp: datetime
    action: str
    actor: str
    actor_role: str
    resource_type: str
    resource_id: str
    changes: Dict[str, Any]
    details: Dict[str, Any]
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "actor": self.actor,
            "actor_role": self.actor_role,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "changes": self.changes,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash
        }


class AuditLog:
    """Immutable audit log with hash chain for integrity."""

    def __init__(self):
        """Initialize audit log."""
        self.entries: List[AuditEntry] = []
        self.last_hash: Optional[str] = None

    def _compute_hash(self, entry: AuditEntry) -> str:
        """Compute SHA256 hash of entry."""
        data = {
            "timestamp": entry.timestamp.isoformat(),
            "action": entry.action,
            "actor": entry.actor,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "changes": entry.changes,
            "details": entry.details,
            "previous_hash": entry.previous_hash
        }

        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def log_action(
        self,
        action: str,
        actor: str,
        actor_role: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log an action to the audit trail."""
        audit_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        entry = AuditEntry(
            audit_id=audit_id,
            timestamp=timestamp,
            action=action,
            actor=actor,
            actor_role=actor_role,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes or {},
            details=details or {},
            previous_hash=self.last_hash
        )

        # Compute hash
        entry.entry_hash = self._compute_hash(entry)
        self.last_hash = entry.entry_hash

        # Append to log (immutable)
        self.entries.append(entry)

        return entry

    def get_entries(
        self,
        actor: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """Query audit log with filters."""
        results = self.entries

        if actor:
            results = [e for e in results if e.actor == actor]
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]
        if action:
            results = [e for e in results if e.action == action]

        # Return paginated results in reverse order (most recent first)
        return results[::-1][offset:offset + limit]

    def verify_integrity(self) -> tuple[bool, List[str]]:
        """Verify integrity of audit log."""
        issues = []

        for i, entry in enumerate(self.entries):
            # Verify hash chain
            if i > 0:
                if entry.previous_hash != self.entries[i - 1].entry_hash:
                    issues.append(f"Entry {i}: Previous hash mismatch")

            # Verify entry hash
            recomputed_hash = self._compute_hash(entry)
            if recomputed_hash != entry.entry_hash:
                issues.append(f"Entry {i}: Entry hash mismatch")

        return len(issues) == 0, issues

    def export_json(self) -> str:
        """Export audit log as JSON."""
        data = {
            "total_entries": len(self.entries),
            "integrity_verified": self.verify_integrity()[0],
            "entries": [entry.to_dict() for entry in self.entries]
        }
        return json.dumps(data, indent=2)

    def export_csv(self) -> str:
        """Export audit log as CSV."""
        lines = [
            "audit_id,timestamp,action,actor,actor_role,resource_type,resource_id,entry_hash"
        ]

        for entry in self.entries:
            lines.append(
                f'"{entry.audit_id}","{entry.timestamp.isoformat()}","{entry.action}",'
                f'"{entry.actor}","{entry.actor_role}","{entry.resource_type}",'
                f'"{entry.resource_id}","{entry.entry_hash}"'
            )

        return "\n".join(lines)


# Global audit log instance
_audit_log = AuditLog()


def get_audit_log() -> AuditLog:
    """Get global audit log instance."""
    return _audit_log


def log_action(
    action: str,
    actor: str,
    actor_role: str,
    resource_type: str,
    resource_id: str,
    changes: Optional[Dict[str, Any]] = None,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """Log action and return audit ID."""
    entry = _audit_log.log_action(
        action=action,
        actor=actor,
        actor_role=actor_role,
        resource_type=resource_type,
        resource_id=resource_id,
        changes=changes,
        details=details
    )
    return entry.audit_id


def get_audit_entries(
    actor: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get audit log entries."""
    entries = _audit_log.get_entries(
        actor=actor,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        limit=limit,
        offset=offset
    )
    return [e.to_dict() for e in entries]
