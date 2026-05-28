import json
import os
import random
from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from app.models import QuizQuestionCache, SearchVocabulary, UserWordProgress, VocabularyEnrichment, VocabularyMaster, db
from app.services.vocabulary_platform import get_or_create_enrichment, normalize_level


QUIZ_TYPES = (
    ("multiple_choice", "MCQ"),
    ("meaning_match", "Meaning Match"),
    ("fill_blank", "Fill in the blank"),
    ("synonym_match", "Synonym Match"),
    ("reverse_meaning", "Reverse Meaning"),
    ("bangla_to_english", "Bangla to English"),
    ("english_to_bangla", "English to Bangla"),
)
WORD_SOURCES = (
    ("learned_words", "My Learned Words"),
    ("difficult_words", "Difficult / Review Words"),
    ("generated_words", "Generated Flashcard Words"),
    ("mixed_curriculum", "Mixed Curriculum"),
    ("search_vocabulary", "Search Vocabulary"),
    ("level_curriculum", "Level-Based Curriculum"),
)
LEVEL_OPTIONS = ("Mixed", "Intermediate", "Upper Intermediate", "Advanced")
QUESTION_COUNTS = (5, 10, 15, 20)


def _clean(value):
    return str(value or "").strip()


def _level_filter(query, level):
    if not level or str(level).lower() == "mixed":
        return query
    return query.filter(VocabularyMaster.level == normalize_level(level))


def _progress_vocab_query(user_id, level):
    return _level_filter(
        VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment))
        .join(UserWordProgress, UserWordProgress.vocabulary_id == VocabularyMaster.id)
        .filter(UserWordProgress.user_id == user_id),
        level,
    )


def _source_query(user_id, source, level):
    source = source or "mixed_curriculum"
    # unseen_vocabulary is retired (cache-first architecture requires approved enrichments)
    if source == "unseen_vocabulary":
        source = "mixed_curriculum"
    if source == "learned_words":
        return _progress_vocab_query(user_id, level).filter(UserWordProgress.is_learned.is_(True))
    if source == "difficult_words":
        return _progress_vocab_query(user_id, level).filter(UserWordProgress.is_difficult.is_(True))
    if source == "generated_words":
        return _progress_vocab_query(user_id, level).filter(UserWordProgress.is_generated.is_(True))
    if source == "level_curriculum":
        return _level_filter(VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)), level)
    return _level_filter(VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)), level)


def _search_vocabulary_rows(user_id, count):
    return (
        SearchVocabulary.query.filter_by(searched_by_user_id=user_id)
        .order_by(SearchVocabulary.created_at.desc(), SearchVocabulary.id.desc())
        .limit(count)
        .all()
    )


# ── Quizable Vocabulary Validation ──────────────────────────────────────────

def is_quizable(vocabulary, quiz_type="multiple_choice"):
    """Return True if this vocabulary entry can produce a valid quiz question
    WITHOUT requiring live AI generation.

    Criteria (cache-first, no live AI dependency):
    - Must have an enrichment row
    - enrichment.definition must be non-empty
    - For bangla quiz types, bangla_meaning must exist
    - For synonym_match, synonyms must exist
    """
    e = vocabulary.enrichment
    if e is None:
        return False
    definition = str(e.definition or "").strip()
    if not definition or len(definition) < 5:
        return False
    if quiz_type == "bangla_to_english" or quiz_type == "english_to_bangla":
        bangla = str(e.bangla_meaning or "").strip()
        return bool(bangla)
    if quiz_type == "synonym_match":
        synonym = str(e.synonyms or "").strip()
        return bool(synonym)
    return True


