import json
import os
import re

import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


FALLBACK_VOCABULARY = {
    "Beginner": [
        {
            "word": "convenient",
            "part_of_speech": "adjective",
            "meaning": "easy and useful for your situation",
            "bangla_meaning": "সুবিধাজনক",
            "sentence": "Online learning is convenient for many students.",
            "phonetic": "kun-VEEN-yunt",
            "bangla_pronunciation": "কনভিনিয়েন্ট",
            "memory_trick": "Convenient sounds like something you can use conveniently anytime.",
            "difficulty": "Beginner",
        },
        {
            "word": "effective",
            "part_of_speech": "adjective",
            "meaning": "working well and giving a good result",
            "bangla_meaning": "কার্যকর",
            "sentence": "Practice is an effective way to improve speaking.",
            "phonetic": "ih-FEK-tiv",
            "bangla_pronunciation": "ইফেক্টিভ",
            "memory_trick": "Effective creates a strong effect.",
            "difficulty": "Beginner",
        },
        {
            "word": "benefit",
            "part_of_speech": "noun",
            "meaning": "a helpful result or advantage",
            "bangla_meaning": "উপকার",
            "sentence": "There are many benefits to reading every day.",
            "phonetic": "BEN-uh-fit",
            "bangla_pronunciation": "বেনিফিট",
            "memory_trick": "Benefit sounds like getting something better.",
            "difficulty": "Beginner",
        },
        {
            "word": "improve",
            "part_of_speech": "verb",
            "meaning": "to make something better",
            "bangla_meaning": "উন্নত করা",
            "sentence": "Daily speaking practice can improve your confidence.",
            "phonetic": "im-PROOV",
            "bangla_pronunciation": "ইমপ্রুভ",
            "memory_trick": "Improve means move upward to better quality.",
            "difficulty": "Beginner",
        },
        {
            "word": "challenge",
            "part_of_speech": "noun",
            "meaning": "something difficult that tests you",
            "bangla_meaning": "চ্যালেঞ্জ",
            "sentence": "Finding time to study is a challenge for many people.",
            "phonetic": "CHAL-inj",
            "bangla_pronunciation": "চ্যালেঞ্জ",
            "memory_trick": "A challenge pushes you to change and grow.",
            "difficulty": "Beginner",
        },
        {
            "word": "prefer",
            "part_of_speech": "verb",
            "meaning": "to like one thing more than another",
            "bangla_meaning": "পছন্দ করা",
            "sentence": "Many students prefer videos to long textbooks.",
            "phonetic": "prih-FUR",
            "bangla_pronunciation": "প্রিফার",
            "memory_trick": "Prefer is what you put first.",
            "difficulty": "Beginner",
        },
        {
            "word": "practical",
            "part_of_speech": "adjective",
            "meaning": "useful in real situations",
            "bangla_meaning": "ব্যবহারিক",
            "sentence": "This course gives practical advice for job interviews.",
            "phonetic": "PRAK-ti-kul",
            "bangla_pronunciation": "প্র্যাকটিক্যাল",
            "memory_trick": "Practical is what you can practice in real life.",
            "difficulty": "Beginner",
        },
        {
            "word": "confident",
            "part_of_speech": "adjective",
            "meaning": "feeling sure about your ability",
            "bangla_meaning": "আত্মবিশ্বাসী",
            "sentence": "She sounded confident during the presentation.",
            "phonetic": "KON-fi-dunt",
            "bangla_pronunciation": "কনফিডেন্ট",
            "memory_trick": "A confident person trusts what is inside.",
            "difficulty": "Beginner",
        },
        {
            "word": "opportunity",
            "part_of_speech": "noun",
            "meaning": "a good chance to do something",
            "bangla_meaning": "সুযোগ",
            "sentence": "Studying abroad is a great opportunity for many learners.",
            "phonetic": "op-er-TOO-ni-tee",
            "bangla_pronunciation": "অপরচুনিটি",
            "memory_trick": "Opportunity opens a door of chance.",
            "difficulty": "Beginner",
        },
        {
            "word": "suitable",
            "part_of_speech": "adjective",
            "meaning": "right or appropriate for something",
            "bangla_meaning": "উপযুক্ত",
            "sentence": "This topic is suitable for an IELTS essay.",
            "phonetic": "SOO-tuh-bul",
            "bangla_pronunciation": "সুটেবল",
            "memory_trick": "Suitable is something that suits you.",
            "difficulty": "Beginner",
        },
    ],
    "Intermediate": [
        {
            "word": "significant",
            "part_of_speech": "adjective",
            "meaning": "important or noticeable",
            "bangla_meaning": "গুরুত্বপূর্ণ",
            "sentence": "Technology has had a significant impact on education.",
            "phonetic": "sig-NIF-ih-kunt",
            "bangla_pronunciation": "সিগনিফিক্যান্ট",
            "memory_trick": "Significant deserves a sign because it matters.",
            "difficulty": "Intermediate",
        },
        {
            "word": "maintain",
            "part_of_speech": "verb",
            "meaning": "to keep in a good condition",
            "bangla_meaning": "রক্ষা করা",
            "sentence": "It is hard to maintain a balance between work and study.",
            "phonetic": "main-TAIN",
            "bangla_pronunciation": "মেইনটেইন",
            "memory_trick": "Maintain means keep it the same and stable.",
            "difficulty": "Intermediate",
        },
        {
            "word": "approach",
            "part_of_speech": "noun",
            "meaning": "a way of dealing with something",
            "bangla_meaning": "পদ্ধতি",
            "sentence": "A balanced approach is often best in academic writing.",
            "phonetic": "uh-PROACH",
            "bangla_pronunciation": "অ্যাপ্রোচ",
            "memory_trick": "Approach is the path you move toward.",
            "difficulty": "Intermediate",
        },
        {
            "word": "impact",
            "part_of_speech": "noun",
            "meaning": "a strong effect on something",
            "bangla_meaning": "প্রভাব",
            "sentence": "Social media has a strong impact on daily communication.",
            "phonetic": "IM-pakt",
            "bangla_pronunciation": "ইমপ্যাক্ট",
            "memory_trick": "Impact is the effect after something hits.",
            "difficulty": "Intermediate",
        },
        {
            "word": "factor",
            "part_of_speech": "noun",
            "meaning": "one reason that influences a result",
            "bangla_meaning": "উপাদান",
            "sentence": "Cost is an important factor when choosing a university.",
            "phonetic": "FAK-tur",
            "bangla_pronunciation": "ফ্যাক্টর",
            "memory_trick": "A factor affects the final fact.",
            "difficulty": "Intermediate",
        },
        {
            "word": "achieve",
            "part_of_speech": "verb",
            "meaning": "to succeed in reaching a goal",
            "bangla_meaning": "অর্জন করা",
            "sentence": "Students can achieve better scores with regular practice.",
            "phonetic": "uh-CHEEV",
            "bangla_pronunciation": "অচিভ",
            "memory_trick": "Achieve sounds like reaching a chief goal.",
            "difficulty": "Intermediate",
        },
        {
            "word": "concern",
            "part_of_speech": "noun",
            "meaning": "a worry or important issue",
            "bangla_meaning": "উদ্বেগ বা বিষয়",
            "sentence": "Air pollution is a major concern in large cities.",
            "phonetic": "kun-SURN",
            "bangla_pronunciation": "কনসার্ন",
            "memory_trick": "Concern stays in your mind because you care.",
            "difficulty": "Intermediate",
        },
        {
            "word": "develop",
            "part_of_speech": "verb",
            "meaning": "to grow or improve over time",
            "bangla_meaning": "উন্নয়ন করা",
            "sentence": "Reading regularly helps learners develop new ideas.",
            "phonetic": "dih-VEL-up",
            "bangla_pronunciation": "ডেভেলপ",
            "memory_trick": "Develop means building something level by level.",
            "difficulty": "Intermediate",
        },
        {
            "word": "influence",
            "part_of_speech": "verb",
            "meaning": "to affect how someone thinks or acts",
            "bangla_meaning": "প্রভাবিত করা",
            "sentence": "Parents often influence a child's habits and behavior.",
            "phonetic": "IN-floo-uns",
            "bangla_pronunciation": "ইনফ্লুয়েন্স",
            "memory_trick": "Influence flows into another person's decision.",
            "difficulty": "Intermediate",
        },
        {
            "word": "solution",
            "part_of_speech": "noun",
            "meaning": "an answer to a problem",
            "bangla_meaning": "সমাধান",
            "sentence": "Public transport can be a solution to traffic congestion.",
            "phonetic": "suh-LOO-shun",
            "bangla_pronunciation": "সলিউশন",
            "memory_trick": "Solution solves the situation.",
            "difficulty": "Intermediate",
        },
    ],
    "Advanced": [
        {
            "word": "substantial",
            "part_of_speech": "adjective",
            "meaning": "large in amount or very important",
            "bangla_meaning": "উল্লেখযোগ্য",
            "sentence": "The government should make a substantial investment in education.",
            "phonetic": "sub-STAN-shul",
            "bangla_pronunciation": "সাবস্ট্যানশাল",
            "memory_trick": "Substantial means strong enough to have substance.",
            "difficulty": "Advanced",
        },
        {
            "word": "inevitable",
            "part_of_speech": "adjective",
            "meaning": "certain to happen and impossible to avoid",
            "bangla_meaning": "অনিবার্য",
            "sentence": "In a modern economy, technological change is inevitable.",
            "phonetic": "in-EV-ih-tuh-bul",
            "bangla_pronunciation": "ইনেভিটেবল",
            "memory_trick": "Inevitable means it never escapes happening.",
            "difficulty": "Advanced",
        },
        {
            "word": "analyze",
            "part_of_speech": "verb",
            "meaning": "to examine carefully and deeply",
            "bangla_meaning": "বিশ্লেষণ করা",
            "sentence": "Students should analyze both sides before writing an essay.",
            "phonetic": "AN-uh-lyze",
            "bangla_pronunciation": "অ্যানালাইজ",
            "memory_trick": "Analyze breaks ideas into smaller parts.",
            "difficulty": "Advanced",
        },
        {
            "word": "sustainable",
            "part_of_speech": "adjective",
            "meaning": "able to continue for a long time without damage",
            "bangla_meaning": "টেকসই",
            "sentence": "Cities need sustainable solutions to environmental problems.",
            "phonetic": "suh-STAY-nuh-bul",
            "bangla_pronunciation": "সাস্টেইনেবল",
            "memory_trick": "Sustainable means it can stay and continue.",
            "difficulty": "Advanced",
        },
        {
            "word": "perspective",
            "part_of_speech": "noun",
            "meaning": "a particular way of thinking about something",
            "bangla_meaning": "দৃষ্টিভঙ্গি",
            "sentence": "Travel can broaden a person's perspective on life.",
            "phonetic": "per-SPEK-tiv",
            "bangla_pronunciation": "পারস্পেকটিভ",
            "memory_trick": "Perspective is the way you see from your position.",
            "difficulty": "Advanced",
        },
        {
            "word": "compelling",
            "part_of_speech": "adjective",
            "meaning": "very convincing and strong",
            "bangla_meaning": "জোরালো ও বিশ্বাসযোগ্য",
            "sentence": "She gave a compelling reason for changing the policy.",
            "phonetic": "kum-PEL-ing",
            "bangla_pronunciation": "কমপেলিং",
            "memory_trick": "Compelling pulls attention because it is powerful.",
            "difficulty": "Advanced",
        },
        {
            "word": "allocate",
            "part_of_speech": "verb",
            "meaning": "to give something to a particular purpose",
            "bangla_meaning": "বরাদ্দ করা",
            "sentence": "The school should allocate more money to library resources.",
            "phonetic": "AL-uh-kate",
            "bangla_pronunciation": "অ্যালোকেট",
            "memory_trick": "Allocate means locate resources to a place.",
            "difficulty": "Advanced",
        },
        {
            "word": "controversial",
            "part_of_speech": "adjective",
            "meaning": "causing disagreement among people",
            "bangla_meaning": "বিতর্কিত",
            "sentence": "The proposal was controversial because opinions were divided.",
            "phonetic": "kon-truh-VUR-shul",
            "bangla_pronunciation": "কনট্রোভারশাল",
            "memory_trick": "Controversial creates conversation and controversy.",
            "difficulty": "Advanced",
        },
        {
            "word": "efficient",
            "part_of_speech": "adjective",
            "meaning": "working well without wasting time or energy",
            "bangla_meaning": "দক্ষ",
            "sentence": "Public transport should be more efficient in crowded cities.",
            "phonetic": "ih-FISH-unt",
            "bangla_pronunciation": "ইফিশিয়েন্ট",
            "memory_trick": "Efficient finishes work with less waste.",
            "difficulty": "Advanced",
        },
        {
            "word": "profound",
            "part_of_speech": "adjective",
            "meaning": "very deep or powerful",
            "bangla_meaning": "গভীর",
            "sentence": "Education can have a profound effect on a person's future.",
            "phonetic": "pruh-FOUND",
            "bangla_pronunciation": "প্রফাউন্ড",
            "memory_trick": "Profound sounds like going far down and deep.",
            "difficulty": "Advanced",
        },
    ],
}

