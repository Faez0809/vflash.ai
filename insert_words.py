import os

WORDS_HTML = """{% extends "base.html" %}

{% block title %}My Words | vflash.ai{% endblock %}

{% block content %}
<!-- TAILWIND INTEGRATION FOR THIS PAGE -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Inter:wght@300;400;500;600;700&family=Hind+Siliguri:wght@400;600&display=swap" rel="stylesheet"/>
<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 20;
    }
    .no-scrollbar::-webkit-scrollbar {
        display: none;
    }
    details > summary {
        list-style: none;
    }
    details > summary::-webkit-details-marker {
        display: none;
    }
    .word-row:hover {
        background-color: rgba(255, 255, 255, 0.03);
    }
    details[open] .word-row {
        background-color: rgba(255, 255, 255, 0.05);
        border-bottom-color: transparent;
    }
    .font-bengali {
        font-family: 'Hind Siliguri', sans-serif;
    }
    
    /* Safely override old global input styles for this tailwind container */
    .tw-scope input, .tw-scope select, .tw-scope textarea {
        color: #e2e2e2 !important;
        background-color: transparent;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .tw-scope input[type="search"] { padding-left: 2.5rem; }
</style>
<script id="tailwind-config">
    tailwind.config = {
      corePlugins: {
        preflight: false,
      },
      darkMode: "class",
      theme: {
        extend: {
          "colors": {
            "surface-container-lowest": "#0d0f0f",
            "surface-container-low": "#1a1c1c",
            "outline": "#8a9291",
            "outline-variant": "#404848",
            "on-surface": "#e2e2e2",
            "on-surface-variant": "#c0c8c7",
            "primary": "#9dd0cd",
            "on-primary": "#003735",
            "primary-container": "#2d5f5d",
            "secondary": "#dec38f",
            "error": "#ffb4ab",
            "error-container": "#93000a",
          },
          "fontFamily": {
            "headline": ["Manrope"],
            "body": ["Inter"]
          }
        }
      }
    }
</script>

<div class="tw-scope px-6 max-w-screen-2xl mx-auto font-body antialiased" style="margin-top: 1rem;">
    <!-- Filter Section -->
    <section class="mb-8 space-y-4">
        <form method="get" class="flex flex-col gap-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="relative group">
                    <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-sm" data-icon="search">search</span>
                    <input name="q" value="{{ search_query }}" class="w-full bg-surface-container-lowest border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg pl-10 text-sm h-11 text-on-surface placeholder:text-on-surface-variant/40 outline-none" placeholder="Search my words..." type="search"/>
                </div>
                <select name="difficulty" class="bg-surface-container-lowest border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg text-sm h-11 text-on-surface-variant px-4 outline-none">
                    <option value="All" {{ 'selected' if difficulty_filter == 'All' else '' }}>Difficulty: All</option>
                    {% for difficulty in available_difficulties %}
                        <option value="{{ difficulty }}" {{ 'selected' if difficulty_filter == difficulty else '' }}>{{ difficulty }}</option>
                    {% endfor %}
                </select>
                <select name="topic" class="bg-surface-container-lowest border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg text-sm h-11 text-on-surface-variant px-4 outline-none">
                    <option value="All" {{ 'selected' if topic_filter == 'All' else '' }}>Topic: All</option>
                    {% for topic in available_topics %}
                        <option value="{{ topic }}" {{ 'selected' if topic_filter == topic else '' }}>{{ topic }}</option>
                    {% endfor %}
                </select>
                <select name="learned" class="bg-surface-container-lowest border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg text-sm h-11 text-on-surface-variant px-4 outline-none">
                    <option value="all" {{ 'selected' if learned_filter == 'all' else '' }}>Learning State: All</option>
                    <option value="learned" {{ 'selected' if learned_filter == 'learned' else '' }}>Learned</option>
                    <option value="learning" {{ 'selected' if learned_filter == 'learning' else '' }}>Learning</option>
                </select>
            </div>
            
            <div class="flex flex-col md:flex-row items-center justify-end gap-6">
                <div class="flex items-center gap-4">
                    <label class="flex items-center gap-2 cursor-pointer group">
                        <input name="difficult" type="checkbox" value="1" {{ 'checked' if difficult_only else '' }} class="w-4 h-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary" style="accent-color: #9dd0cd;"/>
                        <span class="text-[0.7rem] uppercase font-bold tracking-widest text-on-surface-variant group-hover:text-primary transition-colors mt-[2px]">Difficult only</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer group">
                        <input name="favorite" type="checkbox" value="1" {{ 'checked' if favorite_only else '' }} class="w-4 h-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary" style="accent-color: #9dd0cd;"/>
                        <span class="text-[0.7rem] uppercase font-bold tracking-widest text-on-surface-variant group-hover:text-primary transition-colors mt-[2px]">Favorites only</span>
                    </label>
                </div>
                <div class="flex items-center gap-3">
                    <a href="{{ url_for('words') }}" class="text-[0.7rem] uppercase font-bold tracking-widest text-outline hover:text-on-surface transition-colors cursor-pointer">Clear</a>
                    <button type="submit" class="bg-primary text-on-primary px-6 py-2 rounded font-bold text-[0.7rem] uppercase tracking-widest hover:brightness-110 active:scale-95 duration-200" style="border: none;">Apply Filters</button>
                </div>
            </div>
        </form>
    </section>

    <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-on-surface font-headline tracking-tight">Your Vocabulary</h2>
        <span class="text-sm font-medium text-outline-variant">{{ user_words|length }} words match</span>
    </div>

    <!-- Word List: High-Density Interactive List -->
    {% if user_words %}
        <div class="bg-surface-container-lowest border border-white/[0.05] rounded-xl overflow-hidden mb-8">
            <!-- Header Row -->
            <div class="hidden md:grid grid-cols-[160px_100px_160px_1fr_100px_90px] gap-6 px-6 py-3 bg-white/[0.02] border-b border-white/[0.05] text-[0.65rem] font-bold uppercase tracking-widest text-outline">
                <div>Word</div>
                <div class="text-left">Type</div>
                <div>Bangla Meaning</div>
                <div>Definition</div>
                <div class="text-center">Status</div>
                <div class="text-right">Actions</div>
            </div>

            {% for item in user_words %}
                <details class="group border-b border-white/[0.05] last:border-b-0" {% if loop.index == 1 %}open{% endif %}>
                    <summary class="word-row grid grid-cols-[1fr_80px_90px] md:grid-cols-[160px_100px_160px_1fr_100px_90px] items-center gap-4 md:gap-6 px-6 py-4 cursor-pointer transition-colors outline-none">
                        <div class="flex flex-col md:block min-w-0">
                            <h3 class="text-base font-headline font-bold text-primary tracking-tight truncate">{{ item.word_entry.word }}</h3>
                            <span class="md:hidden text-[0.65rem] font-medium text-on-surface-variant/60 truncate">{{ item.word_entry.bangla_meaning or 'No translation' }}</span>
                        </div>
                        
                        <div class="hidden md:flex items-center">
                            <span class="text-[0.65rem] font-bold text-secondary uppercase tracking-tighter opacity-80">{{ item.word_entry.part_of_speech or 'Word' }}</span>
                        </div>
                        
                        <div class="hidden md:block font-bengali text-[0.95rem] font-semibold text-on-surface truncate">{{ item.word_entry.bangla_meaning or '--' }}</div>
                        
                        <div class="hidden md:block text-[0.8rem] text-on-surface-variant/70 truncate pr-4">{{ item.word_entry.meaning }}</div>
                        
                        <div class="flex justify-center">
                            {% if item.learned %}
                                <span class="bg-primary-container/20 text-primary text-[0.6rem] px-2 py-0.5 rounded-full font-bold uppercase tracking-widest border border-primary/20">Mastered</span>
                            {% else %}
                                <span class="bg-[#93000a]/20 text-[#ffb4ab] text-[0.6rem] px-2 py-0.5 rounded-full font-bold uppercase tracking-widest border border-[#ffb4ab]/20">Learning</span>
                            {% endif %}
                        </div>
                        
                        <div class="flex justify-end items-center gap-3">
                            <form method="post" action="{{ url_for('toggle_favorite_flag', user_word_id=item.id) }}">
                                <input type="hidden" name="next" value="{{ request.full_path }}">
                                <button type="submit" class="{{ 'text-secondary' if item.is_favorite else 'text-outline-variant hover:text-secondary' }} transition-colors" title="Favorite" onclick="event.stopPropagation();">
                                    <span class="material-symbols-outlined text-lg bg-transparent border-none p-0" data-icon="star" style="{{ 'font-variation-settings: \'FILL\' 1;' if item.is_favorite else '' }}">star</span>
                                </button>
                            </form>
                            <form method="post" action="{{ url_for('toggle_difficult_flag', user_word_id=item.id) }}">
                                <input type="hidden" name="next" value="{{ request.full_path }}">
                                <button type="submit" class="{{ 'text-primary' if item.is_difficult else 'text-outline-variant hover:text-primary' }} transition-colors" title="Difficult" onclick="event.stopPropagation();">
                                    <span class="material-symbols-outlined text-lg bg-transparent border-none p-0" data-icon="priority_high" style="{{ 'font-variation-settings: \'FILL\' 1;' if item.is_difficult else '' }}">priority_high</span>
                                </button>
                            </form>
                        </div>
                    </summary>
                    
                    <div class="px-6 pb-6 pt-2 bg-white/[0.02]">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4 border-t border-white/[0.03]">
                            <div class="space-y-4">
                                <div>
                                    <span class="text-[0.7rem] font-bold text-outline-variant uppercase tracking-tighter block mb-1">Meaning</span>
                                    <p class="text-[0.9rem] text-on-surface leading-relaxed">{{ item.word_entry.meaning }}</p>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <span class="text-[0.7rem] font-bold text-outline-variant uppercase tracking-tighter block mb-1">Example</span>
                                    <p class="text-[0.9rem] italic text-on-surface-variant">"{{ item.word_entry.sentence or 'No example provided.' }}"</p>
                                </div>
                            </div>
                            <div class="space-y-4">
                                <div>
                                    <span class="text-[0.7rem] font-bold text-outline-variant uppercase tracking-tighter block mb-1">Synonyms</span>
                                    <p class="text-[0.85rem] text-secondary">{{ item.word_entry.synonym or 'None available' }}</p>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <span class="text-[0.7rem] font-bold text-outline-variant uppercase tracking-tighter block mb-1">Personal Note</span>
                                    <form method="post" action="{{ url_for('save_word_note', user_word_id=item.id) }}" class="bg-[#121414] rounded-lg p-3 flex flex-col gap-2 border border-white/[0.1]">
                                        <input type="hidden" name="next" value="{{ request.full_path }}">
                                        <textarea name="note" class="w-full bg-transparent border-none outline-none focus:ring-0 text-[0.85rem] text-on-surface p-0 placeholder:text-outline-variant/40 no-scrollbar mb-1" placeholder="Add personal mnemonic or memory trick..." rows="2" style="resize: none;">{{ item.note or '' }}</textarea>
                                        <button type="submit" class="self-end text-[0.65rem] font-bold uppercase tracking-widest text-[#9dd0cd]/60 hover:text-[#9dd0cd] transition-colors bg-transparent border-none p-0 cursor-pointer">Save Note</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </details>
            {% endfor %}
        </div>
    {% else %}
        <div class="text-center py-16 bg-surface-container-lowest/50 rounded-xl border border-white/[0.05]">
            <span class="material-symbols-outlined text-4xl text-outline-variant mb-3">style</span>
            <p class="text-on-surface-variant">You do not have saved words yet.</p>
            <p class="text-sm mt-1 text-outline-variant">Go to the Dashboard to generate your first study set.</p>
        </div>
    {% endif %}
</div>
{% endblock %}
"""

with open('templates/words.html', 'w', encoding='utf-8') as f:
    f.write(WORDS_HTML)

print("words.html updated successfully with Tailwind integrations!")