def count_quizable_vocabularies(user_id, quiz_type, level, word_source, specific_vocabulary_ids=None):
    """Count how many vocabulary entries are quizable for the given parameters.

    If Groq live generation is configured, we can generate questions on the fly
    for any vocabulary word, so we do not restrict counting to only pre-enriched words.
    """
    # Search vocabulary quizzes use their own pool — estimate from SearchVocabulary rows
    if word_source == "search_vocabulary" and not specific_vocabulary_ids:
        rows = SearchVocabulary.query.filter_by(searched_by_user_id=user_id).count()
        return min(rows, 20)  # conservative cap

    has_groq = bool(os.environ.get("GROQ_API_KEY_QUIZ") or os.environ.get("GROQ_API_KEY"))

    # For specific vocabulary IDs, check each one
    if specific_vocabulary_ids:
        vocabs = (
            VocabularyMaster.query
            .options(selectinload(VocabularyMaster.enrichment))
            .filter(VocabularyMaster.id.in_(specific_vocabulary_ids))
            .all()
        )
        # Permissive check: if Groq is configured, all are quizable
        if has_groq:
            return len(vocabs)
        return sum(1 for v in vocabs if is_quizable(v, quiz_type))

    # Base query for source
    base_q = _source_query(user_id, word_source, level)

    # If Groq is present, we can dynamically enrich/generate on the fly!
    if has_groq:
        try:
            return base_q.count()
        except Exception:
            return 0

    # Otherwise fallback to strict approved-enrichment filter
    if quiz_type in ("bangla_to_english", "english_to_bangla"):
        base_q = (
            base_q
            .join(VocabularyEnrichment, VocabularyEnrichment.vocabulary_id == VocabularyMaster.id)
            .filter(
                VocabularyEnrichment.definition != None,
                VocabularyEnrichment.bangla_meaning != None,
            )
        )
    elif quiz_type == "synonym_match":
        base_q = (
            base_q
            .join(VocabularyEnrichment, VocabularyEnrichment.vocabulary_id == VocabularyMaster.id)
            .filter(
                VocabularyEnrichment.definition != None,
                VocabularyEnrichment.synonyms != None,
            )
        )
    else:
        base_q = (
            base_q
            .join(VocabularyEnrichment, VocabularyEnrichment.vocabulary_id == VocabularyMaster.id)
            .filter(VocabularyEnrichment.definition != None)
        )

    try:
        return base_q.count()
    except Exception:
        return 0


def _meaning(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.definition if enrichment else "")


def _bangla(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.bangla_meaning if enrichment else "")


def _sentence(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.example_sentence if enrichment else "")


def _synonym(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.synonyms if enrichment else "")


def _antonym(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.antonyms if enrichment else "")


def _distractors(vocabulary, pool, getter, count=3, used_options=None):
    values = []
    target_val = _clean(getter(vocabulary)).lower()
    seen = {target_val, vocabulary.word.lower()}

    # Identify target level and part of speech
    target_level = vocabulary.level
    target_pos = None
    if vocabulary.enrichment and vocabulary.enrichment.part_of_speech:
        target_pos = vocabulary.enrichment.part_of_speech.strip().lower()

    scored_candidates = []
    for item in pool:
        if item.id == vocabulary.id:
            continue
        if item.enrichment is None:
            # Skip if enrichment is missing; do NOT call get_or_create_enrichment to prevent write/flush triggers
            continue
        
        value = _clean(getter(item))
        if getter == _meaning and (not value or value.lower() in seen):
            value = f"A vocabulary meaning for {item.word}."
        
        if value and value.lower() not in seen:
            # Smart scoring
            score = 0
            
            # Level awareness
            if item.level == target_level:
                score += 10
            
            # Part of speech awareness
            item_pos = None
            if item.enrichment and item.enrichment.part_of_speech:
                item_pos = item.enrichment.part_of_speech.strip().lower()
            if target_pos and item_pos and target_pos == item_pos:
                score += 5
            
            # Repetition prevention penalty
            if used_options and value.lower() in used_options:
                score -= 20
                
            # Random jitter for variety
            score += random.uniform(0, 3)
            
            scored_candidates.append((score, value))

    # Sort candidates by score descending
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    for _, value in scored_candidates:
        if value.lower() not in seen:
            seen.add(value.lower())
            values.append(value)
            if used_options is not None:
                used_options.add(value.lower())
        if len(values) >= count:
            break

    # Fallback to simple pool loop if we couldn't get enough
    if len(values) < count:
        for item in pool:
            if item.id == vocabulary.id:
                continue
            if item.enrichment is None:
                continue
            value = _clean(getter(item))
            if getter == _meaning and (not value or value.lower() in seen):
                value = f"A vocabulary meaning for {item.word}."
            if value and value.lower() not in seen:
                seen.add(value.lower())
                values.append(value)
                if used_options is not None:
                    used_options.add(value.lower())
            if len(values) >= count:
                break

    return values


