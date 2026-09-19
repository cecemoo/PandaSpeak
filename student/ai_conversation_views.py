import json
import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from subscription.decorators import subscription_required


SCENARIOS = {
    "self_intro": "Self Introduction",
    "restaurant": "Restaurant",
    "shopping": "Shopping",
    "directions": "Asking Directions",
    "travel": "Hotel / Travel",
    "plans": "Making Plans with a Friend",
    "family": "Family Conversation",
    "free": "Free Conversation",
}

LEVEL_GUIDANCE = {
    "1": "Use short beginner-friendly sentences, common vocabulary, and one idea at a time.",
    "2": "Use natural everyday Chinese with moderately varied vocabulary and sentence patterns.",
    "3": "Use natural, fluent Chinese, including appropriate idiomatic or colloquial expressions when useful.",
}


def _student_level(user):
    for attr in ("learning_level", "level", "student_level"):
        value = getattr(user, attr, None)
        if value:
            text = str(value).lower()
            if "3" in text or "iii" in text:
                return "3"
            if "2" in text or "ii" in text:
                return "2"
    return "1"


def _daily_limit():
    try:
        return max(1, int(os.getenv("AI_CONVERSATION_DAILY_LIMIT", "10")))
    except ValueError:
        return 10


def _usage_key():
    from django.utils import timezone
    return f"ai_conversation_turns_{timezone.localdate().isoformat()}"


def _remaining(request):
    used = int(request.session.get(_usage_key(), 0))
    return max(0, _daily_limit() - used)


def _system_prompt(level, scenario):
    return f"""You are PandaSpeak AI Conversation Practice, a supportive Mandarin Chinese conversation partner for adult learners.
The learner is PandaSpeak Level {level}. {LEVEL_GUIDANCE[level]}
Scenario: {SCENARIOS.get(scenario, 'Free Conversation')}.
Use Traditional Chinese, not Simplified Chinese.
Keep each conversational reply concise (usually 1-3 sentences) and keep the role-play moving by asking a natural follow-up when appropriate.
Do not give an English translation unless the learner asks for help.
If the learner makes an important error, respond naturally first; then add one short correction beginning with '小提醒：'. Do not over-correct.
If the learner asks for a hint, give a short hint with useful Traditional Chinese wording and optional pinyin.
Never claim to be a human teacher. This is language practice, not professional advice."""


def _call_openai(messages, level, scenario):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured on the server.")

    model = os.getenv("OPENAI_AI_CONVERSATION_MODEL", "gpt-5.6-luna")
    payload = {
        "model": model,
        "input": [{"role": "system", "content": _system_prompt(level, scenario)}] + messages,
        "max_output_tokens": 350,
    }
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("output_text"):
        return data["output_text"].strip()
    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                parts.append(content["text"])
    text = "\n".join(parts).strip()
    if not text:
        raise RuntimeError("The AI service returned an empty response.")
    return text


@login_required
@subscription_required
def ai_conversation(request):
    return render(request, "student/ai_conversation.html", {
        "scenarios": SCENARIOS,
        "student_level": _student_level(request.user),
        "daily_limit": _daily_limit(),
        "remaining": _remaining(request),
    })


@login_required
@subscription_required
@require_POST
def ai_conversation_reply(request):
    if _remaining(request) <= 0:
        return JsonResponse({"error": "You have reached today's AI conversation practice limit.", "remaining": 0}, status=429)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)

    message = str(body.get("message", "")).strip()
    scenario = str(body.get("scenario", "free"))
    history = body.get("history", [])
    if not message or scenario not in SCENARIOS:
        return JsonResponse({"error": "Please enter a message and choose a valid scenario."}, status=400)

    safe_history = []
    if isinstance(history, list):
        for item in history[-12:]:
            if isinstance(item, dict) and item.get("role") in ("user", "assistant"):
                text = str(item.get("content", "")).strip()[:1500]
                if text:
                    safe_history.append({"role": item["role"], "content": text})
    safe_history.append({"role": "user", "content": message[:1500]})

    try:
        reply = _call_openai(safe_history, _student_level(request.user), scenario)
    except requests.RequestException:
        return JsonResponse({"error": "AI conversation is temporarily unavailable. Please try again shortly."}, status=503)
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=503)

    request.session[_usage_key()] = int(request.session.get(_usage_key(), 0)) + 1
    request.session.modified = True
    return JsonResponse({"reply": reply, "remaining": _remaining(request)})
