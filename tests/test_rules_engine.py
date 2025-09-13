from app.schemas import InferenceRequest, UserState, MotionData, MotionMetrics, UserUtterance, SessionState
from app.rules_engine import decide


def base_req(**overrides):
    req = InferenceRequest(
        transaction_id="test-001",
        timestamp_ms=1757700000000,
        user_state=UserState(physical_fatigue=0.8, mental_focus=0.5, consecutive_form_errors=0),
        motion_data=MotionData(
            exercise_id="standing_march",
            rep_count_total=8,
            current_set_target_reps=10,
            form_error_detected="none",
            metrics=MotionMetrics(jitter_percent_increase=16.0, velocity_percent_decrease=5.0),
            uncertainty_score=0.9,
        ),
        user_utterance=UserUtterance(intent="silence", transcribed_text=""),
        session_state=SessionState(time_since_last_cue_ms=10000),
    )
    for k, v in overrides.items():
        setattr(req, k, v)
    return req


def test_fatigue_jitter_cue():
    resp = decide(base_req())
    assert "FATIGUE_JITTER" in resp["log"]["triggered_action"].get("cue_template_id", "")
    assert "shakiness" in resp["response"]["text_to_speak"].lower()


def test_question_reps_left():
    req = base_req(
        user_utterance=UserUtterance(intent="question_for_coach", transcribed_text="how many reps left?")
    )
    resp = decide(req)
    assert "reps" in resp["response"]["text_to_speak"].lower()
    assert resp["log"]["triggered_action"]["priority"] == "HIGH"


def test_form_microcue_range_low():
    req = base_req(
        motion_data=MotionData(
            exercise_id="standing_march",
            rep_count_total=3,
            current_set_target_reps=10,
            form_error_detected="range_too_low",
            metrics=MotionMetrics(jitter_percent_increase=0.0, velocity_percent_decrease=0.0),
            uncertainty_score=0.9,
        ),
        session_state=SessionState(time_since_last_cue_ms=8000),
        user_utterance=UserUtterance(intent="silence", transcribed_text=""),
    )
    resp = decide(req)
    assert resp["log"]["triggered_action"]["cue_template_id"] == "FORM_RANGE"
    assert "range" in resp["response"]["text_to_speak"].lower()
