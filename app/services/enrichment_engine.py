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


def build_meaning_pairs(english_value, bangla_value, raw_pairs=None, limit=2):
    pairs = []

    def normalized_pair_text(value):
        return re.sub(r"\s+", " ", clean_text(value).lower()).strip(" .,:;-/")

    def meaning_terms(value):
        stopwords = {
            "a", "an", "and", "are", "as", "based", "by", "for", "from", "in",
            "is", "it", "of", "or", "something", "the", "to", "with", "without",
        }
        concept_aliases = {
            "conclude": "infer_conclude",
            "conclusion": "infer_conclude",
            "deduce": "infer_conclude",
            "educate": "infer_conclude",
            "educated": "infer_conclude",
            "guess": "infer_conclude",
            "infer": "infer_conclude",
            "reason": "evidence_reason",
            "reasoning": "evidence_reason",
            "evidence": "evidence_reason",
            "information": "evidence_reason",
            "given": "evidence_reason",
        }
        terms = set()
        for token in re.findall(r"[a-z]+", normalized_pair_text(value)):
            if len(token) <= 2 or token in stopwords:
                continue
            stemmed = token
            for suffix in ("ing", "ed", "es", "s"):
                if stemmed.endswith(suffix) and len(stemmed) > len(suffix) + 3:
                    stemmed = stemmed[: -len(suffix)]
                    break
            terms.add(concept_aliases.get(token, concept_aliases.get(stemmed, stemmed)))
        return terms

    def is_redundant_text(existing, candidate):
        existing_key = normalized_pair_text(existing)
        candidate_key = normalized_pair_text(candidate)
        if not existing_key or not candidate_key:
            return False
        if existing_key == candidate_key:
            return True
        if existing_key in candidate_key or candidate_key in existing_key:
            return True
        existing_terms = meaning_terms(existing_key)
        candidate_terms = meaning_terms(candidate_key)
        if not existing_terms or not candidate_terms:
            return False
        overlap = len(existing_terms.intersection(candidate_terms))
        shorter_size = max(1, min(len(existing_terms), len(candidate_terms)))
        if overlap / shorter_size >= 0.68:
            return True
        shared_concepts = existing_terms.intersection(candidate_terms)
        return "infer_conclude" in shared_concepts and "evidence_reason" in shared_concepts

    def better_pair(candidate, existing):
        candidate_score = len(meaning_terms(candidate["english"])) + (len(candidate["english"]) / 80)
        existing_score = len(meaning_terms(existing["english"])) + (len(existing["english"]) / 80)
        return candidate_score > existing_score

    def add_pair(english, bangla):
        english = clean_text(english)
        bangla = clean_text(bangla)
        if not english or not bangla:
            return
        candidate = {"english": english, "bangla": bangla}
        for existing in pairs:
            if (
                is_redundant_text(existing["english"], english)
                or is_redundant_text(existing["bangla"], bangla)
            ):
                if better_pair(candidate, existing):
                    existing.update(candidate)
                return
        pairs.append(candidate)

    if isinstance(raw_pairs, list):
        for item in raw_pairs:
            if not isinstance(item, dict):
                continue
            add_pair(item.get("english"), item.get("bangla"))
            if len(pairs) >= limit:
                return pairs

    separator_pattern = r"\s*(?:/|;)\s*|\n+|\s*\d+\.\s*"
    english_parts = [clean_text(part) for part in re.split(separator_pattern, clean_text(english_value)) if clean_text(part)]
    bangla_parts = [clean_text(part) for part in re.split(separator_pattern, clean_text(bangla_value)) if clean_text(part)]
    for index, english in enumerate(english_parts[:limit]):
        bangla = bangla_parts[index] if index < len(bangla_parts) else ""
        add_pair(english, bangla)
    if not pairs and clean_text(english_value) and clean_text(bangla_value):
        add_pair(english_value, bangla_value)
    return pairs[:limit]

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
  "meaning_pairs": [
    {{"english": "...", "bangla": "..."}}
  ],
  "sentence": "...",
  "phonetic": "...",
  "synonym": "...",
  "antonym": "..."
}}