FALLBACK_RELATIONS = {
    "achieve": {"synonym": "accomplish", "antonym": "fail"},
    "analyze": {"synonym": "examine", "antonym": "ignore"},
    "approach": {"synonym": "method", "antonym": "avoidance"},
    "benefit": {"synonym": "advantage", "antonym": "drawback"},
    "challenge": {"synonym": "difficulty", "antonym": "ease"},
    "compelling": {"synonym": "convincing", "antonym": "weak"},
    "concern": {"synonym": "worry", "antonym": "confidence"},
    "confident": {"synonym": "self-assured", "antonym": "uncertain"},
    "convenient": {"synonym": "handy", "antonym": "inconvenient"},
    "controversial": {"synonym": "disputed", "antonym": "accepted"},
    "develop": {"synonym": "improve", "antonym": "decline"},
    "effective": {"synonym": "successful", "antonym": "ineffective"},
    "efficient": {"synonym": "productive", "antonym": "wasteful"},
    "factor": {"synonym": "element", "antonym": "result"},
    "impact": {"synonym": "effect", "antonym": "insignificance"},
    "improve": {"synonym": "enhance", "antonym": "worsen"},
    "influence": {"synonym": "affect", "antonym": "deter"},
    "inevitable": {"synonym": "unavoidable", "antonym": "avoidable"},
    "maintain": {"synonym": "preserve", "antonym": "neglect"},
    "opportunity": {"synonym": "chance", "antonym": "limitation"},
    "perspective": {"synonym": "viewpoint", "antonym": "blindness"},
    "practical": {"synonym": "useful", "antonym": "impractical"},
    "prefer": {"synonym": "favor", "antonym": "reject"},
    "profound": {"synonym": "deep", "antonym": "superficial"},
    "significant": {"synonym": "important", "antonym": "minor"},
    "solution": {"synonym": "answer", "antonym": "problem"},
    "substantial": {"synonym": "considerable", "antonym": "minor"},
    "suitable": {"synonym": "appropriate", "antonym": "unsuitable"},
    "sustainable": {"synonym": "lasting", "antonym": "wasteful"},
    "unity": {"synonym": "harmony", "antonym": "division"},
}