def _options(answer, distractors):
    choices = [answer] + distractors[:3]
    random.shuffle(choices)
    return choices


def _subtitle_for_type(quiz_type, is_english=True):
    if quiz_type == "fill_blank":
        return "Type the missing vocabulary word"
    if quiz_type == "reverse_meaning":
        return "Choose the word that matches this meaning"
    if quiz_type == "bangla_to_english":
        return "Choose the English word"
    if quiz_type == "english_to_bangla":
        return "Choose the Bangla meaning"
    if quiz_type == "synonym_match":
        return "Choose the closest synonym"
    return "Choose the correct meaning"


def _save_to_cache(vocabulary, quiz_type, question, custom_explanation=None):
    """Save successfully generated quiz question to DB cache safely if it is high quality."""
    e = vocabulary.enrichment
    distractors = []
    if question.get("question_type") == "multiple_choice":
        distractors = [opt for opt in question.get("options", []) if opt != question.get("answer")]
        if len(distractors) < 1 or len(set(distractors)) != len(distractors):
            return

    try:
        # Create a new cache entry
        cache_entry = QuizQuestionCache(
            vocabulary_id=vocabulary.id,
            quiz_type=quiz_type,
            question_text=question["prompt"],
            correct_answer=question["answer"],
            distractor_options=json.dumps(distractors),
            explanation=custom_explanation or _meaning(vocabulary) or "Definition is being prepared.",
            difficulty=vocabulary.level,
            generation_quality_score=getattr(e, "enrichment_quality_score", 1.0) if e else 1.0,
            validation_status="valid"
        )
        db.session.add(cache_entry)
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        pass