Rules for Fields:
- "word": You MUST keep the spelling of the word/phrase '{word_clean}' EXACTLY as received. Support common phrasal verbs and useful multi-word expressions. Do NOT normalize, singularize, pluralize, simplify, split, or rewrite it, UNLESS the entry is clearly misspelled or has minor typos. If it is correct, return '{word_clean}' exactly.
- "part_of_speech": The most common modern part of speech for this word or phrase, such as "phrasal verb" when appropriate.
- "meaning": One or two common learner-useful meanings only. Use concise, standard, dictionary-style English. Avoid obscure senses, circular definitions, and robotic placeholders. Length must be between 10 and 220 characters.
- "bangla_meaning": The corresponding Bangla meaning(s), context-aware and dictionary-like. Use standard understandable Bangla similar to modern learner dictionaries. Avoid overly literary, overly childish, robotic, or literal translations.
- "meaning_pairs": An array of one or two objects. Each object must pair one English meaning with its matching Bangla meaning. Most common meaning first. Do not include empty or unrelated pairs.
- Only include a second meaning_pair if it is a clearly distinct common meaning, not a rewording or duplicate of the first. If there is only one valid meaning, return exactly one pair.
- "sentence": One realistic, familiar, grammatically correct English example sentence using '{word_clean}'. It MUST contain the exact word/phrase '{word_clean}' in context. Prefer natural spoken/written English and avoid unnecessarily complex textbook phrasing. Length must be >= 20 characters.
- "phonetic": Readable English pronunciation spelled phonetically, hyphenated by syllables. Do NOT use IPA symbols like /, [, ], ˈ, ˌ, ː, or non-English letters. Keep it clean and readable for non-native speakers (e.g., for "convenient" return "kun-VEEN-yunt").
- "synonym": One or two relevant synonyms as a comma-separated string, or an empty string if not available. Do not include placeholder text.
- "antonym": One relevant antonym, or an empty string if not available. Do not include placeholder text.

Strict Output Rules:
- Return ONLY JSON. Do not wrap in markdown except a standard ```json block. Do not write introductory or concluding conversational text.
- Never use placeholder texts like "no synonym", "N/A", "N/A - singular form", etc. If unavailable, return empty string "".
- If '{word_clean}' is nonsense, random keyboard spam, or a meaningless combination, return fields that clearly indicate invalid content rather than inventing a fake meaning.
- Maximum two meanings. Do not list rare, academic, or highly specialized senses unless they are the main common use.
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
    meaning_pairs = build_meaning_pairs(
        result["definition"],
        result["bangla_meaning"],
        raw_pairs=parsed_json.get("meaning_pairs"),
    )
    if meaning_pairs:
        result["meaning_pairs"] = meaning_pairs
        result["definition"] = "\n".join(pair["english"] for pair in meaning_pairs)
        result["bangla_meaning"] = "\n".join(pair["bangla"] for pair in meaning_pairs)

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
        if len(definition) < 10 or len(definition) > 220:
            errors.append("weak_definition_length")
        # Circular definition check: must not just define the word by itself
        if def_lower == word_clean or def_lower.startswith(f"{word_clean} is ") or def_lower.startswith(f"a simple meaning for {word_clean}"):
            errors.append("circular_definition")
        if re.search(r"\b(as an ai|lorem ipsum|undefined|null|cannot provide|i'm sorry)\b", def_lower):
            errors.append("hallucinated_definition")
        if len(re.split(r"\s*(?:/|;|\n|\d+\.)\s*", definition)) > 2:
            errors.append("too_many_meanings")
        if re.search(r"\b(extremely|highly specialized|technical term in|rarely used)\b", def_lower):
            errors.append("obscure_definition")

    # 5. Sentence Quality
    if example_sentence and not is_placeholder(example_sentence):
        sent_lower = example_sentence.lower()
        if len(example_sentence) < 20:
            errors.append("weak_sentence_length")
        if len(example_sentence.split()) > 24:
            errors.append("awkward_sentence")
        if re.search(r"\b(administrative|theoretical|procedures|authority|phenomenon|initiated)\b", sent_lower):
            errors.append("awkward_sentence")
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

    if bangla_meaning and not is_placeholder(bangla_meaning):
        bangla_lower = bangla_meaning.lower()
        if re.search(r"\b(translation|meaning|n/a|null)\b", bangla_lower):
            errors.append("robotic_bangla")
        if len(bangla_meaning) > 240:
            errors.append("overlong_bangla")

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
        "too_many_meanings": 20,
        "obscure_definition": 15,
        "awkward_sentence": 15,
        "robotic_bangla": 20,
        "overlong_bangla": 10,
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
