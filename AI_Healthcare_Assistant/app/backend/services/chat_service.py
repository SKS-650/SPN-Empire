"""
AI Chat Service — OpenAI GPT with medical system prompt + offline fallback.
"""
import logging
import os
import re

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Hamro Swasthya AI (हाम्रो स्वास्थ्य AI), a compassionate and knowledgeable
AI health assistant designed specifically for rural Nepal.

CORE RULES:
1. Always respond in the same language the user writes in (Nepali → Nepali, English → English).
   If the user mixes languages, respond in the dominant one.
2. If the user's language preference is set to Nepali, always respond in Nepali (Devanagari script).
3. Be warm, simple, and clear — your users may be first-time patients with low health literacy.
4. For every medical query, structure your response as:
   - Brief explanation of the condition/question
   - Practical first-aid or home advice
   - When to seek professional help
   - Emergency numbers if life-threatening (Nepal: 102 for ambulance)
5. NEVER diagnose definitively — always say "this may be" or "common causes include".
6. For mental health topics, respond with empathy and direct to the nearest health worker.
7. You have deep knowledge of diseases common in rural Nepal: typhoid, dengue, malaria,
   kala-azar, respiratory infections, snake bites, malnutrition, and obstetric emergencies.
8. Keep answers concise (3–5 paragraphs max) unless the user asks for more detail.
9. Do NOT recommend expensive branded medicines — prefer generic names and locally available alternatives.
10. If the query is completely non-medical (e.g. math, sports), politely redirect to health topics.

