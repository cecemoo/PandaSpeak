import hashlib
import json
import os
from decimal import Decimal

import requests
from opencc import OpenCC
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from subscription.decorators import subscription_required
from subscription.plan_access import ai_conversation_limit, is_plus
from .models import AIConversationUsage, AICachedSpeech

SCENARIOS={"self_intro":"Self Introduction","restaurant":"Restaurant","shopping":"Shopping","directions":"Asking Directions","travel":"Hotel / Travel","plans":"Making Plans with a Friend","family":"Family Conversation","free":"Free Conversation"}
LEVEL_GUIDANCE={"1":"Use short beginner-friendly sentences, common vocabulary, and one idea at a time.","2":"Use natural everyday Chinese with moderately varied vocabulary and sentence patterns.","3":"Use natural, fluent Chinese, including appropriate idiomatic or colloquial expressions when useful."}
TRADITIONAL_CONVERTER=OpenCC('s2twp')
MANDARIN_SPEECH_CONVERTER=OpenCC('t2s')
STANDARD_MANDARIN_REPLACEMENTS={'喫':'吃','哪兒':'哪裡','這兒':'這裡','那兒':'那裡'}


def _traditional(text):
    value=TRADITIONAL_CONVERTER.convert(str(text or ''))
    for source,target in STANDARD_MANDARIN_REPLACEMENTS.items():value=value.replace(source,target)
    return value


def _student_level(user):
    for attr in ("learning_level","level","student_level"):
        value=getattr(user,attr,None)
        if value:
            text=str(value).lower()
            if "3" in text or "iii" in text:return "3"
            if "2" in text or "ii" in text:return "2"
    return "1"


def _monthly_used(user):
    now=timezone.localtime()
    return AIConversationUsage.objects.filter(student=user,kind='reply',created_at__year=now.year,created_at__month=now.month).count()


def _remaining(user):
    return max(0,ai_conversation_limit(user)-_monthly_used(user))


def _system_prompt(level,scenario):
    return f"""You are PandaSpeak AI Conversation Practice, a supportive Standard Mandarin Chinese conversation partner for adult learners.
The learner is PandaSpeak Level {level}. {LEVEL_GUIDANCE[level]}
Scenario: {SCENARIOS.get(scenario,'Free Conversation')}.
Write every Chinese character in Traditional Chinese. Never output Simplified Chinese characters.
Speak and write natural modern Standard Mandarin (標準國語). Do not write Cantonese, Cantonese-style written Chinese, Taiwanese Hokkien, or regional dialect grammar.
Use vocabulary natural to Standard Mandarin written in Traditional Chinese. Use「吃」not「喫」,「哪裡」not「哪兒」,「這裡」not「這兒」, and「那裡」not「那兒」.
Avoid Cantonese sentence-final particles or wording such as「嘅」「咁」「喺」「冇」「唔」「佢」「哋」「啲」「咗」「緊」「嚟」「啦」when they are being used as Cantonese grammar.
Keep each conversational reply concise (usually 1-3 sentences) and keep the role-play moving by asking a natural follow-up when appropriate.
Do not give an English translation unless the learner asks for help.
Prioritize natural conversation. Do not look for mistakes merely to provide a correction.
Only add a correction beginning with '小提醒：' when the learner has made a genuine, meaningful Chinese language error that you can identify with high confidence.
The learner's speech transcription is automatically converted to Traditional Chinese before you receive it. Never add a reminder merely about Simplified versus Traditional character forms.
Never tell the learner to use Traditional Chinese when the learner's wording is already correctly written in Traditional Chinese.
If you are uncertain whether something is an error, do not correct it; simply continue the conversation naturally.
If the learner asks for a hint, give a short hint with useful Traditional Chinese wording and optional pinyin.
Never claim to be a human teacher. This is language practice, not professional advice."""


def _api_key():
    key=os.getenv("OPENAI_API_KEY","")
    if not key:raise RuntimeError("OPENAI_API_KEY is not configured on the server.")
    return key


def _reply_cost(input_tokens,output_tokens):
    in_rate=Decimal(os.getenv("AI_REPLY_INPUT_USD_PER_MILLION","0.20"));out_rate=Decimal(os.getenv("AI_REPLY_OUTPUT_USD_PER_MILLION","1.20"))
    return (Decimal(input_tokens)*in_rate+Decimal(output_tokens)*out_rate)/Decimal(1000000)


def _speech_cost(text):
    return Decimal(len(text))*Decimal(os.getenv("AI_TTS_ESTIMATED_USD_PER_1K_CHARS","0.015"))/Decimal(1000)


def _call_openai(messages,level,scenario):
    model=os.getenv("OPENAI_AI_CONVERSATION_MODEL","gpt-5.6-luna")
    payload={"model":model,"input":[{"role":"system","content":_system_prompt(level,scenario)}]+messages,"max_output_tokens":350}
    r=requests.post("https://api.openai.com/v1/responses",headers={"Authorization":f"Bearer {_api_key()}","Content-Type":"application/json"},json=payload,timeout=30);r.raise_for_status();data=r.json()
    text=data.get("output_text","").strip()
    if not text:
        parts=[]
        for item in data.get("output",[]):
            for content in item.get("content",[]):
                if content.get("type")=="output_text" and content.get("text"):parts.append(content["text"])
        text="\n".join(parts).strip()
    if not text:raise RuntimeError("The AI service returned an empty response.")
    usage=data.get("usage") or {};return _traditional(text),model,int(usage.get("input_tokens",0) or 0),int(usage.get("output_tokens",0) or 0)