CURATED_WORD_CONTENT = {
    "axis": {
        "part_of_speech": "noun",
        "meaning": "a real or imaginary straight line used as a point of reference or rotation",
        "bangla_meaning": "অক্ষ",
        "sentence": "The Earth rotates on its axis once every day.",
        "phonetic": "AK-sis",
        "synonym": "line",
        "antonym": None,
        "memory_trick": "Axis sounds like the central line an object asks to turn around.",
        "topic": "general",
    },
    "enumeration": {
        "part_of_speech": "noun",
        "meaning": "the act of listing items one by one",
        "bangla_meaning": "তালিকাভুক্ত করা বা একে একে উল্লেখ",
        "sentence": "The report included a clear enumeration of the main causes.",
        "phonetic": "ee-noo-muh-RAY-shun",
        "synonym": "listing",
        "antonym": None,
        "memory_trick": "Enumeration sounds like numbering each item in order.",
        "topic": "general",
    },
    "complex": {
        "part_of_speech": "adjective",
        "meaning": "made of many connected parts and often difficult to understand",
        "bangla_meaning": "জটিল",
        "sentence": "The machine is complex, so new users need time to understand it.",
        "phonetic": "KOM-pleks",
        "synonym": "complicated",
        "antonym": "simple",
        "memory_trick": "Complex sounds like many pieces packed together in one place.",
        "topic": "general",
    },
    "follow": {
        "part_of_speech": "verb",
        "meaning": "to go after someone or something, or to understand and accept an idea",
        "bangla_meaning": "অনুসরণ করা",
        "sentence": "Please follow the instructions carefully during the test.",
        "phonetic": "FOL-oh",
        "synonym": "obey",
        "antonym": "ignore",
        "memory_trick": "Follow means going after a path or idea step by step.",
        "topic": "general",
    },
    "power": {
        "part_of_speech": "noun",
        "meaning": "the ability to control, influence, or produce an effect",
        "bangla_meaning": "শক্তি বা ক্ষমতা",
        "sentence": "Education has the power to change a person's future.",
        "phonetic": "POW-er",
        "synonym": "strength",
        "antonym": "weakness",
        "memory_trick": "Power is the force that lets something happen strongly.",
        "topic": "general",
    },
    "radial": {
        "part_of_speech": "adjective",
        "meaning": "spreading outward from a center point like a radius",
        "bangla_meaning": "কেন্দ্র থেকে চারদিকে বিস্তৃত",
        "sentence": "The road map showed a radial pattern around the city center.",
        "phonetic": "RAY-dee-ul",
        "synonym": "radiating",
        "antonym": None,
        "memory_trick": "Radial comes from radius, so think of lines moving out from the middle.",
        "topic": "general",
    },
    "reject": {
        "part_of_speech": "verb",
        "meaning": "to refuse to accept, approve, or believe something",
        "bangla_meaning": "প্রত্যাখ্যান করা",
        "sentence": "The committee may reject the proposal if the evidence is weak.",
        "phonetic": "ri-JEKT",
        "synonym": "refuse",
        "antonym": "accept",
        "memory_trick": "Re-ject sounds like throwing something back instead of taking it.",
        "topic": "general",
    },
    "rejected": {
        "part_of_speech": "adjective",
        "meaning": "not accepted, approved, or allowed",
        "bangla_meaning": "প্রত্যাখ্যাত",
        "sentence": "The rejected application was returned with feedback for improvement.",
        "phonetic": "ri-JEK-tid",
        "synonym": "refused",
        "antonym": "accepted",
        "memory_trick": "Rejected is what remains after something is turned away.",
        "topic": "general",
    },
    "remuneration": {
        "part_of_speech": "noun",
        "meaning": "payment given for work or services",
        "bangla_meaning": "পারিশ্রমিক",
        "sentence": "The company offered fair remuneration for overtime work.",
        "phonetic": "ri-myoo-nuh-RAY-shun",
        "synonym": "payment",
        "antonym": None,
        "memory_trick": "Remuneration is the money you receive in return for work.",
        "topic": "general",
    },
    "run": {
        "part_of_speech": "verb",
        "meaning": "to move quickly on foot; as a noun, it can also mean a period of movement or operation",
        "bangla_meaning": "দৌড়ানো; দৌড়",
        "sentence": "She goes for a short run every morning before work.",
        "phonetic": "RUN",
        "synonym": "sprint",
        "antonym": "walk",
        "memory_trick": "Run is what you do when your feet move faster than walking.",
        "topic": "general",
    },
    "unique": {
        "part_of_speech": "adjective",
        "meaning": "being the only one of its kind",
        "bangla_meaning": "অনন্য",
        "sentence": "Each artist has a unique style of expression.",
        "phonetic": "yoo-NEEK",
        "synonym": "distinctive",
        "antonym": "common",
        "memory_trick": "Unique sounds like one special thing with no true copy.",
        "topic": "general",
    },
    "unity": {
        "part_of_speech": "noun",
        "meaning": "the state of being joined together or acting as one",
        "bangla_meaning": "ঐক্য",
        "sentence": "The team worked in unity to finish the project on time.",
        "phonetic": "YOO-ni-tee",
        "synonym": "harmony",
        "antonym": "division",
        "memory_trick": "Unity sounds like many people moving into one shared direction.",
        "topic": "general",
    },
}


