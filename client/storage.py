"""Local state management for the terminal client."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ClientState:
    """Represents the terminal client's saved local state."""

    users: list[dict[str, str]] = field(default_factory=list)
    active_user_id: str | None = None
    active_word_id: str | None = None
    word_ids_by_user: dict[str, list[str]] = field(default_factory=dict)
    category_ids_by_user: dict[str, list[str]] = field(default_factory=dict)


class StateStore:
    """Persist client state in a small JSON file."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> ClientState:
        """Load state from disk, falling back to empty defaults."""
        if not self.path.exists():
            return ClientState()

        data = json.loads(self.path.read_text(encoding="utf-8"))
        return ClientState(
            users=data.get("users", []),
            active_user_id=data.get("active_user_id"),
            active_word_id=data.get("active_word_id"),
            word_ids_by_user=data.get("word_ids_by_user", {}),
            category_ids_by_user=data.get("category_ids_by_user", {}),
        )

    def save(self, state: ClientState) -> None:
        """Persist state to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "users": state.users,
                    "active_user_id": state.active_user_id,
                    "active_word_id": state.active_word_id,
                    "word_ids_by_user": state.word_ids_by_user,
                    "category_ids_by_user": state.category_ids_by_user,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