def generate_groq_quiz_question(word, quiz_type, enrichment_data=None, level="Mixed"):
    """
    Generate high-quality quiz questions using Groq API.
    Rotates through the quiz key pool on 429, timeout, or temporary failure.
    """
    from app.services.groq_provider import groq_pool
    import requests
    
    quiz_keys = groq_pool._quiz_keys()
    if not quiz_keys:
        return None

    # Compile context from enrichment data if available
    context_str = ""
    if enrichment_data:
        context_str = f"""
Existing Dictionary Data for Reference:
- Part of Speech: {enrichment_data.get('part_of_speech', '')}
- English Meaning: {enrichment_data.get('definition', '')}
- Bangla Meaning: {enrichment_data.get('bangla_meaning', '')}
- Example Sentence: {enrichment_data.get('example_sentence', '')}
- Synonyms: {enrichment_data.get('synonyms', '')}
- Antonyms: {enrichment_data.get('antonyms', '')}
"""

    prompt = f"""You are an elite educational assessment editor designing quiz questions for students.
Target Word: "{word}"
Quiz Type: "{quiz_type}"
Difficulty level: {level}
{context_str}

Please generate a high-quality educational quiz question matching the Quiz Type.

QUIZ TYPE INSTRUCTIONS:
1. "multiple_choice" or "meaning_match":
   - prompt: The English word itself ("{word}").
   - answer: The correct dictionary meaning of the word.
   - distractors: 3 believable English definition distractors of the same part of speech. Avoid obviously silly options.
2. "fill_blank":
   - prompt: A realistic example sentence using "{word}" where the word itself is replaced by "____".
   - answer: "{word}" (the exact target word).
   - distractors: None needed (return empty list).
3. "synonym_match":
   - prompt: The English word itself ("{word}").
   - answer: A high-quality synonym.
   - distractors: 3 believable English word distractors of the same part of speech that are NOT synonyms.
4. "reverse_meaning":
   - prompt: The English dictionary meaning of "{word}".
   - answer: "{word}" (the exact target word).
   - distractors: 3 believable other English vocabulary words of the same level and part of speech.
5. "bangla_to_english":
   - prompt: The natural Bangla meaning/translation of "{word}".
   - answer: "{word}" (the exact target word).
   - distractors: 3 other believable English words.
6. "english_to_bangla":
   - prompt: The English word itself ("{word}").
   - answer: The natural Bangla meaning of the word.
   - distractors: 3 other believable Bangla meanings/definitions.

DISTRACTOR QUALITY RULES:
- Distractors must feel believable, test understanding, and avoid obvious wrong answers.
- Distractors must remain completely fair to prepared learners.
- They must be of the same grammatical part of speech and tone as the correct answer.

OUTPUT FORMAT:
Return ONLY a strict valid JSON object. Do not include any other markdown, text, or conversational prefix/suffix outside the JSON block.
{{
  "prompt": "The question prompt text",
  "answer": "The correct answer",
  "distractors": ["distractor 1", "distractor 2", "distractor 3"],
  "explanation": "A concise, educational explanation explaining why the correct answer is right and why distractors are wrong."
}}
"""

    tried_keys = set()
    model = groq_pool.model() or "llama-3.3-70b-versatile"
    
    # Try up to the length of the configured keys to avoid infinite loop
    for _ in range(len(quiz_keys)):
        api_key = None
        with groq_pool._lock:
            # Pick the first untried non-cooling key
            for key in quiz_keys:
                if key not in tried_keys and not groq_pool._is_cooling(key):
                    api_key = key
                    break
            # Fallback to any untried key as a last resort
            if not api_key:
                for key in quiz_keys:
                    if key not in tried_keys:
                        api_key = key
                        break
                        
        if not api_key:
            break
            
        tried_keys.add(api_key)
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "temperature": 0.4,
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional educational assessment editor returning strict valid JSON objects."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                timeout=12
            )
            
            if response.status_code == 429:
                groq_pool.mark_rate_limited(api_key)
                continue
                
            response.raise_for_status()
            payload = response.json()
            if "choices" not in payload or not payload["choices"]:
                continue
                
            content_str = payload["choices"][0]["message"]["content"].strip()
            # Clean content_str of code block syntax if any
            if content_str.startswith("```"):
                lines = content_str.splitlines()
                if len(lines) >= 3:
                    start_idx = 1
                    if lines[0].strip().lower().startswith("```json"):
                        start_idx = 1
                    content_str = "\n".join(lines[start_idx:-1]).strip()
                    
            parsed = json.loads(content_str)
            if "prompt" in parsed and "answer" in parsed:
                return {
                    "prompt": str(parsed.get("prompt", "")).strip(),
                    "answer": str(parsed.get("answer", "")).strip(),
                    "distractors": [str(d).strip() for d in parsed.get("distractors", []) if str(d).strip()][:3],
                    "explanation": str(parsed.get("explanation", "")).strip()
                }
        except Exception:
            # Temporary failure or timeout
            groq_pool.mark_rate_limited(api_key, cooldown_seconds=120.0)
            
    return None


def collect_quiz_vocabularies(user_id, count, level, word_source, specific_vocabulary_ids=None, exclude_vocabulary_ids=None):
    """Step 1: Collect exactly count random vocabulary entries, prioritizing enriched entries first."""
    exclude_ids = set(exclude_vocabulary_ids or [])
    
    if specific_vocabulary_ids:
        base_q = VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)).filter(VocabularyMaster.id.in_(specific_vocabulary_ids))
    else:
        base_q = _source_query(user_id, word_source, level)
        
    if exclude_ids:
        base_q = base_q.filter(~VocabularyMaster.id.in_(exclude_ids))

    # Query 1: Enriched entries first
    enriched_q = (
        base_q
        .join(VocabularyEnrichment, VocabularyEnrichment.vocabulary_id == VocabularyMaster.id)
        .filter(VocabularyEnrichment.definition != None, func.length(VocabularyEnrichment.definition) >= 5)
    )
    
    # Order randomly
    enriched_q = enriched_q.order_by(func.random())
    
    try:
        enriched_entries = enriched_q.limit(count).all()
    except Exception:
        db.session.rollback()
        enriched_entries = []

    collected = list(enriched_entries)
    
    # Query 2: Fallback to non-enriched entries
    if len(collected) < count:
        needed = count - len(collected)
        already_chosen = exclude_ids.union({v.id for v in collected})
        
        fallback_q = base_q
        if already_chosen:
            fallback_q = fallback_q.filter(~VocabularyMaster.id.in_(already_chosen))
            
        fallback_q = fallback_q.order_by(func.random())
        try:
            fallback_entries = fallback_q.limit(needed).all()
        except Exception:
            db.session.rollback()
            fallback_entries = []
            
        collected.extend(fallback_entries)
        
    return collected[:count]