def _extract_json_text(content):
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return content


def _fallback_word_content(word):
    relations = FALLBACK_RELATIONS.get(word, {})
    curated = CURATED_WORD_CONTENT.get(word, {})
    return {
        "word": word,
        "part_of_speech": curated.get("part_of_speech"),
        "meaning": curated.get("meaning") or f"A simple meaning for {word}.",
        "bangla_meaning": curated.get("bangla_meaning") or f"{word} এর সহজ বাংলা অর্থ",
        "sentence": curated.get("sentence") or f"I used the word {word} in a simple sentence.",
        "phonetic": curated.get("phonetic") or word,
        "synonym": curated.get("synonym") or relations.get("synonym"),
        "antonym": curated.get("antonym") or relations.get("antonym"),
        "memory_trick": curated.get("memory_trick") or f"Think of the sound of {word} and connect it with a daily example.",
        "topic": curated.get("topic") or "general",
    }


TOPIC_FILTER_STOPWORDS = {"a", "an", "and", "for", "from", "in", "of", "on", "or", "the", "to", "with"}


def _normalize_topic_text(value):
    return str(value or "").strip().lower()


def _topic_terms(value):
    return {
        token
        for token in re.findall(r"[a-z]+", _normalize_topic_text(value))
        if len(token) >= 3 and token not in TOPIC_FILTER_STOPWORDS
    }


