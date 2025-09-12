from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class UserState(BaseModel):
    physical_fatigue: float = Field(ge=0.0, le=1.0)
    mental_focus: float = Field(ge=0.0, le=1.0)
    consecutive_form_errors: int = 0

class MotionMetrics(BaseModel):
    jitter_percent_increase: Optional[float] = 0.0
    velocity_percent_decrease: Optional[float] = 0.0

class MotionData(BaseModel):
    exercise_id: str
    rep_count_total: int
    current_set_target_reps: int
    form_error_detected: str = "none"
    metrics: MotionMetrics = MotionMetrics()
    uncertainty_score: float = 1.0

class UserUtterance(BaseModel):
    transcribed_text: Optional[str] = ""
    intent: Optional[str] = "silence"

class SessionState(BaseModel):
    time_since_last_cue_ms: int = 0

class InferenceRequest(BaseModel):
    transaction_id: str
    timestamp_ms: int
    user_state: UserState
    motion_data: MotionData
    user_utterance: UserUtterance
    session_state: SessionState

class GeneratedResponse(BaseModel):
    text_to_speak: str

class InferenceLog(BaseModel):
    log_transaction_id: str
    log_timestamp_ms: int
    input_digest: Dict[str, Any]
    reasoning_chain: list[str]
    triggered_action: Dict[str, Any]
    generated_response: GeneratedResponse
    error_log: Dict[str, Any]

class InferenceResponse(BaseModel):
    log: InferenceLog
    response: GeneratedResponse
