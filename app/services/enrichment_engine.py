import json
import os
import re
import requests
from app.services.stats import clean_text

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

PLACEHOLDER_PATTERNS = (
    "a curated vocabulary item",
    "a simple meaning for",
    "definition is being prepared",
    "definition pending review",
    "no bangla translation",
    "no example",
    "no synonym",
    "no antonym",
    "not added yet",
    "n/a",
)

def _extract_json_text(content):
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return content

def generate_enrichment_payload(word, level=None, api_key=None, timeout=30, model=None):
    """
    Centralized service for ALL AI vocabulary enrichment generation.
    Used by both global search and flashcards.

    api_key: explicit Groq API key to use. When None, falls back to
             GROQ_API_KEY_SEARCH → GROQ_API_KEY (legacy) env vars.

    Raises GroqRateLimitError (a subclass of Exception) when the API
    returns HTTP 429 so callers can rotate keys safely.
    """
    from app.services.groq_provider import GroqRateLimitError

    if api_key is None:
        try:
            from app.services.groq_provider import groq_pool
            # Background callers that pass api_key=None get a worker key.
            # The /search route always passes api_key explicitly (dedicated key) — never reaches here.
            try:
                api_key = groq_pool.get_worker_key()
            except Exception:
                api_key = (
                    os.environ.get("GROQ_API_KEY_WORKER_1")
                    or os.environ.get("GROQ_API_KEY_SEARCH")
                    or os.environ.get("GROQ_API_KEY")
                )
        except ImportError:
            api_key = (
                os.environ.get("GROQ_API_KEY_WORKER_1")
                or os.environ.get("GROQ_API_KEY_SEARCH")
                or os.environ.get("GROQ_API_KEY")
            )
    if not model:
        model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        raise RuntimeError("No Groq API key configured (GROQ_API_KEY_SEARCH / GROQ_API_KEY).")

    word_clean = str(word).strip()
    level_str = str(level).strip() if level else "general"

    prompt = f"""
You are a professional bilingual English-Bangla dictionary editor for intermediate and advanced learners.

Word/Phrase to enrich: {word_clean}
Difficulty Level: {level_str}

Provide high-quality enrichment content.

Return ONLY a strict valid JSON object:
{{
  "word": "...",
  "part_of_speech": "...",
  "meaning": "...",
  "bangla_meaning": "...",
  "sentence": "...",
  "phonetic": "...",
  "synonym": "...",
  "antonym": "..."
}}

Rules for Fields:
- "word": You MUST keep the spelling of the word/phrase '{word_clean}' EXACTLY as received. Do NOT normalize, singularize, pluralize, simplify, split, or rewrite it, UNLESS the word is clearly misspelled or has minor typos (only in that case, you may return the corrected spelling in this field). If it is correct, return '{word_clean}' exactly.
- "part_of_speech": The most common modern part of speech for this word.
- "meaning": A natural, concise, dictionary-quality English explanation appropriate for learners. Do not repeat the word itself or use circular definitions. Avoid robotic placeholders. Length must be between 10 and 180 characters.
- "bangla_meaning": A natural, educational-quality Bangla translation. Avoid literal or awkward machine translation. Must sound natural to native speakers.
- "sentence": One realistic, contextual, grammatically correct English example sentence using '{word_clean}'. It MUST contain the exact word/phrase '{word_clean}' in context. Length must be >= 20 characters.
- "phonetic": Readable English pronunciation spelled phonetically, hyphenated by syllables. Do NOT use IPA symbols like /, [, ], ˈ, ˌ, ː, or non-English letters. Keep it clean and readable for non-native speakers (e.g., for "convenient" return "kun-VEEN-yunt").
- "synonym": One or two relevant synonyms as a comma-separated string, or an empty string if not available. Do not include placeholder text.
- "antonym": One relevant antonym, or an empty string if not available. Do not include placeholder text.

Strict Output Rules:
- Return ONLY JSON. Do not wrap in markdown except a standard ```json block. Do not write introductory or concluding conversational text.
- Never use placeholder texts like "no synonym", "N/A", "N/A - singular form", etc. If unavailable, return empty string "".
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    json_data = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional dictionary API generating strict bilingually-rich JSON outputs.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=json_data, timeout=timeout)

    # Detect rate-limiting specifically so callers can rotate keys
    if response.status_code == 429:
        try:
            from app.services.groq_provider import groq_pool
            groq_pool.mark_rate_limited(api_key)
        except ImportError:
            pass
        raise GroqRateLimitError(
            f"Groq rate limit (429) for key ...{api_key[-4:]}",
            key=api_key,
        )

    response.raise_for_status()
    payload = response.json()
    content_str = payload["choices"][0]["message"]["content"]
    parsed_json = json.loads(_extract_json_text(content_str))

    # Normalize fields from search prompt keys to system fields standard
    # e.g., 'meaning' -> 'definition', 'phonetic' -> 'pronunciation', 'sentence' -> 'example_sentence'
    result = {
        "word": str(parsed_json.get("word", word_clean)).strip(),
        "part_of_speech": str(parsed_json.get("part_of_speech") or "").strip() or None,
        "definition": str(parsed_json.get("meaning") or parsed_json.get("definition") or "").strip(),
        "bangla_meaning": str(parsed_json.get("bangla_meaning") or "").strip() or None,
        "pronunciation": str(parsed_json.get("phonetic") or parsed_json.get("pronunciation") or "").strip() or None,
        "example_sentence": str(parsed_json.get("sentence") or parsed_json.get("example_sentence") or "").strip() or None,
        "synonyms": str(parsed_json.get("synonym") or parsed_json.get("synonyms") or "").strip() or None,
        "antonyms": str(parsed_json.get("antonym") or parsed_json.get("antonyms") or "").strip() or None,
    }

    # If synonym or antonym contains placeholders, remove them
    for key in ("synonyms", "antonyms"):
        val = result[key]
        if val and (val.lower().strip() in PLACEHOLDER_PATTERNS or "not available" in val.lower() or val.strip() == "-"):
            result[key] = None

    return result

def validate_enrichment(word, payload):
    """
    Centralized validation logic.
    Verifies completeness, placeholders, pronunciation letters, sentence usage.
    """
    word_clean = str(word).strip().lower()
    errors = []

    definition = str(payload.get("definition") or "").strip()
    bangla_meaning = str(payload.get("bangla_meaning") or "").strip()
    pronunciation = str(payload.get("pronunciation") or "").strip()
    example_sentence = str(payload.get("example_sentence") or "").strip()
    synonyms = str(payload.get("synonyms") or "").strip()
    antonyms = str(payload.get("antonyms") or "").strip()

    # 1. Required fields exist and are non-empty
    if not definition:
        errors.append("missing_definition")
    if not bangla_meaning:
        errors.append("missing_bangla_meaning")
    if not pronunciation:
        errors.append("missing_pronunciation")
    if not example_sentence:
        errors.append("missing_example_sentence")

    # 2. No placeholder text
    def is_placeholder(val):
        cleaned = clean_text(val).lower()
        if not cleaned:
            return True
        return any(pat in cleaned for pat in PLACEHOLDER_PATTERNS) or "not available" in cleaned

    if definition and is_placeholder(definition):
        errors.append("placeholder_definition")
    if bangla_meaning and is_placeholder(bangla_meaning):
        errors.append("placeholder_bangla")
    if pronunciation and is_placeholder(pronunciation):
        errors.append("placeholder_pronunciation")
    if example_sentence and is_placeholder(example_sentence):
        errors.append("placeholder_example")

    # 3. Malformed Pronunciation
    if pronunciation and not is_placeholder(pronunciation):
        # Must not contain IPA markers, slashes, or brackets
        if re.search(r"[{}<>\\|/\[\]ˈˌː]", pronunciation):
            errors.append("malformed_pronunciation_ipa")
        # Must have letters
        letters = re.sub(r"[^A-Za-z]", "", pronunciation)
        if len(letters) < 3:
            errors.append("malformed_pronunciation_too_short")
        # For words/phrases with length > 4, should ideally contain hyphen syllable split
        if len(word_clean) > 4 and "-" not in pronunciation:
            errors.append("malformed_pronunciation_no_syllables")

    # 4. Explanation Quality
    if definition and not is_placeholder(definition):
        def_lower = definition.lower()
        if len(definition) < 10 or len(definition) > 180:
            errors.append("weak_definition_length")
        # Circular definition check: must not just define the word by itself
        if def_lower == word_clean or def_lower.startswith(f"{word_clean} is ") or def_lower.startswith(f"a simple meaning for {word_clean}"):
            errors.append("circular_definition")
        if re.search(r"\b(as an ai|lorem ipsum|undefined|null|cannot provide|i'm sorry)\b", def_lower):
            errors.append("hallucinated_definition")

    # 5. Sentence Quality
    if example_sentence and not is_placeholder(example_sentence):
        sent_lower = example_sentence.lower()
        if len(example_sentence) < 20:
            errors.append("weak_sentence_length")
        # Check if sentence actually uses the word
        # (Handling root words and standard bounds)
        word_found = False
        if " " in word_clean:
            word_found = word_clean in sent_lower
        else:
            word_found = bool(re.search(rf"\b{re.escape(word_clean)}\w*\b", sent_lower))
        if not word_found:
            errors.append("sentence_missing_word")

    # 6. Repetitive Garbage check
    for text_val in (definition, example_sentence):
        if text_val:
            tokens = text_val.lower().split()
            if len(tokens) > 5 and len(set(tokens)) / len(tokens) < 0.5:
                errors.append("repetitive_garbage")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def calculate_quality_score(word, payload):
    """
    Quality scoring system (0 to 100).
    Assesses completeness, naturalness, definition and sentence metrics, pronunciation formatting.
    """
    word_clean = str(word).strip().lower()
    score = 100

    definition = str(payload.get("definition") or "").strip()
    bangla_meaning = str(payload.get("bangla_meaning") or "").strip()
    pronunciation = str(payload.get("pronunciation") or "").strip()
    example_sentence = str(payload.get("example_sentence") or "").strip()
    synonyms = str(payload.get("synonyms") or "").strip()
    antonyms = str(payload.get("antonyms") or "").strip()

    # Penalties for structural or quality failures
    validation_results = validate_enrichment(word_clean, payload)
    errors = validation_results["errors"]

    penalties = {
        "missing_definition": 45,
        "missing_bangla_meaning": 30,
        "missing_pronunciation": 20,
        "missing_example_sentence": 20,
        "placeholder_definition": 35,
        "placeholder_bangla": 25,
        "placeholder_pronunciation": 25,
        "placeholder_example": 25,
        "malformed_pronunciation_ipa": 25,
        "malformed_pronunciation_too_short": 20,
        "malformed_pronunciation_no_syllables": 10,
        "weak_definition_length": 15,
        "circular_definition": 30,
        "hallucinated_definition": 60,
        "weak_sentence_length": 15,
        "sentence_missing_word": 25,
        "repetitive_garbage": 40,
    }

    for err in errors:
        score -= penalties.get(err, 10)

    # Extra penalties for poor synonym/antonym formatting
    if synonyms:
        if word_clean in {part.strip().lower() for part in re.split(r"[,;]", synonyms)}:
            score -= 10
    if antonyms:
        if word_clean in {part.strip().lower() for part in re.split(r"[,;]", antonyms)}:
            score -= 10

    # Ensure score bounds
    return max(0, min(100, score))