def _is_topic_relevant(item, topic_hint):
    if not _normalize_topic_text(topic_hint):
        return True

    haystack = " ".join(
        str((item or {}).get(field_name) or "")
        for field_name in ("topic", "meaning", "sentence", "memory_trick")
    ).lower()
    topic_terms = _topic_terms(topic_hint)
    if not topic_terms:
        return True
    if _normalize_topic_text(topic_hint) in haystack:
        return True
    return bool(topic_terms.intersection(_topic_terms(haystack)))


def _fallback_vocabulary_words(difficulty, word_count, avoid_words=None, user_custom_prompt=""):
    avoid_words = avoid_words or set()
    selected = []
    for item in FALLBACK_VOCABULARY.get(difficulty, FALLBACK_VOCABULARY["Beginner"]):
        if item["word"] in avoid_words:
            continue
        fallback_item = dict(item)
        relations = FALLBACK_RELATIONS.get(fallback_item["word"], {})
        fallback_item["synonym"] = fallback_item.get("synonym") or relations.get("synonym")
        fallback_item["topic"] = fallback_item.get("topic") or "general"
        if not _is_topic_relevant(fallback_item, user_custom_prompt):
            continue
        selected.append(fallback_item)
        if len(selected) >= word_count:
            break
    return selected


def _request_vocabulary_words_from_groq(difficulty, word_count, user_custom_prompt="", avoid_words=None):
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    avoid_words = avoid_words or []
    avoid_words_list = ", ".join(avoid_words[:200]) if avoid_words else "None"
    normalized_topic = user_custom_prompt.strip().lower()

    if normalized_topic:
        prompt = f"""
You are a vocabulary generator for a learning app.

Task:
Generate {word_count} English vocabulary words STRICTLY related to the topic: '{normalized_topic}'.

Rules:
- Only include words that are clearly connected to the topic
- Include nouns, verbs, adjectives related to the topic
- Do NOT include unrelated or generic words
- Do NOT repeat words
- Output ONLY a clean list of topic-relevant vocabulary

Examples:
Topic: cows
-> cattle, dairy, pasture, livestock, grazing, herd, milking

Topic: countries
-> nation, border, capital, sovereignty, territory, diplomacy

Topic: IELTS
-> vocabulary, fluency, grammar, comprehension, essay, speaking

If the topic is broad, generate diverse relevant words.
If the topic is narrow, still generate the closest meaningful related words.

Do NOT include any of these words:
{avoid_words_list}

Return ONLY valid JSON in this format:
[
  {{
    "word": "example",
    "part_of_speech": "noun",
    "english_meaning": "short clear meaning",
    "bangla_meaning": "short Bangla meaning",
    "pronunciation": "simple pronunciation",
    "synonym": "related synonym",
    "example_sentence": "A short sentence using the word.",
    "memory_trick": "A short memory trick.",
    "topic": "{normalized_topic}"
  }}
]
"""
    else:
        prompt = f"""
You are a vocabulary generator for a learning app.

Task:
Generate {word_count} useful general English vocabulary words for a {difficulty} learner.

Rules:
- Use modern, practical vocabulary
- Do NOT repeat words
- Avoid overly rare, outdated, or technical words

Do NOT include any of these words:
{avoid_words_list}

Return ONLY valid JSON in this format:
[
  {{
    "word": "example",
    "part_of_speech": "noun",
    "english_meaning": "short clear meaning",
    "bangla_meaning": "short Bangla meaning",
    "pronunciation": "simple pronunciation",
    "synonym": "related synonym",
    "example_sentence": "A short sentence using the word.",
    "memory_trick": "A short memory trick.",
    "topic": "general"
  }}
]
"""

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate topic-focused JSON vocabulary flashcards.",
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return json.loads(_extract_json_text(content))