def _question_for(vocabulary, quiz_type, pool, used_options=None):
    quiz_type = quiz_type or "multiple_choice"

    # PRIORITY 1: Try cache first
    try:
        cached = QuizQuestionCache.query.filter_by(vocabulary_id=vocabulary.id, quiz_type=quiz_type).first()
        if cached:
            distractors = json.loads(cached.distractor_options or "[]")
            options = []
            if quiz_type != "fill_blank":
                options = _options(cached.correct_answer, distractors)
            return {
                "question_type": cached.quiz_type,
                "subtitle": _subtitle_for_type(cached.quiz_type, cached.correct_answer == vocabulary.word),
                "prompt": cached.question_text,
                "answer": cached.correct_answer,
                "options": options,
            }
    except Exception:
        db.session.rollback()

    # Helper function for local deterministic generation (Priority 2 & fallback)
    def generate_local_deterministic():
        answer_word = vocabulary.word
        meaning = _meaning(vocabulary) or f"The definition of the vocabulary word '{answer_word}'."
        bangla = _bangla(vocabulary)
        sentence = _sentence(vocabulary)
        synonym = _synonym(vocabulary)

        if quiz_type == "fill_blank":
            prompt_sentence = sentence or f"The word {answer_word} belongs in this sentence."
            prompt = prompt_sentence.replace(answer_word, "____", 1)
            if prompt == prompt_sentence:
                prompt = f"Fill in the blank: ____ means {meaning}"
            return {
                "question_type": "fill_blank",
                "subtitle": "Type the missing vocabulary word",
                "prompt": prompt,
                "answer": answer_word,
                "options": [],
            }
        elif quiz_type == "reverse_meaning":
            return {
                "question_type": "multiple_choice",
                "subtitle": "Choose the word that matches this meaning",
                "prompt": meaning,
                "answer": answer_word,
                "options": _options(answer_word, _distractors(vocabulary, pool, lambda item: item.word, used_options=used_options)),
            }
        elif quiz_type == "bangla_to_english" and bangla:
            return {
                "question_type": "multiple_choice",
                "subtitle": "Choose the English word",
                "prompt": bangla,
                "answer": answer_word,
                "options": _options(answer_word, _distractors(vocabulary, pool, lambda item: item.word, used_options=used_options)),
            }
        elif quiz_type == "english_to_bangla" and bangla:
            return {
                "question_type": "multiple_choice",
                "subtitle": "Choose the Bangla meaning",
                "prompt": answer_word,
                "answer": bangla,
                "options": _options(bangla, _distractors(vocabulary, pool, _bangla, used_options=used_options)),
            }
        elif quiz_type == "synonym_match" and synonym:
            return {
                "question_type": "multiple_choice",
                "subtitle": "Choose the closest synonym",
                "prompt": answer_word,
                "answer": synonym,
                "options": _options(synonym, _distractors(vocabulary, pool, _synonym, used_options=used_options)),
            }
        
        # Default meaning_match fallback
        return {
            "question_type": "multiple_choice",
            "subtitle": "Choose the correct meaning",
            "prompt": answer_word,
            "answer": meaning,
            "options": _options(meaning, _distractors(vocabulary, pool, _meaning, used_options=used_options)),
        }

    # PRIORITY 2: Local deterministic generation from enrichment if available
    if is_quizable(vocabulary, quiz_type):
        local_q = generate_local_deterministic()
        if local_q:
            _save_to_cache(vocabulary, quiz_type, local_q)
            return local_q

    # PRIORITY 3: Groq live generation
    enrichment_data = None
    if vocabulary.enrichment:
        enrichment_data = {
            "part_of_speech": vocabulary.enrichment.part_of_speech,
            "definition": vocabulary.enrichment.definition,
            "bangla_meaning": vocabulary.enrichment.bangla_meaning,
            "example_sentence": vocabulary.enrichment.example_sentence,
            "synonyms": vocabulary.enrichment.synonyms,
            "antonyms": vocabulary.enrichment.antonyms,
        }
    
    groq_res = generate_groq_quiz_question(vocabulary.word, quiz_type, enrichment_data=enrichment_data, level=vocabulary.level)
    if groq_res:
        try:
            q = {
                "question_type": "fill_blank" if quiz_type == "fill_blank" else "multiple_choice",
                "subtitle": _subtitle_for_type(quiz_type, groq_res["answer"] == vocabulary.word),
                "prompt": groq_res["prompt"],
                "answer": groq_res["answer"],
                "options": [] if quiz_type == "fill_blank" else _options(groq_res["answer"], groq_res["distractors"]),
            }
            _save_to_cache(vocabulary, quiz_type, q, custom_explanation=groq_res.get("explanation"))
            return q
        except Exception:
            pass

    # PRIORITY 4: Fallback to local deterministic (even if not strictly quizable, to avoid crash if possible)
    if vocabulary.enrichment:
        return generate_local_deterministic()

    # If no enrichment at all and Groq failed, return None
    return None


