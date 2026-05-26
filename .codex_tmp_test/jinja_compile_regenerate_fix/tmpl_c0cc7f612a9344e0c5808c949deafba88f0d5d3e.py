from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'words.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'words.html')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    yield from parent_template.root_render_func(context)

def block_title(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield 'My Words | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_current_user = resolve('current_user')
    l_0_search_query = resolve('search_query')
    l_0_difficulty_filter = resolve('difficulty_filter')
    l_0_available_difficulties = resolve('available_difficulties')
    l_0_topic_filter = resolve('topic_filter')
    l_0_available_topics = resolve('available_topics')
    l_0_learned_filter = resolve('learned_filter')
    l_0_difficult_only = resolve('difficult_only')
    l_0_favorite_only = resolve('favorite_only')
    l_0_lookup_word = resolve('lookup_word')
    l_0_lookup_status = resolve('lookup_status')
    l_0_related_words = resolve('related_words')
    l_0_lookup_note = resolve('lookup_note')
    l_0_lookup_suggestions = resolve('lookup_suggestions')
    l_0_user_words = resolve('user_words')
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    pass
    yield '\n<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Inter:wght@300;400;500;600;700&family=Hind+Siliguri:wght@400;600&display=swap" rel="stylesheet"/>\n<style>\n    body.tw-dark-page {\n        background-color: #121414 !important;\n        color: #e2e2e2 !important;\n    }\n    .material-symbols-outlined {\n        font-variation-settings: \'FILL\' 0, \'wght\' 300, \'GRAD\' 0, \'opsz\' 20;\n    }\n    .no-scrollbar::-webkit-scrollbar {\n        display: none;\n    }\n    details > summary {\n        list-style: none;\n    }\n    details > summary::-webkit-details-marker {\n        display: none;\n    }\n    .word-row:hover {\n        background-color: rgba(255, 255, 255, 0.03);\n    }\n    details[open] .word-row {\n        background-color: rgba(255, 255, 255, 0.05);\n        border-bottom-color: transparent;\n    }\n    .font-bengali {\n        font-family: \'Hind Siliguri\', sans-serif;\n    }\n    \n    /* Safely override old global input styles for this tailwind container */\n    .tw-scope input, .tw-scope select, .tw-scope textarea {\n        color: #e2e2e2 !important;\n        background-color: transparent;\n        padding-left: 1rem;\n        padding-right: 1rem;\n    }\n    .tw-scope button {\n        background: none !important;\n        box-shadow: none !important;\n        color: inherit;\n    }\n    .tw-scope input[type="search"] { padding-left: 2.5rem; }\n    .words-primary-button {\n        background: linear-gradient(135deg, #9dd0cd 0%, #78b8b4 100%) !important;\n        color: #003735 !important;\n        box-shadow: 0 18px 34px rgba(45, 95, 93, 0.18) !important;\n    }\n    .words-outline-button {\n        background: rgba(157, 208, 205, 0.08) !important;\n        color: #9dd0cd !important;\n        border: 1px solid rgba(157, 208, 205, 0.16) !important;\n    }\n    .words-icon-button {\n        width: 2.1rem;\n        height: 2.1rem;\n        display: inline-flex;\n        align-items: center;\n        justify-content: center;\n        border-radius: 0.8rem;\n        border: 1px solid rgba(255, 255, 255, 0.06) !important;\n        background: rgba(255, 255, 255, 0.03) !important;\n        color: #6f7e7d !important;\n        transition: transform 0.18s ease, border-color 0.18s ease, color 0.18s ease, background-color 0.18s ease;\n    }\n    .words-icon-button:hover {\n        transform: translateY(-1px);\n    }\n    .words-icon-button.is-favorite-active {\n        border-color: rgba(222, 195, 143, 0.22) !important;\n        background: rgba(222, 195, 143, 0.1) !important;\n        color: #dec38f !important;\n    }\n    .words-icon-button.is-difficult-active {\n        border-color: rgba(255, 180, 171, 0.22) !important;\n        background: rgba(255, 180, 171, 0.1) !important;\n        color: #ffb4ab !important;\n    }\n    .words-note-button {\n        background: transparent !important;\n        color: #9dd0cd !important;\n    }\n    .word-lookup-shell {\n        margin-bottom: 2rem;\n    }\n    .word-lookup-card {\n        padding: 1.55rem;\n        border-radius: 1.8rem;\n        border: 1px solid rgba(64, 72, 72, 0.56);\n        background:\n            linear-gradient(180deg, rgba(30, 32, 32, 0.98), rgba(25, 27, 27, 0.98)),\n            radial-gradient(circle at top, rgba(157, 208, 205, 0.05), transparent 34%);\n        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.24);\n    }\n    .word-lookup-head {\n        display: flex;\n        align-items: flex-start;\n        justify-content: space-between;\n        gap: 1.25rem;\n        margin-bottom: 1.3rem;\n    }\n    .word-lookup-title-row {\n        display: flex;\n        align-items: center;\n        gap: 0.85rem;\n        flex-wrap: wrap;\n    }\n    .word-lookup-word {\n        margin: 0;\n        color: #f4f8f8;\n        font-family: "Manrope", "Inter", sans-serif;\n        font-size: clamp(2.2rem, 4vw, 3rem);\n        font-weight: 800;\n        letter-spacing: -0.05em;\n    }\n    .word-lookup-meaning {\n        margin: 0.9rem 0 0;\n        color: #f1f6f6;\n        font-size: 1.12rem;\n        font-weight: 600;\n        line-height: 1.65;\n    }\n    .word-lookup-grid {\n        display: grid;\n        grid-template-columns: repeat(2, minmax(0, 1fr));\n        gap: 1rem;\n    }\n    .word-lookup-detail {\n        min-height: 7.6rem;\n        padding: 1rem 1.05rem;\n        border-radius: 1.15rem;\n        border: 1px solid rgba(255, 255, 255, 0.05);\n        background: rgba(255, 255, 255, 0.02);\n    }\n    .word-lookup-detail.is-wide {\n        grid-column: 1 / -1;\n    }\n    .word-lookup-detail-label {\n        margin: 0;\n        color: #8ea5a4;\n        font-size: 0.68rem;\n        font-weight: 700;\n        letter-spacing: 0.18em;\n        text-transform: uppercase;\n    }\n    .word-lookup-detail-value {\n        margin: 0.8rem 0 0;\n        color: #eef4f4;\n        font-size: 1rem;\n        line-height: 1.7;\n        overflow-wrap: anywhere;\n    }\n    .word-lookup-detail-value.font-bengali {\n        font-size: 1.08rem;\n    }\n    .word-lookup-detail-synonym {\n        color: #9fe5be;\n    }\n    .word-lookup-detail-antonym {\n        color: #ffb4ab;\n    }\n    .word-lookup-detail-memory {\n        color: #f0dfba;\n    }\n    .word-lookup-pending {\n        margin: 0;\n        color: #c0c8c7;\n        font-size: 0.98rem;\n        line-height: 1.75;\n    }\n    @media (max-width: 800px) {\n        .word-lookup-head {\n            flex-direction: column;\n        }\n        .word-lookup-grid {\n            grid-template-columns: 1fr;\n        }\n        .word-lookup-detail.is-wide {\n            grid-column: auto;\n        }\n    }\n    \n    /* Hide base main shell padding */\n    .page-shell { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }\n</style>\n<div class="tw-scope font-body antialiased bg-[#121414] min-h-screen text-[#e2e2e2]">\n\n    <!-- TopNavBar Exactly as tailored for Tailwind -->\n    <header class="bg-[#121414]/80 backdrop-blur-xl fixed top-0 w-full z-50 border-b border-white/[0.05] shadow-lg">\n        <div class="app-topbar-row flex justify-between items-center h-16 px-4 sm:px-6 max-w-screen-2xl mx-auto font-headline tracking-tight gap-3 sm:gap-6">\n            <div class="app-topbar-brand-group flex items-center gap-4 sm:gap-8 min-w-0">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'index', _block_vars=_block_vars))
    yield '" class="text-2xl font-bold tracking-tighter text-primary no-underline">vflash.ai</a>\n                <nav class="hidden md:flex items-center gap-6 text-sm font-semibold pt-1">\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">Dashboard</a>\n                    <a class="text-primary border-b-2 border-primary pb-[0.2rem] no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">My Words</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '">Flashcards</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">Review</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', _block_vars=_block_vars))
    yield '">Quiz</a>\n                </nav>\n            </div>\n            <div class="app-topbar-actions flex items-center gap-4">\n                <button type="button" class="nav-chat-trigger nav-header-icon" data-feedback-open-chat aria-label="Message Faez" title="Message Faez">\n                    <span class="feedback-fab-icon"><span class="material-symbols-outlined">forum</span></span>\n                </button>\n                '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
        pass
        yield '\n                    <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', _block_vars=_block_vars))
        yield '" class="hidden md:inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-[0.72rem] font-bold uppercase tracking-[0.18em] text-primary no-underline transition-all hover:bg-primary/15 hover:brightness-110">Admin Panel</a>\n                '
    yield '\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '" class="hidden md:flex items-center gap-3 text-primary no-underline hover:brightness-125 transition-all outline-none">\n                    <span class="text-sm font-semibold tracking-wide hidden sm:block">'
    yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))
    yield '</span>\n                    <div class="w-8 h-8 rounded-full bg-surface-container-low border border-primary/30 flex items-center justify-center text-primary shadow-sm" title="Profile">\n                        <span class="material-symbols-outlined text-[1.1rem]">person</span>\n                    </div>\n                </a>\n                <div class="nav-menu" data-nav-menu>\n                    <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                        <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                    </button>\n                    <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                        <span class="nav-menu-email">'
    yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))
    yield '</span>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person</span><span>Profile</span></a>\n                        '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
        pass
        yield '\n                            <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', _block_vars=_block_vars))
        yield '"><span class="material-symbols-outlined">shield_person</span><span>Admin Panel</span></a>\n                        '
    yield '\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">dashboard</span><span>Dashboard</span></a>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">style</span><span>My Words</span></a>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">amp_stories</span><span>Flashcards</span></a>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">quiz</span><span>Quiz</span></a>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">rule</span><span>Review</span></a>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'logout', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">logout</span><span>Sign Out</span></a>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </header>\n\n    <main class="pt-24 pb-12 px-4 sm:px-6 max-w-screen-2xl mx-auto">\n        <!-- Filter Section -->\n        <section class="mb-8 space-y-4">\n            <form method="get" class="flex flex-col gap-4" data-async-page="true" data-auto-submit-controls="true" data-loading-messages=\'["Searching...","Checking saved collection...","Generating word details..."]\'>\n                <div class="grid grid-cols-1 md:grid-cols-[1fr_200px_200px_200px] gap-4">\n                    <div class="relative group h-11">\n                        <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-sm" data-icon="search">search</span>\n                        <input name="q" value="'
    yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
    yield '" class="w-full bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg pl-10 text-sm h-full text-on-surface placeholder:text-on-surface-variant/40 outline-none m-0 box-border" placeholder="Search any word, phrase, or topic" data-placeholder-full="Search any word, phrase, or topic" data-placeholder-compact="Search word, phrase, or topic" aria-label="Search any word, phrase, or topic" type="search"/>\n                    </div>\n                    <select name="difficulty" class="bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg text-sm h-11 text-on-surface-variant px-4 outline-none m-0 box-border">\n                        <option value="All" '
    yield escape(('selected' if ((undefined(name='difficulty_filter') if l_0_difficulty_filter is missing else l_0_difficulty_filter) == 'All') else ''))
    yield '>Difficulty: All</option>\n                        '
    for l_1_difficulty in (undefined(name='available_difficulties') if l_0_available_difficulties is missing else l_0_available_difficulties):
        _loop_vars = {}
        pass
        yield '\n                            <option value="'
        yield escape(l_1_difficulty)
        yield '" '
        yield escape(('selected' if ((undefined(name='difficulty_filter') if l_0_difficulty_filter is missing else l_0_difficulty_filter) == l_1_difficulty) else ''))
        yield '>'
        yield escape(l_1_difficulty)
        yield '</option>\n                        '
    l_1_difficulty = missing
    yield '\n                    </select>\n                    <select name="topic" class="bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg text-sm h-11 text-on-surface-variant px-4 outline-none m-0 box-border">\n                        <option value="All" '
    yield escape(('selected' if ((undefined(name='topic_filter') if l_0_topic_filter is missing else l_0_topic_filter) == 'All') else ''))
    yield '>Topic: All</option>\n                        '
    for l_1_topic in (undefined(name='available_topics') if l_0_available_topics is missing else l_0_available_topics):
        _loop_vars = {}
        pass
        yield '\n                            <option value="'
        yield escape(l_1_topic)
        yield '" '
        yield escape(('selected' if ((undefined(name='topic_filter') if l_0_topic_filter is missing else l_0_topic_filter) == l_1_topic) else ''))
        yield '>'
        yield escape(l_1_topic)
        yield '</option>\n                        '
    l_1_topic = missing
    yield '\n                    </select>\n                    <select name="learned" class="bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-lg text-sm h-11 text-on-surface-variant px-4 outline-none m-0 box-border">\n                        <option value="all" '
    yield escape(('selected' if ((undefined(name='learned_filter') if l_0_learned_filter is missing else l_0_learned_filter) == 'all') else ''))
    yield '>Learning State: All</option>\n                        <option value="learned" '
    yield escape(('selected' if ((undefined(name='learned_filter') if l_0_learned_filter is missing else l_0_learned_filter) == 'learned') else ''))
    yield '>Learned</option>\n                        <option value="learning" '
    yield escape(('selected' if ((undefined(name='learned_filter') if l_0_learned_filter is missing else l_0_learned_filter) == 'learning') else ''))
    yield '>Learning</option>\n                    </select>\n                </div>\n                \n                <div class="flex flex-col md:flex-row items-start md:items-center justify-end gap-4 md:gap-6">\n                    <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">\n                        <label class="flex items-center gap-2 cursor-pointer group m-0">\n                            <input name="difficult" type="checkbox" value="1" '
    yield escape(('checked' if (undefined(name='difficult_only') if l_0_difficult_only is missing else l_0_difficult_only) else ''))
    yield ' class="w-4 h-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary" style="accent-color: #9dd0cd;"/>\n                            <span class="text-[0.65rem] uppercase font-bold tracking-widest text-[#8a9291] group-hover:text-primary transition-colors mt-[2px]">Difficult only</span>\n                        </label>\n                        <label class="flex items-center gap-2 cursor-pointer group m-0">\n                            <input name="favorite" type="checkbox" value="1" '
    yield escape(('checked' if (undefined(name='favorite_only') if l_0_favorite_only is missing else l_0_favorite_only) else ''))
    yield ' class="w-4 h-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary" style="accent-color: #9dd0cd;"/>\n                            <span class="text-[0.65rem] uppercase font-bold tracking-widest text-[#8a9291] group-hover:text-primary transition-colors mt-[2px]">Favorites only</span>\n                        </label>\n                    </div>\n                </div>\n            </form>\n        </section>\n\n        '
    if ((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word) or ((undefined(name='lookup_status') if l_0_lookup_status is missing else l_0_lookup_status) in ['suggestions', 'not_found'])):
        pass
        yield '\n            <section class="word-lookup-shell">\n                <article class="word-lookup-card">\n                    '
        if (undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word):
            pass
            yield '\n                        <div class="word-lookup-head">\n                            <div>\n                                <div class="word-lookup-title-row">\n                                    <h2 class="word-lookup-word">'
            yield escape(environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'word'))
            yield '</h2>\n                                    '
            if environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'part_of_speech'):
                pass
                yield '\n                                        <span class="flashcard-pos">'
                yield escape(environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'part_of_speech'))
                yield '</span>\n                                    '
            yield '\n                                </div>\n                                <p class="word-lookup-meaning">\n                                    '
            if environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'lookup_pending'):
                pass
                yield '\n                                        We are preparing this word now so your flashcard stays accurate and useful.\n                                    '
            else:
                pass
                yield '\n                                        '
                yield escape(environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'meaning'))
                yield '\n                                    '
            yield '\n                                </p>\n                            </div>\n                        </div>\n                        '
            if environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'lookup_pending'):
                pass
                yield '\n                            <p class="word-lookup-pending">Search another word now, and check this one again shortly. We are actively preparing vocabulary across beginner, advanced, and rare levels.</p>\n                        '
            else:
                pass
                yield '\n                            <div class="word-lookup-grid">\n                                <div class="word-lookup-detail">\n                                    <p class="word-lookup-detail-label">Bangla meaning</p>\n                                    <p class="word-lookup-detail-value font-bengali">'
                yield escape((environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'bangla_meaning') or 'No Bangla meaning yet.'))
                yield '</p>\n                                </div>\n                                <div class="word-lookup-detail">\n                                    <p class="word-lookup-detail-label">Pronunciation</p>\n                                    <p class="word-lookup-detail-value">'
                yield escape((environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'phonetic') or 'Not added yet.'))
                yield '</p>\n                                </div>\n                                <div class="word-lookup-detail">\n                                    <p class="word-lookup-detail-label">Synonym</p>\n                                    <p class="word-lookup-detail-value word-lookup-detail-synonym">'
                yield escape(((environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'synonym_hint') or environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'synonym')) or 'Not added yet.'))
                yield '</p>\n                                </div>\n                                '
                if environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'antonym_hint'):
                    pass
                    yield '\n                                    <div class="word-lookup-detail">\n                                        <p class="word-lookup-detail-label">Antonym</p>\n                                        <p class="word-lookup-detail-value word-lookup-detail-antonym">'
                    yield escape(environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'antonym_hint'))
                    yield '</p>\n                                    </div>\n                                '
                yield '\n                                <div class="word-lookup-detail">\n                                    <p class="word-lookup-detail-label">Topic</p>\n                                    <p class="word-lookup-detail-value">'
                yield escape((environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'topic') or 'General'))
                yield '</p>\n                                </div>\n                                <div class="word-lookup-detail is-wide">\n                                    <p class="word-lookup-detail-label">Sentence</p>\n                                    <p class="word-lookup-detail-value">'
                yield escape((environment.getattr((undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word), 'sentence') or 'No example sentence yet.'))
                yield '</p>\n                                </div>\n                                '
                if (undefined(name='related_words') if l_0_related_words is missing else l_0_related_words):
                    pass
                    yield '\n                                    <div class="word-lookup-detail is-wide">\n                                        <p class="word-lookup-detail-label">Related forms</p>\n                                        <p class="word-lookup-detail-value">'
                    yield escape(t_1(context.eval_ctx, (undefined(name='related_words') if l_0_related_words is missing else l_0_related_words), ', '))
                    yield '</p>\n                                    </div>\n                                '
                yield '\n                                '
                if (undefined(name='lookup_note') if l_0_lookup_note is missing else l_0_lookup_note):
                    pass
                    yield '\n                                    <div class="word-lookup-detail is-wide">\n                                        <p class="word-lookup-detail-label">Your note</p>\n                                        <p class="word-lookup-detail-value">'
                    yield escape((undefined(name='lookup_note') if l_0_lookup_note is missing else l_0_lookup_note))
                    yield '</p>\n                                    </div>\n                                '
                yield '\n                            </div>\n                        '
            yield '\n                    '
        else:
            pass
            yield '\n                        <div class="word-lookup-head">\n                            <div>\n                                <div class="word-lookup-title-row">\n                                    <h2 class="word-lookup-word">'
            yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
            yield '</h2>\n                                </div>\n                                <p class="word-lookup-meaning">\n                                    '
            if ((undefined(name='lookup_status') if l_0_lookup_status is missing else l_0_lookup_status) == 'suggestions'):
                pass
                yield '\n                                        We could not safely match that spelling to a valid word.\n                                    '
            else:
                pass
                yield '\n                                        This word was not found in the database or fallback dictionary.\n                                    '
            yield '\n                                </p>\n                            </div>\n                        </div>\n                        <div class="word-lookup-grid">\n                            <div class="word-lookup-detail is-wide">\n                                <p class="word-lookup-detail-label">Search guidance</p>\n                                '
            if (undefined(name='lookup_suggestions') if l_0_lookup_suggestions is missing else l_0_lookup_suggestions):
                pass
                yield '\n                                    <p class="word-lookup-detail-value">You entered: \''
                yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
                yield '\'</p>\n                                    <p class="word-lookup-detail-value">Did you mean: '
                yield escape(t_1(context.eval_ctx, (undefined(name='lookup_suggestions') if l_0_lookup_suggestions is missing else l_0_lookup_suggestions), ', '))
                yield '</p>\n                                '
            else:
                pass
                yield '\n                                    <p class="word-lookup-detail-value">We did not generate a definition because the spelling could not be verified safely.</p>\n                                '
            yield '\n                            </div>\n                        </div>\n                    '
        yield '\n                </article>\n            </section>\n        '
    yield '\n\n        <!-- Word List: High-Density Interactive List -->\n        '
    if (undefined(name='user_words') if l_0_user_words is missing else l_0_user_words):
        pass
        yield '\n            <div class="bg-[#0d0f0f]/40 border border-white/[0.05] rounded-xl overflow-hidden mb-8">\n                <!-- Header Row -->\n                <div class="hidden md:grid grid-cols-[160px_100px_160px_1fr_100px_90px] gap-6 px-6 py-4 bg-white/[0.02] border-b border-white/[0.05] text-[0.65rem] font-bold uppercase tracking-widest text-[#8a9291]">\n                    <div>Word</div>\n                    <div class="text-left">Type</div>\n                    <div>Bangla Meaning</div>\n                    <div>Definition</div>\n                    <div class="text-center">Status</div>\n                    <div class="text-right">Actions</div>\n                </div>\n\n                '
        l_1_loop = missing
        for l_1_item, l_1_loop in LoopContext((undefined(name='user_words') if l_0_user_words is missing else l_0_user_words), undefined):
            l_1_request = resolve('request')
            _loop_vars = {}
            pass
            yield '\n                    <details class="group border-b border-white/[0.05] last:border-b-0" '
            if (environment.getattr(l_1_loop, 'index') == 1):
                pass
                yield 'open'
            yield '>\n                        <summary class="word-row grid grid-cols-[1fr_80px_90px] md:grid-cols-[160px_100px_160px_1fr_100px_90px] items-center gap-4 md:gap-6 px-6 py-5 cursor-pointer transition-colors outline-none h-full m-0">\n                            <div class="flex flex-col md:block min-w-0">\n                                <h3 class="text-base font-headline font-bold text-primary tracking-tight truncate m-0">'
            yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'word'))
            yield '</h3>\n                                <span class="md:hidden text-[0.65rem] font-medium text-on-surface-variant/60 truncate">'
            yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'bangla_meaning') or 'No translation'))
            yield '</span>\n                            </div>\n                            \n                            <div class="hidden md:flex items-center">\n                                <span class="text-[0.6rem] font-bold text-[#dec38f] uppercase tracking-widest opacity-80 mt-1">'
            yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'part_of_speech') or 'Word'))
            yield '</span>\n                            </div>\n                            \n                            <div class="hidden md:flex items-center font-bengali text-[0.95rem] font-semibold text-white truncate h-full mt-1">'
            yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'bangla_meaning') or '--'))
            yield '</div>\n                            \n                            <div class="hidden md:flex items-center text-[0.85rem] text-[#8a9291] truncate pr-4 h-full mt-1">'
            yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'meaning'))
            yield '</div>\n                            \n                            <div class="flex justify-center mt-1">\n                                '
            if environment.getattr(l_1_item, 'learned'):
                pass
                yield '\n                                    <span class="bg-[#2d5f5d]/20 text-[#9dd0cd] text-[0.55rem] px-2.5 py-1 rounded-full font-bold uppercase tracking-widest border border-[#9dd0cd]/20">Mastered</span>\n                                '
            else:
                pass
                yield '\n                                    <span class="bg-[#93000a]/20 text-[#ffb4ab] text-[0.55rem] px-2.5 py-1 rounded-full font-bold uppercase tracking-widest border border-[#ffb4ab]/20">Reviewing</span>\n                                '
            yield '\n                            </div>\n                            \n                            <div class="flex justify-end items-center gap-3">\n                                <form method="post" action="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'toggle_favorite_flag', user_word_id=environment.getattr(l_1_item, 'id'), _loop_vars=_loop_vars))
            yield '" class="m-0 flex items-center">\n                                    <input type="hidden" name="next" value="'
            yield escape(environment.getattr((undefined(name='request') if l_1_request is missing else l_1_request), 'full_path'))
            yield '">\n                                    <button type="submit" class="words-icon-button '
            yield escape(('is-favorite-active' if environment.getattr(l_1_item, 'is_favorite') else ''))
            yield ' cursor-pointer p-0 m-0 flex items-center outline-none" title="Favorite" onclick="event.stopPropagation();">\n                                        <span class="material-symbols-outlined text-lg opacity-80" data-icon="star" '
            if environment.getattr(l_1_item, 'is_favorite'):
                pass
                yield 'style="font-variation-settings: \'FILL\' 1;"'
            yield '>star</span>\n                                    </button>\n                                </form>\n                                <form method="post" action="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'toggle_difficult_flag', user_word_id=environment.getattr(l_1_item, 'id'), _loop_vars=_loop_vars))
            yield '" class="m-0 flex items-center">\n                                    <input type="hidden" name="next" value="'
            yield escape(environment.getattr((undefined(name='request') if l_1_request is missing else l_1_request), 'full_path'))
            yield '">\n                                    <button type="submit" class="words-icon-button '
            yield escape(('is-difficult-active' if environment.getattr(l_1_item, 'is_difficult') else ''))
            yield ' cursor-pointer p-0 m-0 flex items-center outline-none" title="Difficult" onclick="event.stopPropagation();">\n                                        <span class="material-symbols-outlined text-lg opacity-80" data-icon="priority_high" '
            if environment.getattr(l_1_item, 'is_difficult'):
                pass
                yield 'style="font-variation-settings: \'FILL\' 1;"'
            yield '>priority_high</span>\n                                    </button>\n                                </form>\n                            </div>\n                        </summary>\n                        \n                        <div class="px-6 pb-6 pt-2 bg-white/[0.01]">\n                            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4 border-t border-white/[0.03]">\n                                <div class="space-y-4">\n                                    <div class="m-0">\n                                        <span class="text-[0.65rem] font-bold text-[#404848] uppercase tracking-widest block mb-2">Meaning</span>\n                                        <p class="text-[0.9rem] text-white leading-relaxed m-0 font-medium">'
            yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'meaning'))
            yield '</p>\n                                    </div>\n                                    '
            if environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'sentence'):
                pass
                yield '\n                                    <div style="margin-top: 1.5rem;">\n                                        <span class="text-[0.65rem] font-bold text-[#404848] uppercase tracking-widest block mb-2">Example</span>\n                                        <p class="text-[0.9rem] italic text-[#8a9291] m-0">"'
                yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'sentence'))
                yield '"</p>\n                                    </div>\n                                    '
            yield '\n                                </div>\n                                <div class="space-y-4">\n                                    '
            if (environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'synonym_hint') or environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'synonym')):
                pass
                yield '\n                                    <div class="m-0">\n                                        <span class="text-[0.65rem] font-bold text-[#404848] uppercase tracking-widest block mb-2">Synonyms</span>\n                                        <p class="text-[0.85rem] text-[#dec38f] m-0">'
                yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'synonym_hint') or environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'synonym')))
                yield '</p>\n                                    </div>\n                                    '
            yield '\n                                    '
            if environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'antonym_hint'):
                pass
                yield '\n                                        <div style="margin-top: 1.5rem;">\n                                            <span class="text-[0.65rem] font-bold text-[#404848] uppercase tracking-widest block mb-2">Antonym</span>\n                                            <p class="text-[0.85rem] text-[#ffb4ab] m-0">'
                yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'antonym_hint'))
                yield '</p>\n                                        </div>\n                                    '
            yield '\n                                    <div style="margin-top: 1.5rem;">\n                                        <span class="text-[0.65rem] font-bold text-[#404848] uppercase tracking-widest block mb-2">Personal Note</span>\n                                        <form method="post" action="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'save_word_note', user_word_id=environment.getattr(l_1_item, 'id'), _loop_vars=_loop_vars))
            yield '" class="bg-[#121414] rounded-lg p-3 flex flex-col gap-2 border border-white/[0.05] shadow-inner mb-0">\n                                            <input type="hidden" name="next" value="'
            yield escape(environment.getattr((undefined(name='request') if l_1_request is missing else l_1_request), 'full_path'))
            yield '">\n                                            <textarea name="note" class="w-full bg-transparent border-none outline-none focus:ring-0 text-[0.85rem] text-[#e2e2e2] p-0 placeholder:text-[#404848] no-scrollbar m-0 min-h-[2.5rem] resize-y" placeholder="Add a personal note..." rows="2">'
            yield escape((environment.getattr(l_1_item, 'note') or ''))
            yield '</textarea>\n                                            <button type="submit" class="words-note-button self-end text-[0.65rem] font-bold uppercase tracking-widest hover:brightness-125 transition-colors border-none p-0 cursor-pointer m-0 mt-1">Save Note</button>\n                                        </form>\n                                    </div>\n                                </div>\n                            </div>\n                        </div>\n                    </details>\n                '
        l_1_loop = l_1_item = l_1_request = missing
        yield '\n            </div>\n        '
    else:
        pass
        yield '\n            '
        if (not (undefined(name='lookup_word') if l_0_lookup_word is missing else l_0_lookup_word)):
            pass
            yield '\n                <div class="text-center py-16 bg-[#0d0f0f] rounded-xl border border-white/[0.05]">\n                    <span class="material-symbols-outlined text-4xl text-[#404848] mb-3 opacity-50">style</span>\n                    <p class="text-[#8a9291]">'
            yield escape(('No saved words matched your search.' if (undefined(name='search_query') if l_0_search_query is missing else l_0_search_query) else 'You do not have saved words yet.'))
            yield '</p>\n                </div>\n            '
        yield '\n        '
    yield '\n    </main>\n</div>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&196=58&198=60&199=62&200=64&201=66&202=68&209=70&210=73&212=76&213=78&223=80&224=82&225=84&226=87&228=90&229=92&230=94&231=96&232=98&233=100&247=102&250=104&251=106&252=110&256=118&257=120&258=124&262=132&263=134&264=136&271=138&275=140&283=142&286=145&290=148&291=150&292=153&296=156&299=162&304=165&310=171&314=173&318=175&320=177&323=180&328=183&332=185&334=187&337=190&340=193&343=196&352=203&355=205&366=212&367=215&368=217&380=225&392=229&393=234&396=238&397=240&401=242&404=244&406=246&409=248&417=255&418=257&419=259&420=261&423=265&424=267&425=269&426=271&437=275&439=277&442=280&447=283&450=286&453=289&456=292&461=295&462=297&463=299&474=306&477=309'