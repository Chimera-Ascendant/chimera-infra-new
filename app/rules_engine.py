import time
from .schemas import InferenceRequest


def _digest(req: InferenceRequest):
    return {
        "fatigue": req.user_state.physical_fatigue,
        "focus": req.user_state.mental_focus,
        "form_error": req.motion_data.form_error_detected,
        "jitter_increase": req.motion_data.metrics.jitter_percent_increase or 0.0,
        "velocity_drop": req.motion_data.metrics.velocity_percent_decrease or 0.0,
        "user_intent": req.user_utterance.intent or "silence",
    }


def decide(req: InferenceRequest):
    now_ms = int(time.time() * 1000)
    rc = []

    # 4.1 Pre-computation & Sanity Checks (subset)
    rc.append("Rule 1.1: Input schema validated.")
    is_high_fatigue = req.user_state.physical_fatigue > 0.75
    if is_high_fatigue:
        rc.append("Rule 1.3: IS_HIGH_FATIGUE=true")
    is_low_focus = req.user_state.mental_focus < 0.35
    if is_low_focus:
        rc.append("Rule 1.4: IS_LOW_FOCUS=true")
    is_form_breakdown = (
        (req.motion_data.form_error_detected != "none")
        and (req.user_state.consecutive_form_errors >= 2)
    )
    if is_form_breakdown:
        rc.append("Rule 1.5: IS_FORM_BREAKDOWN=true")
    is_movement_shaky = (req.motion_data.metrics.jitter_percent_increase or 0.0) > 12.0
    if is_movement_shaky:
        rc.append("Rule 1.7: IS_MOVEMENT_SHAKY=true")

    reps_remaining = max(req.motion_data.current_set_target_reps - req.motion_data.rep_count_total, 0)
    rc.append(f"Rule 1.8: reps_remaining={reps_remaining}")
    time_since_last_cue_ms = getattr(req.session_state, "time_since_last_cue_ms", 0)

    # 4.2 Prioritization (subset)
    intent = (req.user_utterance.intent or "").lower()
    intent_text = (req.user_utterance.transcribed_text or "").lower()

    action = {"action_type": "NONE", "priority": "LOW", "cue_template_id": None}
    speak = ""

    # 3.1 [direct_command]
    if intent == "direct_command":
        if "stop" in intent_text or "end" in intent_text:
            action = {"action_type": "STOP_WORKOUT", "priority": "CRITICAL"}
            speak = "Workout stopped."
            rc.append("Rule 3.1.1: ACTION_STOP_WORKOUT")
        elif "pause" in intent_text:
            action = {"action_type": "PAUSE_WORKOUT", "priority": "CRITICAL"}
            speak = "Workout paused."
            rc.append("Rule 3.1.2: ACTION_PAUSE_WORKOUT")
        elif "next" in intent_text or "skip" in intent_text:
            action = {"action_type": "NEXT_EXERCISE", "priority": "CRITICAL"}
            speak = "Okay, moving to the next exercise."
            rc.append("Rule 3.1.3: ACTION_NEXT_EXERCISE")
    # 3.2 [question_for_coach]
    elif intent == "question_for_coach":
        # 3.2.1 reps left
        if ("how many" in intent_text) or ("reps left" in intent_text):
            base = f"You have {reps_remaining} reps to go."
            if is_form_breakdown:
                base += " Focus on keeping good form."
                rc.append("Rule 3.2.3: Appending micro-cue for form.")
            elif is_high_fatigue:
                base += " You're almost there."
                rc.append("Rule 3.2.2: Empathy phrase for fatigue.")
            speak = base
            action = {"action_type": "GENERATE_SPEECH", "priority": "HIGH", "cue_template_id": "REPS_LEFT"}
            rc.append("Rule 3.2.1: Responding to reps remaining question.")
        # 3.2.4 form question
        elif ("my form" in intent_text) or ("how was that" in intent_text):
            if req.motion_data.form_error_detected == "none":
                speak = "Your form on that last rep was solid."
                rc.append("Rule 3.2.5: Positive reinforcement.")
            else:
                speak = "I'm seeing an issue. Keep movements controlled and aligned."
                rc.append("Rule 3.2.6: Actionable correction.")
            action = {"action_type": "GENERATE_SPEECH", "priority": "HIGH", "cue_template_id": "FORM_RESPONSE"}
        else:
            speak = "I'm not sure I understand. Can you rephrase?"
            rc.append("Rule 3.2.9: Ambiguous question.")
            action = {"action_type": "GENERATE_SPEECH", "priority": "HIGH", "cue_template_id": "AMBIGUOUS"}
    # 4.1 Form correction (proactive)
    elif is_form_breakdown and time_since_last_cue_ms >= 7000:
        speak = "Let's pause a moment and reset your form. Focus on control."
        rc.append("Rule 4.1.1: Form correction cue.")
        action = {"action_type": "GENERATE_SPEECH", "priority": "HIGH", "cue_template_id": "FORM_CORRECTION"}
    # 4.x Form-specific micro-cues (single detection, gentle)
    elif (req.motion_data.form_error_detected in {"balance_unstable","range_too_low","jerk_high"}) and time_since_last_cue_ms >= 7000:
        err = req.motion_data.form_error_detected
        if err == "balance_unstable":
            speak = "Plant your feet and steady your balance."
            tmpl = "FORM_BALANCE"
        elif err == "range_too_low":
            speak = "Increase your range slightly—aim for a fuller motion."
            tmpl = "FORM_RANGE"
        else:  # jerk_high
            speak = "Smooth it out—control the tempo on each rep."
            tmpl = "FORM_JERK"
        rc.append(f"Rule 4.x: Micro-cue for {err}.")
        action = {"action_type": "GENERATE_SPEECH", "priority": "MEDIUM", "cue_template_id": tmpl}
    # 4.2 Fatigue-jitter cue
    elif is_high_fatigue and is_movement_shaky:
        speak = "I'm detecting some shakiness. Focus on controlling the movement."
        rc.append("Rule 4.2.1: FATIGUE_JITTER cue.")
        action = {"action_type": "GENERATE_SPEECH", "priority": "MEDIUM", "cue_template_id": "FATIGUE_JITTER"}
    # 5.1 Cue budget (very simplified enforcement happens outside in app)

    log = {
        "log_transaction_id": req.transaction_id,
        "log_timestamp_ms": now_ms,
        "input_digest": _digest(req),
        "reasoning_chain": rc,
        "triggered_action": action,
        "generated_response": {"text_to_speak": speak},
        "error_log": {"error_code": None, "error_message": None},
    }

    return {"log": log, "response": {"text_to_speak": speak}}