@login_required
@subscription_required
def ai_conversation(request):
    limit=ai_conversation_limit(request.user)
    return render(request,"student/ai_conversation.html",{"scenarios":SCENARIOS,"student_level":_student_level(request.user),"conversation_limit":limit,"remaining":_remaining(request.user),"is_plus":is_plus(request.user)})


@login_required
@subscription_required
@require_POST
def ai_conversation_traditionalize(request):
    try:body=json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError,UnicodeDecodeError):return JsonResponse({"error":"Invalid request."},status=400)
    text=str(body.get("text","")).strip()[:1500]
    return JsonResponse({"text":_traditional(text) if text else ""})


@login_required
@subscription_required
@require_POST
def ai_conversation_reply(request):
    if _remaining(request.user)<=0:
        return JsonResponse({"error":"You have reached your monthly AI conversation practice limit.","remaining":0,"upgrade_available":not is_plus(request.user)},status=429)
    try:body=json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError,UnicodeDecodeError):return JsonResponse({"error":"Invalid request."},status=400)
    message=_traditional(str(body.get("message","")).strip());scenario=str(body.get("scenario","free"));history=body.get("history",[])
    if not message or scenario not in SCENARIOS:return JsonResponse({"error":"Please enter a message and choose a valid scenario."},status=400)
    safe=[]
    if isinstance(history,list):
        for item in history[-12:]:
            if isinstance(item,dict) and item.get("role") in ("user","assistant"):
                text=_traditional(str(item.get("content","")).strip())[:1500]
                if text:safe.append({"role":item["role"],"content":text})
    safe.append({"role":"user","content":message[:1500]})
    try:reply,model,input_tokens,output_tokens=_call_openai(safe,_student_level(request.user),scenario)
    except requests.RequestException:return JsonResponse({"error":"AI conversation is temporarily unavailable. Please try again shortly."},status=503)
    except RuntimeError as exc:return JsonResponse({"error":str(exc)},status=503)
    AIConversationUsage.objects.create(student=request.user,kind='reply',model_name=model,input_units=input_tokens,output_units=output_tokens,estimated_cost_usd=_reply_cost(input_tokens,output_tokens))
    return JsonResponse({"reply":reply,"remaining":_remaining(request.user),"upgrade_available":not is_plus(request.user)})


@login_required
@subscription_required
@require_POST
def ai_conversation_speech(request):
    try:body=json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError,UnicodeDecodeError):return JsonResponse({"error":"Invalid request."},status=400)
    text=_traditional(str(body.get("text","")).strip())[:2000];choice=str(body.get("voice","female")).lower()
    if not text:return JsonResponse({"error":"No text to speak."},status=400)
    speech_text=MANDARIN_SPEECH_CONVERTER.convert(text);voice="onyx" if choice=="male" else "coral";model=os.getenv("OPENAI_AI_TTS_MODEL","gpt-4o-mini-tts")
    cache_version="standard-mandarin-v4";key=hashlib.sha256(f"{cache_version}|{model}|{voice}|{speech_text}".encode("utf-8")).hexdigest();cached=AICachedSpeech.objects.filter(cache_key=key).first()
    if cached:
        AIConversationUsage.objects.create(student=request.user,kind='speech',model_name=model,input_units=len(text),estimated_cost_usd=0,cached=True)
        return HttpResponse(bytes(cached.audio),content_type="audio/mpeg",headers={"X-PandaSpeak-AI-Cache":"HIT"})
    payload={"model":model,"voice":voice,"input":speech_text,"instructions":"Read the supplied Chinese text verbatim in Standard Mandarin Chinese (Putonghua / 標準國語) pronunciation. The language is Mandarin Chinese, not Cantonese. Use standard Mandarin phonology and tones for every Chinese character. Do NOT use Cantonese pronunciation, Cantonese readings, Cantonese particles, Taiwanese Hokkien, or any other regional reading. Do not translate, paraphrase, add, omit, or explain any words.","response_format":"mp3"}
    try:r=requests.post("https://api.openai.com/v1/audio/speech",headers={"Authorization":f"Bearer {_api_key()}","Content-Type":"application/json"},json=payload,timeout=45);r.raise_for_status()
    except requests.RequestException:return JsonResponse({"error":"Standard Mandarin voice is temporarily unavailable."},status=503)
    except RuntimeError as exc:return JsonResponse({"error":str(exc)},status=503)
    AICachedSpeech.objects.update_or_create(cache_key=key,defaults={"voice":voice,"text":text,"audio":r.content})
    AIConversationUsage.objects.create(student=request.user,kind='speech',model_name=model,input_units=len(text),estimated_cost_usd=_speech_cost(text),cached=False)
    return HttpResponse(r.content,content_type="audio/mpeg",headers={"X-PandaSpeak-AI-Cache":"MISS"})