def generate_vocabulary_words(difficulty="Beginner", word_count=5, user_custom_prompt="", avoid_words=None):
    """Generate a flashcard set directly from the AI model."""
    difficulty = str(difficulty).strip().title()
    if difficulty not in {"Beginner", "Intermediate", "Advanced"}:
        difficulty = "Beginner"

    try:
        word_count = int(word_count)
    except (TypeError, ValueError):
        word_count = 5

    if word_count < 1:
        word_count = 5
    word_count = min(word_count, 15)

    topic = str(user_custom_prompt or "").strip().lower()
    print("Topic:", topic)

    avoid_words = {
        str(word).strip().lower()
        for word in (avoid_words or [])
        if str(word).strip()
    }

    def clean_items(items, fallback_topic, generation_source):
        cleaned_items = []
        seen_words = set(avoid_words)

        for item in items:
            if not isinstance(item, dict):
                continue

            word = str(item.get("word", "")).strip().lower()
            if not word or word in seen_words:
                continue

            seen_words.add(word)
            cleaned_items.append(
                {
                    "word": word,
                    "part_of_speech": str(item.get("part_of_speech", "")).strip() or None,
                    "meaning": str(item.get("english_meaning", item.get("meaning", ""))).strip() or f"A word related to {fallback_topic or 'general English'}.",
                    "bangla_meaning": str(item.get("bangla_meaning", "")).strip() or None,
                    "sentence": str(item.get("example_sentence", item.get("sentence", ""))).strip() or f"This lesson includes the word {word}.",
                    "phonetic": str(item.get("pronunciation", item.get("phonetic", ""))).strip() or word,
                    "synonym": str(item.get("synonym", "")).strip() or FALLBACK_RELATIONS.get(word, {}).get("synonym") or None,
                    "memory_trick": str(item.get("memory_trick", "")).strip() or None,
                    "difficulty": difficulty,
                    "topic": str(item.get("topic", "")).strip() or fallback_topic or "general",
                    "generation_source": generation_source,
                }
            )
        return cleaned_items

    try:
        items = _request_vocabulary_words_from_groq(
            difficulty,
            word_count,
            user_custom_prompt=topic,
            avoid_words=sorted(avoid_words),
        )
        cleaned_items = clean_items(items, fallback_topic=topic or "general", generation_source="topic")
        print("AI response:", [item["word"] for item in cleaned_items])
        if cleaned_items:
            return cleaned_items

        if topic:
            retry_items = _request_vocabulary_words_from_groq(
                difficulty,
                word_count,
                user_custom_prompt=f"Generate general English vocabulary related to '{topic}'",
                avoid_words=sorted(avoid_words),
            )
            cleaned_retry_items = clean_items(
                retry_items,
                fallback_topic=topic,
                generation_source="topic_retry",
            )
            print("AI response:", [item["word"] for item in cleaned_retry_items])
            if cleaned_retry_items:
                return cleaned_retry_items
    except (requests.RequestException, ValueError, KeyError, RuntimeError):
        pass

    fallback_items = _fallback_vocabulary_words(
        difficulty,
        word_count,
        avoid_words=avoid_words,
        user_custom_prompt="",
    )
    cleaned_fallback_items = clean_items(
        fallback_items,
        fallback_topic="general",
        generation_source="general_fallback",
    )
    print("AI response:", [item["word"] for item in cleaned_fallback_items])
    return cleaned_fallback_items


