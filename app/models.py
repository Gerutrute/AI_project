"""Domain models for the LLM village prototype."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class Mood(str, Enum):
    """Represents the high level emotion derived from NPC stats."""

    HAPPY = "happy"
    NEUTRAL = "neutral"
    TIRED = "tired"
    HUNGRY = "hungry"
    EXHAUSTED = "exhausted"


@dataclass
class NPC:
    """Data container with lightweight behaviour helpers for an NPC."""

    npc_id: str
    name: str
    role: str
    hp: int = 100
    stamina: int = 100
    hunger: int = 0
    affection: int = 0
    personality: str = ""
    biography: str = ""
    last_dialogue: Optional[datetime] = None
    dialog_history: List[int] = field(default_factory=list)

    def derive_mood(self) -> Mood:
        """Return the NPC mood calculated from its stats."""

        if self.stamina < 20 or self.hp < 20:
            return Mood.EXHAUSTED
        if self.hunger > 80:
            return Mood.HUNGRY
        if self.stamina < 50:
            return Mood.TIRED
        if self.affection > 40 and self.hunger < 30:
            return Mood.HAPPY
        return Mood.NEUTRAL

    def apply_daily_decay(self) -> None:
        """Update stats to simulate time passing."""

        # Hunger increases gradually while stamina recovers when possible.
        self.hunger = min(100, self.hunger + 10)
        if self.hunger > 70:
            self.stamina = max(0, self.stamina - 15)
        else:
            self.stamina = min(100, self.stamina + 10)
        # HP regenerates slowly if hunger is manageable.
        if self.hunger < 60:
            self.hp = min(100, self.hp + 5)
        else:
            self.hp = max(0, self.hp - 5)

    def adjust_affection(self, delta: int) -> None:
        """Apply affection delta with soft bounds."""

        self.affection = max(-100, min(100, self.affection + delta))


@dataclass
class DialogueLog:
    """Represents a single line of conversation in the village."""

    timestamp: datetime
    speaker_id: str
    target_id: Optional[str]
    message: str
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert the entry to a serialisable mapping."""

        return {
            "timestamp": self.timestamp.isoformat(),
            "speaker_id": self.speaker_id,
            "target_id": self.target_id,
            "message": self.message,
            "tags": self.tags,
        }
