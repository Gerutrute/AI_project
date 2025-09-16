"""FastAPI entry point for the LLM village prototype."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .state import STATE


class UserInteractionRequest(BaseModel):
    npc_id: str = Field(..., description="Identifier of the NPC to talk to")
    message: str = Field(..., min_length=1, description="Player utterance")


class AdvanceTimeRequest(BaseModel):
    steps: int = Field(1, ge=1, le=24, description="Number of time slices to advance")


app = FastAPI(title="LLM Village Prototype", version="0.1.0")


@app.get("/api/npcs")
def list_npcs() -> dict:
    """Return the current NPC roster and stats."""

    return {"npcs": STATE.serialise_npcs()}


@app.get("/api/logs")
def list_logs(limit: int | None = None) -> dict:
    """Return recent dialogue logs."""

    return {"logs": STATE.serialise_logs(limit=limit)}


@app.post("/api/interactions/user")
def interact_with_npc(payload: UserInteractionRequest) -> dict:
    """Apply the player's message to the NPC and return the response."""

    try:
        result = STATE.apply_user_interaction(payload.npc_id, payload.message)
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result


@app.post("/api/simulate/tick")
def advance_time(payload: AdvanceTimeRequest) -> dict:
    """Advance the simulation by the requested number of steps."""

    return STATE.advance_time(payload.steps)


@app.post("/api/admin/reset")
def reset_state() -> dict:
    """Reset the in-memory state to the initial scenario."""

    STATE.reset()
    return {"status": "ok"}