def _request_word_content_from_groq(word):
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    prompt = f"""
You are helping Bangla speaking students learn English vocabulary.

Word: {word}

Provide:
- The most common modern part of speech for this word
- Simple English meaning (very easy)
- Bangla meaning (simple Bangla)
- One simple English sentence (daily life example)
- Phonetic pronunciation in English letters (like: e-BAN-don)
- One simple synonym
- One simple antonym when possible
- A memory trick to remember the word easily

Return ONLY JSON:
{{
  \"word\": \"...\",
  \"part_of_speech\": \"...\",
  \"meaning\": \"...\",
  \"bangla_meaning\": \"...\",
  \"sentence\": \"...\",
  \"phonetic\": \"...\",
  \"synonym\": \"...\",
  \"antonym\": \"...\",
  \"memory_trick\": \"...\"
}}

Rules:
- Give the most common modern dictionary meaning.
- Keep the part of speech consistent with the meaning.
- Never use placeholder text like "a simple meaning for {word}".
- Never repeat the word itself as the definition.
- Keep the content accurate, concise, and natural.
"""

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate simple JSON vocabulary explanations.",
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return json.loads(_extract_json_text(content))


def generate_word_content(word):
    """Generate Bangla and study content for a specific word."""
    normalized_word = str(word).strip().lower()
    if not normalized_word:
        raise ValueError("word is required")
    curated = CURATED_WORD_CONTENT.get(normalized_word, {})

    try:
        content = _request_word_content_from_groq(normalized_word)
        return {
            "word": str(content.get("word", normalized_word)).strip().lower() or normalized_word,
            "part_of_speech": str(content.get("part_of_speech", "")).strip() or curated.get("part_of_speech") or None,
            "meaning": str(content.get("meaning", "")).strip() or curated.get("meaning") or f"A simple meaning for {normalized_word}.",
            "bangla_meaning": str(content.get("bangla_meaning", "")).strip() or curated.get("bangla_meaning") or None,
            "sentence": str(content.get("sentence", "")).strip() or curated.get("sentence") or f"I used the word {normalized_word} in a simple sentence.",
            "phonetic": str(content.get("phonetic", "")).strip() or curated.get("phonetic") or normalized_word,
            "synonym": str(content.get("synonym", "")).strip() or curated.get("synonym") or FALLBACK_RELATIONS.get(normalized_word, {}).get("synonym") or None,
            "antonym": str(content.get("antonym", "")).strip() or curated.get("antonym") or FALLBACK_RELATIONS.get(normalized_word, {}).get("antonym") or None,
            "memory_trick": str(content.get("memory_trick", "")).strip() or curated.get("memory_trick") or None,
            "topic": str(content.get("topic", "")).strip() or curated.get("topic") or "general",
        }
    except (requests.RequestException, ValueError, KeyError, RuntimeError):
        return _fallback_word_content(normalized_word)


def _request_dictionary_details_from_groq(word):
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    prompt = f"""
You are an English dictionary.

Provide accurate information for the word: '{word}'.

Return JSON ONLY:
{{
  "word": "exact word",
  "part_of_speech": "...",
  "meaning": "...",
  "sentence": "...",
  "synonyms": ["...", "..."],
  "difficulty": "easy/medium/hard"
}}

Rules:
- Word must EXACTLY match input (do not change it)
- If input is misspelled -> suggest correction separately
- Meaning must be clear and correct
- Sentence must use the SAME word (not a different word)
- No hallucinated or unrelated data
"""

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": "You return strict dictionary JSON and keep the target word exact.",
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return json.loads(_extract_json_text(content))


def generate_word_details(word):
    normalized_word = str(word).strip().lower()
    if not normalized_word:
        raise ValueError("word is required")

    content = _request_dictionary_details_from_groq(normalized_word)
    synonyms = content.get("synonyms")
    if not isinstance(synonyms, list):
        synonyms = []

    cleaned_synonyms = []
    seen = set()
    for item in synonyms:
        cleaned = str(item or "").strip().lower()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_synonyms.append(cleaned)

    difficulty = str(content.get("difficulty", "")).strip().lower()
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    correction = content.get("correction")
    correction_text = str(correction or "").strip().lower() or None

    return {
        "word": str(content.get("word", normalized_word)).strip().lower() or normalized_word,
        "part_of_speech": str(content.get("part_of_speech", "")).strip() or None,
        "meaning": str(content.get("meaning", "")).strip(),
        "sentence": str(content.get("sentence", "")).strip() or None,
        "synonyms": cleaned_synonyms,
        "difficulty": difficulty,
        "correction": correction_text,
    }


