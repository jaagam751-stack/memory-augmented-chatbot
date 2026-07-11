
import json
import re
from datetime import datetime
from typing import Dict, List

from app.utils.config import settings


class MemoryStore:
    """Simple JSON-based long-term memory for beginners."""

    def __init__(self) -> None:
        self.path = settings.memory_file
        if not self.path.exists():
            self._write({})

    def _read(self) -> Dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write(self, data: Dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _ensure_user(self, user_id: str) -> Dict:
        data = self._read()
        data.setdefault(user_id, {"profile": {}, "preferences": [], "conversations": []})
        self._write(data)
        return data[user_id]

    def get_memory(self, user_id: str) -> Dict:
        """Return all saved memory for one user."""
        return self._ensure_user(user_id)

    def memory_as_text(self, user_id: str, last_n: int = 5) -> str:
        """Convert memory into text that can be included in an LLM prompt."""
        memory = self.get_memory(user_id)
        profile = memory.get("profile", {})
        preferences = memory.get("preferences", [])
        conversations = memory.get("conversations", [])[-last_n:]

        history_text = "\n".join(
            f"User: {item['question']}\nAssistant: {item['answer']}"
            for item in conversations
        )

        return (
            f"Profile: {profile}\n"
            f"Preferences: {preferences}\n"
            f"Recent conversations:\n{history_text or 'No previous conversations.'}"
        )

    def update_from_user_message(self, user_id: str, message: str) -> None:
        """Extract simple memory facts from the user's message."""
        data = self._read()
        user_memory = data.setdefault(user_id, {"profile": {}, "preferences": [], "conversations": []})

        # Beginner-friendly rule-based extraction.
        name_match = re.search(r"(?:my name is|i am|i'm)\s+([A-Z][a-zA-Z]+)", message, re.IGNORECASE)
        if name_match:
            user_memory["profile"]["name"] = name_match.group(1).title()

        preference_match = re.search(r"(?:i like|i prefer|my preference is)\s+(.+)", message, re.IGNORECASE)
        if preference_match:
            preference = preference_match.group(1).strip().rstrip(".")
            if preference and preference not in user_memory["preferences"]:
                user_memory["preferences"].append(preference)

        self._write(data)

    def save_interaction(self, user_id: str, question: str, answer: str) -> None:
        """Save one conversation turn."""
        data = self._read()
        user_memory = data.setdefault(user_id, {"profile": {}, "preferences": [], "conversations": []})
        user_memory["conversations"].append(
            {
                "time": datetime.utcnow().isoformat() + "Z",
                "question": question,
                "answer": answer,
            }
        )
        # Keep file small for a beginner project.
        user_memory["conversations"] = user_memory["conversations"][-50:]
        self._write(data)

    def history(self, user_id: str) -> List[Dict]:
        return self.get_memory(user_id).get("conversations", [])
