import uuid
from datetime import datetime
from typing import Dict, List, Optional

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'history': [],
            'metadata': {}
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, message: Dict):
        if session_id in self.sessions:
            self.sessions[session_id]['history'].append({
                **message,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        session = self.get_session(session_id)
        if session:
            return session['history'][-limit:]
        return []
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
