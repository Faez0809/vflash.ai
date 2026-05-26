from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'flashcards.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'flashcards.html')
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
    l_0_review_mode = resolve('review_mode')
    pass
    yield escape(('Review' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'Flashcards'))
    yield ' | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_review_mode = resolve('review_mode')
    l_0_current_user = resolve('current_user')
    l_0_user_words = resolve('user_words')
    l_0_study_session = resolve('study_session')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_2 = environment.filters['tojson']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'tojson' found.")
    pass
    yield '\n<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>\n\n<style>\n    /* Safely override base styles so main layout is unpadded tailwind shell */\n    .page-shell { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }\n    \n    .stitch-label {\n        font-size: 0.65rem;\n        letter-spacing: 0.15em;\n        text-transform: uppercase;\n        color: #8a9291;\n        font-weight: 600;\n    }\n    .flashcard-glow {\n        box-shadow: 0 48px 48px -12px rgba(157, 208, 205, 0.04);\n    }\n    .editorial-shadow {\n        box-shadow: 0 48px 48px -12px rgba(157, 208, 205, 0.04);\n    }\n    /* 3D Flip Mechanics */\n    .perspective-1000 {\n        perspective: 1000px;\n    }\n    .transform-style-3d {\n        transform-style: preserve-3d;\n    }\n    /* Hide the opposite face to prevent mirroring and ghosting */\n    #flashcard-flip:not(.is-flipped) .flashcard-back {\n        opacity: 0;\n        pointer-events: none;\n        transition: opacity 0.2s;\n    }\n    #flashcard-flip.is-flipped .flashcard-front {\n        opacity: 0;\n        pointer-events: none;\n        transition: opacity 0.2s;\n    }\n    \n    /* Reveal the active face */\n    #flashcard-flip:not(.is-flipped) .flashcard-front {\n        opacity: 1;\n        transition: opacity 0.2s 0.1s;\n    }\n    #flashcard-flip.is-flipped .flashcard-back {\n        opacity: 1;\n        transition: opacity 0.2s 0.1s;\n    }\n    #flashcard-flip.is-flipped #flip-inner {\n        transform: rotateY(180deg);\n    }\n    #flashcard-flip {\n        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;\n        will-change: transform;\n    }\n    @media (min-width: 768px) and (hover: hover) and (pointer: fine) {\n        #flashcard-flip.is-desktop-clickable {\n            cursor: pointer;\n        }\n        #flashcard-flip.is-desktop-clickable:hover {\n            transform: scale(1.01);\n            filter: brightness(1.02);\n        }\n        #flashcard-flip.is-desktop-clickable:hover .flashcard-glow,\n        #flashcard-flip.is-desktop-clickable:hover .editorial-shadow {\n            box-shadow: 0 56px 60px -16px rgba(157, 208, 205, 0.08);\n        }\n        #flashcard-flip.is-desktop-clickable.is-pressing {\n            transform: scale(0.95);\n        }\n    }\n    \n    /* Zero scroll styling but without breaking short screens */\n    body {\n        background-color: #121414 !important;\n    }\n    \n    /* Reset style.css global overrides for our custom tailwind buttons */\n    .tw-scope button {\n        background-image: none !important;\n        box-shadow: none !important;\n        color: inherit !important;\n        border: none !important;\n    }\n</style>\n\n<div class="tw-scope flashcards-local-shell font-body antialiased bg-[#121414] min-h-screen flex flex-col text-[#e2e2e2] m-0 overflow-x-hidden pt-20 pb-28 md:pb-12">\n    \n    <!-- TopNavBar Exactly as tailored for Tailwind -->\n    <header class="bg-[#121414]/60 backdrop-blur-xl fixed top-0 w-full z-50 border-b border-white/[0.05] shadow-lg">\n        <div class="app-topbar-row flex justify-between items-center h-16 px-4 sm:px-6 max-w-screen-2xl mx-auto font-headline tracking-tight gap-3 sm:gap-6">\n            <div class="app-topbar-brand-group flex items-center gap-4 sm:gap-8 min-w-0">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'index', _block_vars=_block_vars))
    yield '" class="text-2xl font-bold tracking-tighter text-primary no-underline hover:text-primary">vflash.ai</a>\n                <nav class="hidden md:flex items-center gap-6 text-sm font-semibold pt-1">\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">Dashboard</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">My Words</a>\n                    <a class="'
    yield escape(('text-primary border-b-2 border-primary pb-[0.2rem]' if (not (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode)) else 'text-primary/60'))
    yield ' no-underline hover:text-primary transition-all" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '">Flashcards</a>\n                    <a class="'
    yield escape(('text-primary border-b-2 border-primary pb-[0.2rem]' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'text-primary/60'))
    yield ' no-underline hover:text-primary transition-all" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">Review</a>\n                </nav>\n            </div>\n            <div class="app-topbar-actions flex items-center gap-4">\n                <button type="button" class="nav-chat-trigger nav-header-icon" data-feedback-open-chat aria-label="Message Faez" title="Message Faez">\n                    <span class="feedback-fab-icon"><span class="material-symbols-outlined">forum</span></span>\n                </button>\n                '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
        pass
        yield '\n                    <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', _block_vars=_block_vars))
        yield '" class="hidden md:inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-[0.72rem] font-bold uppercase tracking-[0.18em] text-primary no-underline transition-all hover:bg-primary/15 hover:brightness-110">Admin Panel</a>\n                '
    yield '\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '" class="hidden md:flex items-center gap-3 text-primary no-underline hover:brightness-125 transition-all outline-none">\n                    <span class="text-sm font-semibold tracking-wide hidden sm:block">'
    yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))
    yield '</span>\n                    <div class="w-8 h-8 rounded-full bg-surface-container-low border border-primary/30 flex items-center justify-center text-primary shadow-sm" title="Profile">\n                        <span class="material-symbols-outlined text-[1.1rem]" style="font-variation-settings: \'FILL\' 0, \'wght\' 300, \'GRAD\' 0, \'opsz\' 24;">person</span>\n                    </div>\n                </a>\n                <div class="nav-menu" data-nav-menu>\n                    <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                        <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                    </button>\n                    <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                        <span class="nav-menu-email">'
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
    yield '"><span class="material-symbols-outlined">logout</span><span>Sign Out</span></a>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </header>\n\n    '
    if (undefined(name='user_words') if l_0_user_words is missing else l_0_user_words):
        pass
        yield '\n        <div id="flashcard-app"\n            data-mode="'
        yield escape(('review' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'study'))
        yield '"\n            data-cards=\'[\n            '
        l_1_loop = missing
        for l_1_item, l_1_loop in LoopContext((undefined(name='user_words') if l_0_user_words is missing else l_0_user_words), undefined):
            _loop_vars = {}
            pass
            yield '\n                {\n                    "id": '
            yield escape(environment.getattr(l_1_item, 'id'))
            yield ',\n                    "word": '
            yield escape(t_2(context.eval_ctx, environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'word')))
            yield ',\n                    "is_difficult": '
            yield escape(t_2(context.eval_ctx, environment.getattr(l_1_item, 'is_difficult')))
            yield ',\n                    "already_known": '
            yield escape(t_2(context.eval_ctx, environment.getattr(l_1_item, 'already_known')))
            yield ',\n                    "part_of_speech": '
            yield escape(t_2(context.eval_ctx, (environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'part_of_speech') or '')))
            yield ',\n                    "meaning": '
            yield escape(t_2(context.eval_ctx, environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'meaning')))
            yield ',\n                    "bangla_meaning": '
            yield escape(t_2(context.eval_ctx, (environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'bangla_meaning') or '')))
            yield ',\n                    "sentence": '
            yield escape(t_2(context.eval_ctx, (environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'sentence') or '')))
            yield ',\n                    "phonetic": '
            yield escape(t_2(context.eval_ctx, (environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'phonetic') or '')))
            yield ',\n                    "synonym": '
            yield escape(t_2(context.eval_ctx, ((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'synonym_hint') or environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'synonym')) or '')))
            yield ',\n                    "antonym": '
            yield escape(t_2(context.eval_ctx, (environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'antonym_hint') or '')))
            yield '\n                }'
            yield escape((',' if (not environment.getattr(l_1_loop, 'last')) else cond_expr_undefined("the inline if-expression on line 157 in 'flashcards.html' evaluated to false and no else section was defined.")))
            yield '\n            '
        l_1_loop = l_1_item = missing
        yield '\n            ]\'\n            class="flex flex-col items-center w-full max-w-screen-2xl px-4 sm:px-6 mx-auto relative my-auto"\n        >\n\n            <!-- Keyboard Shortcuts (Side Info) -->\n            <div class="absolute left-12 top-1/2 -translate-y-1/2 hidden xl:flex flex-col gap-6">\n                <div class="flex items-center gap-3 text-emerald-400/60 group">\n                    <span class="px-2 py-1 bg-emerald-500/5 rounded border border-emerald-500/20 text-[10px] font-mono group-hover:text-emerald-300 transition-colors">SPACE</span>\n                    <span class="text-xs uppercase tracking-widest font-medium group-hover:text-emerald-300 transition-colors">Reveal</span>\n                </div>\n                <div class="flex items-center gap-3 text-cyan-400/60 group">\n                    <span class="px-2 py-1 bg-cyan-500/5 rounded border border-cyan-500/20 text-[10px] font-mono group-hover:text-cyan-300 transition-colors">→</span>\n                    <span class="text-xs uppercase tracking-widest font-medium group-hover:text-cyan-300 transition-colors">Next</span>\n                </div>\n            </div>\n\n            <!-- Session Progress Bar -->\n            <div class="w-full max-w-[600px] flex flex-col gap-2 mb-4">\n                <div class="flex justify-between text-[10px] font-bold tracking-widest text-emerald-400/80 uppercase">\n                    <span>'
        yield escape(('Review Progress' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'Session Progress'))
        yield '</span>\n                    <span class="text-cyan-400/80" id="flashcard-count">1 / '
        yield escape(t_1((undefined(name='user_words') if l_0_user_words is missing else l_0_user_words)))
        yield ' Cards</span>\n                </div>\n                <div class="h-1 w-full bg-surface-container-highest rounded-full overflow-hidden">\n                    <div id="flashcard-progress" class="h-full w-0 bg-gradient-to-r from-primary to-primary-container shadow-[0_0_8px_rgba(157,208,205,0.4)] opacity-80 relative overflow-hidden transition-all duration-300">\n                        <div class="absolute inset-0 bg-white/20 w-1/2 animate-[progress-pulse_2s_infinite]"></div>\n                    </div>\n                </div>\n            </div>\n\n            '
        if ((undefined(name='study_session') if l_0_study_session is missing else l_0_study_session) and (not (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode))):
            pass
            yield '\n            <form method="post" action="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'generate_words', _block_vars=_block_vars))
            yield '" class="w-full max-w-[600px] mb-4">\n                <input type="hidden" name="difficulty" value="'
            yield escape(environment.getattr((undefined(name='study_session') if l_0_study_session is missing else l_0_study_session), 'difficulty'))
            yield '">\n                <input type="hidden" name="word_count" value="'
            yield escape(environment.getattr((undefined(name='study_session') if l_0_study_session is missing else l_0_study_session), 'word_count'))
            yield '">\n                <input type="hidden" name="order_mode" value="mixed">\n                <button\n                    type="submit"\n                    class="w-full rounded-2xl border border-primary/20 bg-primary/10 px-4 py-3 text-sm font-bold uppercase tracking-[0.18em] text-primary transition-all hover:bg-primary/15 hover:brightness-110"\n                >\n                    Start More From This Level\n                </button>\n            </form>\n            '
        yield '\n\n            <!-- Main Flashcard Container -->\n            <div class="relative w-full max-w-[600px]">\n                \n                <!-- Card Meta Header -->\n                <div class="flashcard-session-toolbar flex justify-between items-center mb-4 px-2">\n                    <span class="font-label text-xs text-teal-400/70 tracking-wider font-bold uppercase">'
        yield escape(('Review Queue' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'Current Session'))
        yield '</span>\n                    <button type="button" id="flashcard-restart-btn" class="w-11 h-11 flex items-center justify-center rounded-full bg-surface-variant hover:bg-surface-bright transition-all duration-300 active:scale-95 border-none outline-none cursor-pointer" title="Restart Session" aria-label="Restart session">\n                        <span class="material-symbols-outlined text-primary text-lg" style="font-variation-settings: \'FILL\' 0, \'wght\' 500, \'GRAD\' 0, \'opsz\' 24;">restart_alt</span>\n                    </button>\n                </div>\n\n                <!-- 3D Flipping Card -->\n                <div id="flashcard-flip" class="w-full aspect-[4/5] sm:aspect-[16/10] perspective-1000 group cursor-pointer active:scale-[0.99] transition-transform duration-200 outline-none">\n                    <div id="flip-inner" class="relative w-full h-full transition-transform duration-500 transform-style-3d">\n                        \n                        <!-- FRONT OF CARD -->\n                        <div class="flashcard-front absolute inset-0 w-full h-full bg-surface-container-low rounded-xl flashcard-glow border border-white/[0.03] flex flex-col">\n                            \n                            <!-- Card Center Content -->\n                            <div class="flex-grow flex flex-col items-center justify-center text-center px-6 sm:px-12 relative z-10 overflow-visible">\n                                <h1 class="text-4xl sm:text-6xl font-bold font-headline bg-gradient-to-br from-emerald-200 via-teal-200 to-cyan-400 bg-clip-text text-transparent tracking-tighter drop-shadow-sm pb-2 leading-tight" id="flashcard-word" style="word-break: break-word;"></h1>\n                                <div class="px-3 py-0.5 bg-[#dec38f]/10 border border-[#dec38f]/20 rounded-full text-[10px] font-bold text-[#dec38f] tracking-[0.2em] uppercase mt-2 mb-8" id="flashcard-part-of-speech">\n                                </div>\n                                <p class="text-sm text-outline font-medium animate-pulse m-0 md:hidden">Tap to flip. Swipe left or right to change flashcards.</p>\n                                <p class="hidden md:block text-sm text-outline font-medium animate-pulse m-0">Click left for previous, center to flip, and right for next.</p>\n                            </div>\n                            \n                            <!-- Card Footer -->\n                            <div class="p-4 sm:p-6 flex items-center justify-center gap-4 relative z-10 mt-auto border-t border-white/[0.02]">\n                                <button class="material-symbols-outlined text-emerald-400/80 hover:text-emerald-300 transition-colors p-2 hover:bg-white/5 rounded-full border border-white/5 cursor-pointer text-lg outline-none backdrop-blur-sm shadow-sm" style="font-variation-settings: \'FILL\' 0;" onclick="event.stopPropagation();">volume_up</button>\n                                <span class="text-sm font-medium text-emerald-300/80 font-mono tracking-tight" id="flashcard-front-phonetic"></span>\n                            </div>\n\n                            <!-- Subtle Tonal Gradient Overlay -->\n                            <div class="absolute inset-0 pointer-events-none bg-gradient-to-br from-primary/5 to-transparent opacity-30 rounded-xl"></div>\n                        </div>\n\n                        <!-- BACK OF CARD -->\n                        <div class="flashcard-back absolute inset-0 w-full h-full bg-surface-container-low rounded-xl p-5 sm:p-8 editorial-shadow border border-white/[0.03] flex flex-col items-center text-center" style="transform: rotateY(180deg);">\n                            <div class="flashcard-direct-head mb-4 w-full flex-shrink-0 overflow-visible">\n                                <div class="search-word-heading">\n                                    <h1 class="font-headline text-3xl sm:text-5xl font-extrabold tracking-tighter m-0 pb-2 leading-tight" id="flashcard-word-back" style="word-break: break-word;"></h1>\n                                    <span class="flashcard-pos" id="flashcard-part-of-speech-back"></span>\n                                </div>\n                                <p class="search-flashcard-meaning" id="flashcard-meaning"></p>\n                            </div>\n                            \n                            <!-- Fields Stack -->\n                            <div class="flashcard-back-grid search-flashcard-grid search-direct-grid w-full overflow-y-auto no-scrollbar flex-grow relative z-10 px-1">\n                                <div class="flashcard-detail" data-flashcard-field="bangla">\n                                        <p class="stitch-label mb-2 m-0 text-[#8a9291]">Bangla meaning</p>\n                                        <p class="font-body text-base sm:text-lg font-medium m-0 mt-1" id="flashcard-bangla-meaning"></p>\n                                </div>\n                                <div class="flashcard-detail" data-flashcard-field="phonetic">\n                                    <p class="stitch-label mb-2 m-0 text-[#8a9291]">Pronunciation</p>\n                                    <p class="font-body text-slate-200 text-[0.85rem] sm:text-sm leading-relaxed m-0" id="flashcard-phonetic"></p>\n                                </div>\n                                <div class="flashcard-detail" data-flashcard-field="synonym">\n                                        <p class="stitch-label mb-2 m-0 text-[#8a9291]">Synonym</p>\n                                        <p class="font-body text-emerald-300 text-[0.8rem] sm:text-sm leading-relaxed m-0" id="flashcard-synonym"></p>\n                                </div>\n                                <div class="flashcard-detail" id="flashcard-antonym-card" data-flashcard-field="antonym">\n                                        <p class="stitch-label mb-2 m-0 text-[#8a9291]">Antonym</p>\n                                        <p class="font-body text-orange-200 text-[0.8rem] sm:text-sm leading-relaxed m-0" id="flashcard-antonym"></p>\n                                </div>\n\n                                <!-- Sentence -->\n                                <div class="flashcard-detail search-flashcard-detail-wide" data-flashcard-field="sentence">\n                                    <p class="stitch-label mb-2 m-0 text-[#8a9291]">Sentence</p>\n                                    <p class="font-body italic text-sky-200 leading-relaxed text-[0.85rem] sm:text-sm m-0" id="flashcard-sentence"></p>\n                                </div>\n                            </div>\n                        </div>\n\n                    </div>\n                </div>\n\n                <!-- Action Buttons Grid -->\n                <div class="grid grid-cols-3 gap-3 mt-4 relative z-10 w-full max-w-[600px] mx-auto">\n                    <button id="mark-learned-btn" class="flex flex-col items-center justify-center py-3 bg-surface-container hover:bg-emerald-500/10 group transition-all duration-300 rounded-xl active:scale-95 border-none cursor-pointer outline-none m-0 shadow-sm border border-transparent hover:border-emerald-500/20">\n                        <span class="material-symbols-outlined text-emerald-400 mb-1 group-hover:scale-110 duration-300 pointer-events-none" style="font-variation-settings: \'FILL\' 1;">check_circle</span>\n                        <span class="font-label text-[9px] sm:text-[10px] font-bold text-emerald-300 uppercase tracking-widest pointer-events-none">'
        yield escape(('Reviewed' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'Learned'))
        yield '</span>\n                    </button>\n                    <button id="mark-difficult-btn" class="flex flex-col items-center justify-center py-3 bg-surface-container hover:bg-orange-500/10 group transition-all duration-300 rounded-xl active:scale-95 border-none cursor-pointer outline-none m-0 shadow-sm border border-transparent hover:border-orange-500/20">\n                        <span class="material-symbols-outlined text-orange-400 mb-1 group-hover:scale-110 duration-300 pointer-events-none" style="font-variation-settings: \'FILL\' 1;">error</span>\n                        <span class="font-label text-[9px] sm:text-[10px] font-bold text-orange-300 uppercase tracking-widest pointer-events-none">Difficult</span>\n                    </button>\n                    '
        if (not (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode)):
            pass
            yield '\n                        <button id="already-known-btn" class="flex flex-col items-center justify-center py-3 sm:py-4 bg-surface-container hover:bg-primary/10 group transition-all duration-300 rounded-xl active:scale-95 border-none cursor-pointer outline-none m-0 shadow-sm border border-transparent hover:border-primary/20">\n                            <span class="material-symbols-outlined text-primary mb-1 group-hover:scale-110 duration-300 pointer-events-none" style="font-variation-settings: \'FILL\' 1;">visibility</span>\n                            <span class="font-label text-[9px] sm:text-[10px] font-bold text-primary uppercase tracking-widest pointer-events-none">Known</span>\n                        </button>\n                    '
        else:
            pass
            yield '\n                        <button disabled class="flex flex-col items-center justify-center py-3 sm:py-4 bg-surface-container/50 opacity-40 cursor-not-allowed rounded-xl border-none outline-none m-0">\n                            <span class="material-symbols-outlined text-outline mb-1 pointer-events-none" style="font-variation-settings: \'FILL\' 1;">visibility_off</span>\n                            <span class="font-label text-[9px] sm:text-[10px] font-bold text-outline uppercase tracking-widest pointer-events-none">Known</span>\n                        </button>\n                    '
        yield '\n                </div>\n                <div id="flashcard-status" class="text-center text-xs mt-4 text-[#dec38f] font-mono tracking-widest uppercase min-h-[1.5rem] flex items-center justify-center"></div>\n            </div>\n\n        </div>\n    '
    else:
        pass
        yield '\n        <div class="flex flex-col items-center justify-center h-full pt-32 w-full">\n            <div class="text-center py-16 px-8 max-w-sm bg-[#0d0f0f] rounded-2xl border border-white/[0.05] shadow-2xl relative overflow-hidden">\n                <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent"></div>\n                <span class="material-symbols-outlined text-6xl text-[#404848] mb-4 opacity-50 block relative z-10">task_alt</span>\n                <h2 class="text-xl font-bold font-headline text-on-surface tracking-tighter mb-2 relative z-10">All Caught Up</h2>\n                <p class="text-sm text-outline font-medium relative z-10 m-0">No more words to study right now.</p>\n                <div class="mt-8 relative z-10">\n                    <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
        yield '" class="inline-block bg-primary text-[#003735] px-6 py-2 rounded-full font-bold text-xs uppercase tracking-widest hover:brightness-110 active:scale-95 duration-200 border-none no-underline">Return to Dashboard</a>\n                </div>\n            </div>\n        </div>\n    '
    yield '\n\n    <!-- BottomNavBar - Contextual Visibility: Mobile only -->\n    <nav class="md:hidden fixed bottom-0 left-0 w-full grid grid-cols-4 items-center p-3 pb-safe bg-[#121414]/90 backdrop-blur-lg rounded-t-2xl z-50 border-t border-white/[0.05] shadow-[0_-10px_40px_rgba(0,0,0,0.3)] min-h-[5rem]">\n        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '" class="flex flex-col items-center justify-center text-[#8a9291] px-4 py-1 hover:text-primary transition-colors no-underline">\n            <span class="material-symbols-outlined mb-1" style="font-size: 1.5rem;">dashboard</span>\n            <span class="font-[\'Inter\'] text-[0.65rem] font-bold uppercase tracking-widest">Dashboard</span>\n        </a>\n        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '" class="flex flex-col items-center justify-center '
    yield escape(('bg-[#2d5f5d] text-[#9dd0cd] rounded-xl px-5 py-2 shadow-lg border border-[#9dd0cd]/20' if (not (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode)) else 'text-[#8a9291] px-4 py-1 hover:text-primary transition-colors'))
    yield ' no-underline">\n            <span class="material-symbols-outlined mb-1" style="font-size: 1.5rem;">school</span>\n            <span class="font-[\'Inter\'] text-[0.65rem] font-bold uppercase tracking-widest">Flashcards</span>\n        </a>\n        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '" class="flex flex-col items-center justify-center '
    yield escape(('bg-[#2d5f5d] text-[#9dd0cd] rounded-xl px-5 py-2 shadow-lg border border-[#9dd0cd]/20' if (undefined(name='review_mode') if l_0_review_mode is missing else l_0_review_mode) else 'text-[#8a9291] px-4 py-1 hover:text-primary transition-colors'))
    yield ' no-underline">\n            <span class="material-symbols-outlined mb-1" style="font-size: 1.5rem;">rule</span>\n            <span class="font-[\'Inter\'] text-[0.65rem] font-bold uppercase tracking-widest">Review</span>\n        </a>\n        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', _block_vars=_block_vars))
    yield '" class="flex flex-col items-center justify-center text-[#8a9291] px-4 py-1 hover:text-primary transition-colors no-underline">\n            <span class="material-symbols-outlined mb-1" style="font-size: 1.5rem;">quiz</span>\n            <span class="font-[\'Inter\'] text-[0.65rem] font-bold uppercase tracking-widest">Quiz</span>\n        </a>\n    </nav>\n\n</div>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=29&97=55&99=57&100=59&101=61&102=65&109=69&110=72&112=75&113=77&123=79&124=81&125=83&126=86&128=89&129=91&130=93&131=95&132=97&133=99&140=101&142=104&144=107&146=111&147=113&148=115&149=117&150=119&151=121&152=123&153=125&154=127&155=129&156=131&157=133&178=137&179=139&188=141&189=144&190=146&191=148&207=151&283=153&289=155&313=165&321=168&325=170&329=174&333=178'