def build_curriculum_quiz_questions(
    user_id,
    total_questions=5,
    quiz_type="multiple_choice",
    level="Mixed",
    word_source="mixed_curriculum",
    focus="",
    exclude_vocabulary_ids=None,
    specific_vocabulary_ids=None,
):
    with db.session.no_autoflush:
        exclude_vocabulary_ids = set(exclude_vocabulary_ids or [])
        total_questions = total_questions if total_questions in QUESTION_COUNTS else 5
        
        # Search Vocabulary source
        if word_source == "search_vocabulary" and not specific_vocabulary_ids:
            rows = _search_vocabulary_rows(user_id, max(total_questions * 2, 12))
            questions = []
            for row in rows:
                meaning = _clean(row.definition) or "Definition is being prepared."
                bangla = _clean(row.bangla_meaning)
                answer_word = row.word
                if quiz_type == "fill_blank":
                    prompt = (_clean(row.example_sentence) or f"____ means {meaning}").replace(answer_word, "____", 1)
                    question = {"question_type": "fill_blank", "subtitle": "Type the searched word", "prompt": prompt, "answer": answer_word, "options": []}
                elif quiz_type == "bangla_to_english" and bangla:
                    question = {"question_type": "multiple_choice", "subtitle": "Choose the English word", "prompt": bangla, "answer": answer_word, "options": _options(answer_word, [item.word for item in rows if item.id != row.id])}
                elif quiz_type == "english_to_bangla" and bangla:
                    question = {"question_type": "multiple_choice", "subtitle": "Choose the Bangla meaning", "prompt": answer_word, "answer": bangla, "options": _options(bangla, [_clean(item.bangla_meaning) for item in rows if item.id != row.id and _clean(item.bangla_meaning)])}
                else:
                    question = {"question_type": "multiple_choice", "subtitle": "Choose the correct meaning", "prompt": answer_word, "answer": meaning, "options": _options(meaning, [_clean(item.definition) for item in rows if item.id != row.id and _clean(item.definition)])}
                question.update({"vocabulary_id": None, "user_word_id": None, "word": answer_word, "explanation": meaning})
                if question["question_type"] == "fill_blank" or len(question["options"]) >= 2:
                    questions.append(question)
                if len(questions) >= total_questions:
                    break
            return questions
            
        # Collect vocabularies using prioritized logic
        vocabularies = collect_quiz_vocabularies(
            user_id=user_id,
            count=total_questions,
            level=level,
            word_source=word_source,
            specific_vocabulary_ids=specific_vocabulary_ids,
            exclude_vocabulary_ids=exclude_vocabulary_ids
        )
        
        if not vocabularies and word_source != "mixed_curriculum":
            vocabularies = collect_quiz_vocabularies(
                user_id=user_id,
                count=total_questions,
                level=level,
                word_source="mixed_curriculum",
                exclude_vocabulary_ids=exclude_vocabulary_ids
            )

        pool = _source_query(user_id, "mixed_curriculum", "Mixed").order_by(func.random()).limit(150).all()
        questions = []
        used_options = set()
        for vocabulary in vocabularies:
            question = _question_for(vocabulary, quiz_type, pool, used_options=used_options)
            if not question:
                continue
            if question.get("question_type") != "fill_blank" and len(question.get("options", [])) < 2:
                continue
            progress = UserWordProgress.query.filter_by(user_id=user_id, vocabulary_id=vocabulary.id).first()
            question.update(
                {
                    "vocabulary_id": vocabulary.id,
                    "user_word_id": progress.id if progress else None,
                    "word": vocabulary.word,
                    "explanation": _meaning(vocabulary),
                }
            )
            questions.append(question)
        return questions