def suggest_word_corrections(word, max_suggestions=3):
    normalized_word = str(word).strip().lower()
    if not normalized_word:
        return []

    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        return []

    prompt = f"""
You are a dictionary-quality English spelling assistant.

Input: {normalized_word}

Task:
- If the input is already a valid English word, return an empty list.
- If the input is misspelled, return up to {max_suggestions} likely valid English corrections.
- Suggestions must be real English words only.
- Do not explain anything.
- Do not include the original misspelling unless it is a valid word.
- Prefer modern common words over rare or obscure ones.

Return ONLY valid JSON:
["word1", "word2", "word3"]
"""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "system",
                        "content": "You return compact JSON spelling suggestions.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        parsed = json.loads(_extract_json_text(content))
    except (requests.RequestException, ValueError, KeyError, RuntimeError):
        return []

    suggestions = []
    seen = set()
    for item in parsed if isinstance(parsed, list) else []:
        cleaned = str(item or "").strip().lower()
        if (
            not cleaned
            or cleaned == normalized_word
            or cleaned in seen
            or not cleaned.isalpha()
        ):
            continue
        seen.add(cleaned)
        suggestions.append(cleaned)
        if len(suggestions) >= max_suggestions:
            break
    return suggestions


def _request_quiz_question_support_from_groq(word, meaning, sentence, difficulty="", custom_instruction="", quiz_type="multiple_choice"):
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    prompt = f"""
You are an IELTS vocabulary coach and quiz designer.

Create better quiz support for this English vocabulary item.

Word: {word}
Meaning: {meaning}
Sentence: {sentence}
Difficulty: {difficulty or "General"}
Quiz type: {quiz_type}
Custom instruction: {custom_instruction or "General IELTS, speaking, and writing focus"}

Rules:
- Focus on useful IELTS, speaking, and writing vocabulary.
- Avoid very easy questions.
- Avoid very rare or outdated words.
- Use realistic, plausible wrong options.
- Keep the language natural and clean.
- Prefer medium to advanced vocabulary support.
- If quiz_type is fill_blank, the fill_blank_sentence must naturally include the exact target word before hiding it.
- Do not switch the target concept, topic, part of speech, or meaning.
- Do not return duplicate distractors.
- Keep question_prompt relevant to the exact word and meaning provided.

Return ONLY JSON:
{{
  "question_prompt": "...",
  "subtitle": "...",
  "distractors": ["...", "...", "..."],
  "fill_blank_sentence": "..."
}}
"""

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.4,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate compact JSON quiz support for vocabulary learning.",
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return json.loads(_extract_json_text(content))


def generate_quiz_question_support(word, meaning, sentence="", difficulty="", custom_instruction="", quiz_type="multiple_choice"):
    try:
        content = _request_quiz_question_support_from_groq(
            word=word,
            meaning=meaning,
            sentence=sentence,
            difficulty=difficulty,
            custom_instruction=custom_instruction,
            quiz_type=quiz_type,
        )
        distractors = [
            str(item).strip()
            for item in content.get("distractors", [])
            if str(item).strip()
        ]
        return {
            "question_prompt": str(content.get("question_prompt", "")).strip() or word,
            "subtitle": str(content.get("subtitle", "")).strip() or "Choose the best answer",
            "distractors": distractors[:3],
            "fill_blank_sentence": str(content.get("fill_blank_sentence", "")).strip() or sentence,
        }
    except (requests.RequestException, ValueError, KeyError, RuntimeError):
        return {
            "question_prompt": word,
            "subtitle": "Choose the correct meaning" if quiz_type == "multiple_choice" else "Type the missing word",
            "distractors": [],
            "fill_blank_sentence": sentence,
        }

def verify_answer_using_ai(prompt, exact_answer, user_answer):
    """Use AI to verify if the user's fill-in-the-blank answer is correct."""
    def normalize_token(value):
        return "".join(ch.lower() for ch in str(value).strip() if ch.isalnum())

    if not user_answer.strip():
        return False
    if normalize_token(user_answer) == normalize_token(exact_answer):
        return True
        
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        return False
        
    instruction = f"""Evaluate this fill-in-the-blank answer.
Sentence: {prompt}
Target exact word: {exact_answer}
User's submitted word: {user_answer}

Accept alternate answers if they fit the blank naturally, preserve the sentence meaning, and are grammatically correct.
Reject answers that are close in meaning but do not fit the grammar or tone of the sentence.
Return ONLY 'YES' or 'NO'."""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": "You are an English language evaluator."},
                    {"role": "user", "content": instruction},
                ],
            },
            timeout=15,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip().upper()
        return "YES" in content
    except Exception:
        return False
