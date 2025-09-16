"""In-memory simulation state for the LLM village prototype."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import random
from typing import Dict, List, Optional

from .models import DialogueLog, Mood, NPC


POSITIVE_KEYWORDS = {
    "감사", "고마", "멋져", "좋", "사랑", "행복", "도와", "친절",
}
NEGATIVE_KEYWORDS = {
    "싫", "나쁘", "화나", "짜증", "귀찮", "실망", "못해",
}


def _create_initial_npcs() -> Dict[str, NPC]:
    """Return a deterministic set of prototype NPCs."""

    return {
        "astro": NPC(
            npc_id="astro",
            name="별이",
            role="점성술사",
            personality="차분하고 신비로운 말투로 상대를 위로함",
            biography="마을의 별점을 책임지는 점성술사. 매일 새벽 별자리를 읽는다.",
            hunger=20,
        ),
        "shopkeeper": NPC(
            npc_id="shopkeeper",
            name="다온",
            role="상점 주인",
            personality="장난기 있지만 장사에는 진지함",
            biography="작은 잡화점을 운영하며 마을 경제를 챙긴다.",
            stamina=80,
        ),
        "chief": NPC(
            npc_id="chief",
            name="하람",
            role="촌장",
            personality="차분하지만 결정이 빠른 지도자",
            biography="마을 사람들의 의견을 모아 축제를 기획한다.",
        ),
    }


class GameState:
    """Mutable state container for the web simulation."""

    def __init__(self) -> None:
        self.npcs: Dict[str, NPC] = _create_initial_npcs()
        self.logs: List[DialogueLog] = []
        self.day: int = 1
        self.time_slice: int = 0
        random.seed(42)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------
    def serialise_npcs(self) -> List[Dict[str, object]]:
        """Return NPCs as dictionaries for the API."""

        return [
            {
                **asdict(npc),
                "mood": npc.derive_mood().value,
                "last_dialogue": npc.last_dialogue.isoformat()
                if npc.last_dialogue
                else None,
            }
            for npc in self.npcs.values()
        ]

    def serialise_logs(self, limit: Optional[int] = None) -> List[Dict[str, object]]:
        """Return the most recent conversation entries."""

        entries = self.logs[-limit:] if limit else self.logs
        return [log.to_dict() for log in entries]

    # ------------------------------------------------------------------
    # Simulation operations
    # ------------------------------------------------------------------
    def record_dialogue(
        self,
        speaker_id: str,
        message: str,
        target_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Append a dialogue log entry and update metadata."""

        now = datetime.utcnow()
        entry = DialogueLog(
            timestamp=now,
            speaker_id=speaker_id,
            target_id=target_id,
            message=message,
            tags=tags or {},
        )
        self.logs.append(entry)
        if speaker_id in self.npcs:
            self.npcs[speaker_id].last_dialogue = now
            self.npcs[speaker_id].dialog_history.append(len(self.logs) - 1)
        if target_id and target_id in self.npcs:
            self.npcs[target_id].dialog_history.append(len(self.logs) - 1)

    def apply_user_interaction(self, npc_id: str, message: str) -> Dict[str, object]:
        """Update NPC state according to a user message and produce a reply."""

        if npc_id not in self.npcs:
            raise KeyError(f"Unknown NPC id: {npc_id}")

        npc = self.npcs[npc_id]
        affection_delta = self._estimate_affection_delta(message)
        npc.adjust_affection(affection_delta)
        npc.stamina = max(0, npc.stamina - 5)
        npc.hunger = min(100, npc.hunger + 3)

        reply = self._generate_npc_reply(npc, message, affection_delta)
        self.record_dialogue("player", message, npc_id, tags={"type": "user"})
        self.record_dialogue(npc_id, reply, "player", tags={"type": "npc"})

        return {
            "reply": reply,
            "affection_change": affection_delta,
            "npc": {
                **asdict(npc),
                "mood": npc.derive_mood().value,
                "last_dialogue": npc.last_dialogue.isoformat()
                if npc.last_dialogue
                else None,
            },
        }

    def advance_time(self, steps: int = 1) -> Dict[str, object]:
        """Advance the simulation by a number of steps."""

        summaries: List[str] = []
        for _ in range(steps):
            self.time_slice += 1
            if self.time_slice % 4 == 0:
                self.day += 1
                self._new_day_reset()
            self._npc_background_conversations()
            self._apply_stat_changes()
            summaries.append(
                f"시간이 흘러 현재 {self.day}일차 {self.time_slice % 4}번째 시간입니다."
            )
        return {
            "day": self.day,
            "time_slice": self.time_slice,
            "summaries": summaries,
        }

    def reset(self) -> None:
        """Restore the initial state."""

        self.__init__()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _estimate_affection_delta(self, message: str) -> int:
        """Heuristic scoring to emulate a lightweight sentiment check."""

        lowered = message.lower()
        pos_hits = sum(keyword in lowered for keyword in POSITIVE_KEYWORDS)
        neg_hits = sum(keyword in lowered for keyword in NEGATIVE_KEYWORDS)
        return max(-5, min(5, pos_hits * 3 - neg_hits * 3))

    def _generate_npc_reply(
        self, npc: NPC, message: str, affection_delta: int
    ) -> str:
        """Produce a context-aware reply without external LLM calls."""

        mood = npc.derive_mood()
        if affection_delta > 0:
            acknowledgement = "고마워요."
        elif affection_delta < 0:
            acknowledgement = "조금 마음이 상했어요."
        else:
            acknowledgement = "그렇군요."

        templates: Dict[Mood, str] = {
            Mood.HAPPY: (
                "{ack} 오늘 기분이 좋아요! 별들도 당신 편인 것 같아요."
            ),
            Mood.NEUTRAL: "{ack} 마을 소식은 늘 조용하네요.",
            Mood.TIRED: "{ack} 조금 쉬고 싶지만 이야기 나누는 건 좋아요.",
            Mood.HUNGRY: "{ack} 배가 좀 고파서인지 집중이 잘 안 되네요.",
            Mood.EXHAUSTED: "{ack} 오늘은 힘이 빠져서 대답이 늦을지도 몰라요.",
        }
        template = templates[mood]
        reply = template.format(ack=acknowledgement)
        if npc.role == "점성술사":
            reply += " 별자리가 전하는 작은 조언도 곧 전해드릴게요."
        elif npc.role == "상점 주인":
            reply += " 가게에 신선한 물건이 들어왔답니다."
        elif npc.role == "촌장":
            reply += " 마을 사람들을 위해 더 나은 결정을 고민 중이죠."

        if "도와" in message:
            reply += " 언제든 도움이 필요하면 말씀하세요."
        return reply

    def _npc_background_conversations(self) -> None:
        """Generate lightweight NPC to NPC chatter."""

        npc_ids = list(self.npcs.keys())
        if len(npc_ids) < 2:
            return

        speaker_id, target_id = random.sample(npc_ids, 2)
        speaker = self.npcs[speaker_id]
        target = self.npcs[target_id]

        mood = speaker.derive_mood()
        if mood == Mood.HAPPY:
            text = f"{target.name}씨, 오늘 별빛이 특히 반짝여요!"
        elif mood == Mood.HUNGRY:
            text = f"{target.name}씨, 혹시 남는 간식이 있나요?"
        elif mood == Mood.TIRED:
            text = f"{target.name}씨, 오늘 일손이 좀 부족하네요."
        else:
            text = f"{target.name}씨, 마을 소식은 어떠세요?"

        self.record_dialogue(speaker_id, text, target_id, tags={"type": "npc_chatter"})
        target.adjust_affection(1)

    def _apply_stat_changes(self) -> None:
        """Apply passive stat drift to all NPCs."""

        for npc in self.npcs.values():
            npc.apply_daily_decay()

    def _new_day_reset(self) -> None:
        """Reset limited stats at the beginning of a day."""

        for npc in self.npcs.values():
            npc.stamina = min(100, npc.stamina + 20)
            npc.hunger = max(0, npc.hunger - 20)
            self.record_dialogue(
                npc.npc_id,
                "새로운 하루가 밝았어요. 모두 힘내봐요!",
                tags={"type": "daily_greeting"},
            )


# Global singleton used by the API layer.
STATE = GameState()