def quiz_started_at():
    return int(datetime.utcnow().timestamp())


def generate_question_for_item(item_id, is_search, quiz_type, user_id):
    if is_search:
        row = SearchVocabulary.query.get(item_id)
        if not row:
            return None
        meaning = _clean(row.definition) or "Definition is being prepared."
        bangla = _clean(row.bangla_meaning)
        answer_word = row.word
        # Get distractor candidates from SearchVocabulary first, then VocabularyMaster
        other_rows = SearchVocabulary.query.filter(SearchVocabulary.searched_by_user_id == user_id, SearchVocabulary.id != item_id).limit(10).all()
        
        if quiz_type == "fill_blank":
            prompt = (_clean(row.example_sentence) or f"____ means {meaning}").replace(answer_word, "____", 1)
            question = {"question_type": "fill_blank", "subtitle": "Type the searched word", "prompt": prompt, "answer": answer_word, "options": []}
        elif quiz_type == "bangla_to_english" and bangla:
            distractors = [item.word for item in other_rows if item.word.lower() != answer_word.lower()][:3]
            while len(distractors) < 3:
                mv = VocabularyMaster.query.order_by(func.random()).first()
                if mv and mv.word.lower() not in [answer_word.lower()] + [d.lower() for d in distractors]:
                    distractors.append(mv.word)
            question = {"question_type": "multiple_choice", "subtitle": "Choose the English word", "prompt": bangla, "answer": answer_word, "options": _options(answer_word, distractors)}
        elif quiz_type == "english_to_bangla" and bangla:
            distractors = [_clean(item.bangla_meaning) for item in other_rows if _clean(item.bangla_meaning) and _clean(item.bangla_meaning).lower() != bangla.lower()][:3]
            while len(distractors) < 3:
                me = VocabularyEnrichment.query.filter(VocabularyEnrichment.bangla_meaning != None).order_by(func.random()).first()
                if me and _clean(me.bangla_meaning) and _clean(me.bangla_meaning).lower() not in [bangla.lower()] + [d.lower() for d in distractors]:
                    distractors.append(_clean(me.bangla_meaning))
            question = {"question_type": "multiple_choice", "subtitle": "Choose the Bangla meaning", "prompt": answer_word, "answer": bangla, "options": _options(bangla, distractors)}
        else:
            distractors = [_clean(item.definition) for item in other_rows if _clean(item.definition) and _clean(item.definition).lower() != meaning.lower()][:3]
            while len(distractors) < 3:
                me = VocabularyEnrichment.query.filter(VocabularyEnrichment.definition != None).order_by(func.random()).first()
                if me and _clean(me.definition) and _clean(me.definition).lower() not in [meaning.lower()] + [d.lower() for d in distractors]:
                    distractors.append(_clean(me.definition))
            question = {"question_type": "multiple_choice", "subtitle": "Choose the correct meaning", "prompt": answer_word, "answer": meaning, "options": _options(meaning, distractors)}
            
        question.update({"vocabulary_id": None, "user_word_id": None, "word": answer_word, "explanation": meaning})
        return question
    else:
        vocab = VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)).get(item_id)
        if not vocab:
            return None
        pool = _source_query(user_id, "mixed_curriculum", "Mixed").order_by(func.random()).limit(100).all()
        question = _question_for(vocab, quiz_type, pool)
        if not question:
            return None
        progress = UserWordProgress.query.filter_by(user_id=user_id, vocabulary_id=vocab.id).first()
        question.update({
            "vocabulary_id": vocab.id,
            "user_word_id": progress.id if progress else None,
            "word": vocab.word,
            "explanation": _meaning(vocab)
        })
        return question


