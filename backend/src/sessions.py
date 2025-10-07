import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .config import _redis, SESSION_TTL_SECONDS


session_store: Dict[str, Dict[str, Any]] = {}


class SessionManager:
    @staticmethod
    def create_session(initial_data: dict) -> str:
        session_id = str(uuid.uuid4())
        payload = {
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "data": initial_data,
            "history": []
        }
        if _redis:
            try:
                _redis.setex(f"pla:session:{session_id}", SESSION_TTL_SECONDS, json.dumps(payload))
            except Exception:
                pass
        else:
            session_store[session_id] = {
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "data": initial_data,
                "history": []
            }
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[dict]:
        if _redis:
            try:
                raw = _redis.get(f"pla:session:{session_id}")
                if not raw:
                    return None
                obj = json.loads(raw)
                obj["last_accessed"] = datetime.now().isoformat()
                _redis.setex(f"pla:session:{session_id}", SESSION_TTL_SECONDS, json.dumps(obj))
                return obj
            except Exception:
                pass
        if session_id in session_store:
            session_store[session_id]["last_accessed"] = datetime.now()
            return session_store[session_id]
        return None

    @staticmethod
    def update_session(session_id: str, data: dict, action: str = "update"):
        if _redis:
            try:
                raw = _redis.get(f"pla:session:{session_id}")
                if not raw:
                    return
                obj = json.loads(raw)
                obj["data"].update(data)
                obj["last_accessed"] = datetime.now().isoformat()
                obj["history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": action,
                    "data": data
                })
                _redis.setex(f"pla:session:{session_id}", SESSION_TTL_SECONDS, json.dumps(obj))
                return
            except Exception:
                pass
        if session_id in session_store:
            session_store[session_id]["data"].update(data)
            session_store[session_id]["last_accessed"] = datetime.now()
            session_store[session_id]["history"].append({
                "timestamp": datetime.now(),
                "action": action,
                "data": data
            })

    @staticmethod
    def cleanup_old_sessions():
        cutoff = datetime.now() - timedelta(hours=24)
        to_remove = [sid for sid, session in session_store.items()
                     if session["last_accessed"] < cutoff]
        for sid in to_remove:
            del session_store[sid]