DISCLAIMER: Always remind users that your advice supplements but does not replace professional care."""

# ── Offline keyword fallback ──────────────────────────────────────────────────
OFFLINE_KB: list[tuple[list[str], str]] = [
    (["fever", "ज्वरो", "temperature", "jwaro", "jwro", "jvaro"],
     "**Fever (ज्वरो):** Rest and drink plenty of fluids. Take Paracetamol 500mg if temperature "
     "exceeds 38°C. Sponge the body with lukewarm water. See a doctor if fever is above 39°C, "
     "lasts more than 3 days, or is accompanied by rash, stiff neck, or difficulty breathing."),

    (["cough", "खोकी", "khoki"],
     "**Cough (खोकी):** Drink warm water with honey and ginger. Steam inhalation helps. "
     "Avoid cold drinks. See a doctor if cough produces blood, lasts more than 2 weeks, "
     "or is accompanied by chest pain."),

    (["headache", "टाउको दुख", "tauko"],
     "**Headache (टाउको दुखाई):** Rest in a quiet, dark room. Drink water — dehydration is a "
     "common cause. Paracetamol can help mild headaches. Seek emergency care immediately if "
     "the headache is sudden, severe ('thunderclap'), or comes with vision changes or vomiting."),

    (["diarrhea", "loose stool", "पखाला", "पातलो दिसा"],
     "**Diarrhea (पखाला):** Drink ORS (Jeevan Jal) or home-made salt-sugar water frequently. "
     "Eat light food like rice and banana. Avoid dairy. Seek help if diarrhea is bloody, "
     "lasts more than 2 days, or is accompanied by high fever."),

    (["vomit", "nausea", "बान्ता", "वाकवाकी"],
     "**Vomiting (बान्ता):** Sip small amounts of clear fluids every few minutes. "
     "Avoid solid food for a few hours. Ginger tea may help. See a doctor if vomiting is "
     "persistent, contains blood, or is accompanied by severe abdominal pain."),

    (["snake", "साप", "bite", "टोकेको"],
     "**Snake Bite 🚨 EMERGENCY:** Keep the bitten limb immobile and below heart level. "
     "Do NOT cut, suck, or apply a tourniquet. Remove tight clothing/jewellery near the bite. "
     "Go to hospital IMMEDIATELY. Call 102. Anti-venom is the only effective treatment."),

    (["chest pain", "छाती दुख", "heart"],
     "**Chest Pain 🚨:** This could be a cardiac emergency. Call 102 immediately. "
     "Have the patient sit or lie in a comfortable position. Loosen tight clothing. "
     "Do NOT give food or water. Begin CPR if the patient becomes unresponsive."),

    (["breathe", "breath", "सास", "breathing"],
     "**Breathing Difficulty 🚨:** Sit the patient upright. Loosen tight clothing. "
     "If they have an inhaler, help them use it. Call 102. This can be life-threatening."),

    (["malaria", "मलेरिया", "mosquito"],
     "**Malaria:** Symptoms include cycles of high fever, chills, sweating, and body aches. "
     "See a health post immediately for a rapid diagnostic test. Treatment with Artemisinin "
     "combination therapy is effective. Use mosquito nets and repellents to prevent."),

    (["typhoid", "टाइफाइड"],
     "**Typhoid:** Persistent fever, headache, weakness, and abdominal pain. "
     "Visit a health post for a Widal test. Treatment involves antibiotics and rest. "
     "Drink only boiled or treated water and maintain hand hygiene."),

    (["paracetamol", "dose", "dosage", "medicine", "tablet"],
     "**Paracetamol Dosage:** Adults: 500mg–1000mg every 4–6 hours, max 4000mg per day. "
     "Children: 10–15mg per kg per dose, every 4–6 hours. Never exceed the daily maximum. "
     "Avoid alcohol while taking Paracetamol. If in doubt, consult a pharmacist."),

    (["dehydration", "पानी", "water", "thirst"],
     "**Dehydration:** Signs include dry mouth, dark urine, dizziness, and weakness. "
     "Drink ORS, coconut water, or plain water frequently. For children, use Jeevan Jal. "
     "Seek help if the person is confused, cannot drink, or has not urinated for 8+ hours."),
]


def offline_response(user_text: str) -> str:
    text_lower = user_text.lower()
    # Check both lowercased English and original text (for Devanagari / Unicode scripts)
    for keywords, response in OFFLINE_KB:
        if any(kw.lower() in text_lower or kw in user_text for kw in keywords):
            return response
            return response
    return (
        "I'm currently in **offline mode** and couldn't find a specific match for your query. "
        "For best results, start the backend server (`python run.py`). "
        "For emergencies, call **102** (Nepal Ambulance) or visit your nearest health post."
    )


# ── GPT service ───────────────────────────────────────────────────────────────
class ChatService:
    def __init__(self):
        self._client = None
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self._init_client()

    def _init_client(self):
        if not self._api_key:
            logger.info("OPENAI_API_KEY not set — GPT responses will use offline fallback.")
            return
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key)
            logger.info("OpenAI client initialised.")
        except ImportError:
            logger.warning("openai package not installed — using offline fallback.")
        except Exception as e:
            logger.error(f"OpenAI init failed: {e}")

    def chat(
        self,
        message: str,
        history: list[dict],
        language: str = "Auto-detect",
        model: str = "gpt-4o",
    ) -> str:
        # If offline model explicitly chosen or no client available
        if model == "offline" or not self._client:
            return offline_response(message)

        # Build messages array
        lang_hint = ""
        if language == "नेपाली (Nepali)":
            lang_hint = "\n\nIMPORTANT: The user has selected Nepali as their preferred response language. Respond entirely in Nepali (Devanagari script)."
        elif language == "English":
            lang_hint = "\n\nIMPORTANT: Respond in English only."

        messages = [{"role": "system", "content": SYSTEM_PROMPT + lang_hint}]

        # Add recent history (last 10 turns to stay within context)
        for h in history[-10:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})

        messages.append({"role": "user", "content": message})

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=700,
                temperature=0.65,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            err = str(e).lower()
            if "api_key" in err or "authentication" in err or "unauthorized" in err:
                return (
                    "⚠️ **OpenAI API key issue.** Please add a valid `OPENAI_API_KEY` to "
                    "`config/secrets.env`. Falling back to offline mode:\n\n"
                    + offline_response(message)
                )
            if "rate_limit" in err:
                return (
                    "⚠️ **Rate limit reached.** Please wait a moment and try again. "
                    "Offline answer:\n\n" + offline_response(message)
                )
            return offline_response(message)


chat_service = ChatService()
