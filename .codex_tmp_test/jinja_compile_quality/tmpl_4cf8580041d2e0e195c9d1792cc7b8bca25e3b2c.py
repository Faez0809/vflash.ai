from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'quiz.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'quiz.html')
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
    yield 'Quiz Mode | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_current_user = resolve('current_user')
    l_0_quiz_result = resolve('quiz_result')
    l_0_dashoffset = resolve('dashoffset')
    l_0_quiz_setup = resolve('quiz_setup')
    l_0_question = resolve('question')
    l_0_question_number = resolve('question_number')
    l_0_total_questions = resolve('total_questions')
    l_0_progress_pct = resolve('progress_pct')
    l_0_range = resolve('range')
    pass
    yield '\n<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;400;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>\n<style>\n    body.tw-dark-page {\n        background-color: #121414 !important;\n        color: #e2e2e2 !important;\n    }\n    .material-symbols-outlined {\n        font-variation-settings: \'FILL\' 0, \'wght\' 200, \'GRAD\' 0, \'opsz\' 24;\n    }\n    .tw-scope input, .tw-scope select, .tw-scope textarea {\n        color: #e2e2e2 !important;\n        background-color: transparent !important;\n    }\n    .page-shell { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }\n    .bg-quiz-gradient {\n        background: radial-gradient(circle at 50% 0%, rgba(157, 208, 205, 0.05) 0%, rgba(18, 20, 20, 0) 50%);\n    }\n    .glow-overlay {\n        background: radial-gradient(circle at 50% 50%, rgba(157, 208, 205, 0.08) 0%, transparent 70%);\n    }\n    .btn-stitch-glow {\n        background: linear-gradient(135deg, #9dd0cd 0%, #2d5f5d 100%) !important;\n        color: #00201f !important;\n        box-shadow: 0 8px 24px -4px rgba(157, 208, 205, 0.2) !important;\n        border: none !important;\n        transition: all 0.2s ease;\n    }\n    .btn-stitch-glow:hover {\n        filter: brightness(1.15) !important;\n        box-shadow: 0 12px 28px -4px rgba(157, 208, 205, 0.35) !important;\n    }\n    .btn-stitch-glow:active {\n        transform: scale(0.97) !important;\n    }\n    .btn-ghost-dark {\n        background: transparent !important;\n        border: 1px solid rgba(255,255,255,0.1) !important;\n        color: #8a9291 !important;\n        transition: all 0.2s ease;\n    }\n    .btn-ghost-dark:hover {\n        border-color: rgba(255,180,171,0.5) !important;\n        color: #ffb4ab !important;\n    }\n    .btn-ghost-neutral {\n        background: transparent !important;\n        border: 1px solid rgba(255,255,255,0.2) !important;\n        color: #e2e2e2 !important;\n        transition: all 0.2s ease;\n    }\n    .btn-ghost-neutral:hover {\n        background: rgba(255,255,255,0.05) !important;\n    }\n    .btn-danger-solid {\n        background: #93000a !important;\n        color: #ffdad6 !important;\n        border: none !important;\n        box-shadow: 0 4px 12px rgba(147, 0, 10, 0.2) !important;\n    }\n    .btn-danger-solid:hover {\n        background: #690005 !important;\n    }\n    .no-scrollbar::-webkit-scrollbar {\n        display: none;\n    }\n</style>\n<div class="tw-scope quiz-local-shell font-body antialiased bg-[#121414] min-h-screen text-[#e2e2e2] flex flex-col items-center">\n\n    <!-- Top Navigation Anchor (Shared) -->\n    <header class="bg-[#121414]/80 backdrop-blur-xl fixed top-0 w-full z-50 border-b border-white/[0.05] shadow-[0_48px_48px_-12px_rgba(45,95,93,0.04)]">\n        <div class="app-topbar-row flex justify-between items-center h-16 px-4 sm:px-6 w-full max-w-screen-2xl mx-auto font-headline tracking-tight gap-3 sm:gap-6">\n            <div class="app-topbar-brand-group flex items-center gap-4 sm:gap-8 min-w-0">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'index', _block_vars=_block_vars))
    yield '" class="text-2xl font-bold tracking-tighter text-primary no-underline">vflash.ai</a>\n                <nav class="hidden md:flex items-center gap-6 text-sm font-semibold pt-1">\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">Dashboard</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">My Words</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '">Flashcards</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">Review</a>\n                    <a class="text-primary border-b-2 border-primary pb-[0.2rem] no-underline" href="'
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
    yield '"><span class="material-symbols-outlined">logout</span><span>Sign Out</span></a>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </header>\n\n\n    '
    if (undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result):
        pass
        yield '\n        <!-- Quiz Result Screen -->\n        <main class="flex-1 flex items-center justify-center relative w-full pt-20 pb-12 md:pb-12 overflow-hidden max-h-screen">\n            <div class="absolute inset-0 glow-overlay pointer-events-none"></div>\n            <div class="relative z-10 w-full max-w-lg px-6 h-full flex flex-col justify-center">\n                <div class="bg-surface-container-low rounded-xl shadow-[0_48px_48px_rgba(157,208,205,0.04)] border border-white/5 overflow-hidden flex flex-col max-h-[calc(100vh-6rem)]">\n                    <div class="flex flex-col items-center text-center p-6 sm:p-10 overflow-y-auto no-scrollbar">\n                        <span class="font-headline font-bold text-[10px] tracking-[0.2em] text-primary mb-6 uppercase shrink-0">Quiz Result</span>\n                        \n                        <div class="relative w-40 h-40 shrink-0 flex items-center justify-center mb-6">\n                            <svg class="absolute inset-0 w-full h-full -rotate-90">\n                                <circle class="text-surface-container-highest" cx="80" cy="80" fill="transparent" r="72" stroke="currentColor" stroke-width="2"></circle>\n                                '
        l_0_dashoffset = (452.39 - (452.39 * ((environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'score') / environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'total_questions')) if (environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'total_questions') > 0) else 0)))
        _block_vars['dashoffset'] = l_0_dashoffset
        yield '\n                                <circle class="text-primary" cx="80" cy="80" fill="transparent" r="72" stroke="currentColor" stroke-dasharray="452.39" stroke-dashoffset="'
        yield escape((undefined(name='dashoffset') if l_0_dashoffset is missing else l_0_dashoffset))
        yield '" stroke-width="4"></circle>\n                            </svg>\n                            <div class="flex flex-col items-center mt-2">\n                                <span class="text-5xl font-headline font-extrabold text-on-surface tracking-tighter">'
        yield escape(environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'score'))
        yield '/'
        yield escape(environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'total_questions'))
        yield '</span>\n                                <span class="text-[9px] font-label text-on-surface-variant tracking-widest mt-1">TOTAL SCORE</span>\n                            </div>\n                        </div>\n\n                        <div class="mb-6 shrink-0">\n                            <h2 class="text-xl font-headline font-bold text-on-surface mb-2">\n                                '
        if (environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'accuracy') >= 90):
            pass
            yield 'Masterful!\n                                '
        elif (environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'accuracy') >= 70):
            pass
            yield 'Great work!\n                                '
        elif (environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'accuracy') >= 50):
            pass
            yield 'Good effort.\n                                '
        else:
            pass
            yield 'Keep practicing!'
        yield '\n                            </h2>\n                            <p class="text-xs sm:text-sm text-on-surface-variant max-w-xs leading-relaxed opacity-80">\n                                You are making steady progress. Your grasp of academic vocabulary is improving.\n                                '
        if environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'was_quit'):
            pass
            yield '<br><span class="text-error/80 text-xs">Quiz ended early</span>'
        yield '\n                            </p>\n                        </div>\n\n                        <div class="grid grid-cols-2 gap-4 w-full mb-8 shrink-0">\n                            <div class="bg-[#121414] border border-white/5 rounded-lg p-4 flex flex-col items-center transition-colors hover:bg-surface-bright">\n                                <span class="material-symbols-outlined text-primary/80 mb-2" data-icon="library_books">library_books</span>\n                                <span class="text-lg font-headline font-bold text-on-surface">'
        yield escape(environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'configured_total_questions'))
        yield '</span>\n                                <span class="text-[9px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">Target Qs</span>\n                            </div>\n                            <div class="bg-[#121414] border border-white/5 rounded-lg p-4 flex flex-col items-center transition-colors hover:bg-surface-bright">\n                                <span class="material-symbols-outlined text-primary/80 mb-2" data-icon="bolt">bolt</span>\n                                <span class="text-lg font-headline font-bold text-on-surface">'
        yield escape(environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'accuracy'))
        yield '%</span>\n                                <span class="text-[9px] font-bold text-on-surface-variant uppercase tracking-[0.1em]">Accuracy</span>\n                            </div>\n                        </div>\n\n                        '
        if ((environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'wrong_count') > 0) and environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'answers')):
            pass
            yield '\n                        <!-- Missed Questions Review Module -->\n                        <div class="w-full mb-8 shrink-0 border border-white/10 rounded-lg bg-[#0d0f0f] text-left overflow-hidden shadow-inner">\n                            <div class="p-4 border-b border-white/10 bg-white/5 flex justify-between items-center">\n                                <h3 class="text-sm font-bold text-on-surface">Missed Questions</h3>\n                                <span class="bg-error-container text-[#ffb4ab] text-[9px] uppercase tracking-[0.2em] px-2 py-1.5 rounded font-bold">'
            yield escape(environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'wrong_count'))
            yield ' '
            yield escape(('Error' if (environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'wrong_count') == 1) else 'Errors'))
            yield '</span>\n                            </div>\n                            <div class="p-4 space-y-4">\n                                '
            for l_1_answer in environment.getattr((undefined(name='quiz_result') if l_0_quiz_result is missing else l_0_quiz_result), 'answers'):
                _loop_vars = {}
                pass
                yield '\n                                    '
                if (not environment.getattr(l_1_answer, 'is_correct')):
                    pass
                    yield '\n                                    <div class="space-y-1.5 p-3 rounded-lg border border-white/5 bg-white/[0.02]">\n                                        <p class="text-[13px] font-semibold text-on-surface leading-normal opacity-90">'
                    yield escape(environment.getattr(l_1_answer, 'prompt'))
                    yield '</p>\n                                        <div class="flex flex-col gap-1 mt-2 p-2 bg-[#0d0f0f] rounded">\n                                            <p class="text-[11px] text-[#ffb4ab]/80 truncate"><strong class="opacity-80">You chose:</strong> <span class="line-through">'
                    yield escape(environment.getattr(l_1_answer, 'submitted'))
                    yield '</span></p>\n                                            <p class="text-[11px] text-primary"><strong class="opacity-80">Correct:</strong> <span class="font-medium">'
                    yield escape(environment.getattr(l_1_answer, 'correct'))
                    yield '</span></p>\n                                        </div>\n                                    </div>\n                                    '
                yield '\n                                '
            l_1_answer = missing
            yield '\n                            </div>\n                        </div>\n                        '
        yield '\n\n                        <div class="flex flex-col w-full gap-3 shrink-0 mt-auto">\n                            <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', reset=1, _block_vars=_block_vars))
        yield '" class="btn-stitch-glow w-full py-4 px-8 rounded-lg font-headline font-bold text-[13px] tracking-widest uppercase no-underline text-center">\n                                Start New Quiz\n                            </a>\n                            <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
        yield '" class="mt-4 text-xs font-bold text-on-surface-variant opacity-70 hover:opacity-100 hover:text-primary transition-colors flex items-center justify-center gap-2 no-underline uppercase tracking-wider">\n                                <span class="material-symbols-outlined text-sm" data-icon="arrow_back">arrow_back</span>\n                                Back to Dashboard\n                            </a>\n                        </div>\n                    </div>\n                </div>\n            </div>\n            <div class="absolute -top-12 -right-12 w-48 h-48 bg-primary opacity-[0.03] blur-[100px] rounded-full"></div>\n            <div class="absolute -bottom-12 -left-12 w-48 h-48 bg-primary opacity-[0.03] blur-[100px] rounded-full"></div>\n        </main>\n\n    '
    elif (undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup):
        pass
        yield '\n        <!-- Quiz Setup Screen -->\n        <main class="flex-1 flex items-center justify-center px-4 w-full h-[calc(100vh-4rem)] mt-16 pb-8 overflow-hidden">\n            <div class="fixed inset-0 pointer-events-none overflow-hidden opacity-[0.03]">\n                <div class="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary blur-[120px] rounded-full"></div>\n                <div class="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-primary-container blur-[120px] rounded-full"></div>\n            </div>\n\n            <div class="relative w-full max-w-2xl bg-surface-container-low rounded-xl border border-white/[0.05] shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">\n                <div class="p-8 md:p-12 overflow-y-auto no-scrollbar">\n                    '
        if (environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'has_resume') and environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'resume_progress')):
            pass
            yield '\n                    <div class="mb-10 p-6 bg-primary/10 border border-primary/20 rounded-lg flex flex-col sm:flex-row justify-between items-center gap-6">\n                        <div>\n                            <p class="text-[10px] font-bold tracking-[0.2em] text-primary uppercase mb-1 font-headline">Resume Quiz</p>\n                            <p class="text-sm text-on-surface-variant">You have an unfinished quiz in progress.</p>\n                            <p class="text-xs text-primary/80 mt-1 font-medium">Progress: '
            yield escape((environment.getattr(environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'resume_progress'), 'current_index') + 1))
            yield ' / '
            yield escape(environment.getattr(environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'resume_progress'), 'total_questions'))
            yield ' • Score: '
            yield escape(environment.getattr(environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'resume_progress'), 'score'))
            yield '</p>\n                        </div>\n                        <div class="flex gap-3 w-full sm:w-auto shrink-0">\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_start', _block_vars=_block_vars))
            yield '" class="btn-stitch-glow flex-1 sm:flex-none py-3 px-5 rounded font-bold text-xs shadow-lg text-center no-underline uppercase tracking-wider block leading-relaxed">Resume</a>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', reset=1, _block_vars=_block_vars))
            yield '" class="btn-ghost-neutral flex-1 sm:flex-none py-3 px-5 rounded font-bold text-xs text-center no-underline uppercase tracking-wider block leading-relaxed">Restart</a>\n                        </div>\n                    </div>\n                    '
        yield '\n\n                    <header class="mb-10 text-center md:text-left">\n                        <p class="text-[10px] font-bold tracking-[0.2em] text-primary uppercase mb-3 font-headline">QUIZ SETUP</p>\n                        <h1 class="text-3xl md:text-4xl font-headline font-extrabold text-on-surface tracking-tight mb-3">Build a focused quiz</h1>\n                        <p class="text-outline text-sm md:text-base max-w-md">Choose a source, level, and instruction to shape a more useful practice round.</p>\n                    </header>\n\n                    <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_start', _block_vars=_block_vars))
        yield '" class="space-y-8" data-async-page="true" data-loading-messages=\'["Preparing quiz...","Selecting questions...","Almost ready..."]\'>\n                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">\n                            <!-- Quiz Type -->\n                            <div class="space-y-2">\n                                <label for="quiz_type" class="text-[10px] font-bold text-outline tracking-[0.1em] uppercase ml-1 block">Quiz type</label>\n                                <div class="relative group">\n                                    <select id="quiz_type" name="quiz_type" class="w-full bg-[#0d0f0f] border border-white/10 text-on-surface rounded-lg px-4 py-3 appearance-none focus:border-primary/40 focus:ring-1 focus:ring-primary/40 transition-all outline-none text-sm font-medium">\n                                        '
        for (l_1_value, l_1_label) in environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'quiz_types'):
            _loop_vars = {}
            pass
            yield '\n                                            <option value="'
            yield escape(l_1_value)
            yield '" '
            yield escape(('selected' if (l_1_value == 'multiple_choice') else ''))
            yield '>'
            yield escape(l_1_label)
            yield '</option>\n                                        '
        l_1_value = l_1_label = missing
        yield '\n                                    </select>\n                                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-outline text-sm">expand_more</span>\n                                </div>\n                            </div>\n\n                            <!-- Word Source -->\n                            <div class="space-y-2">\n                                <label for="word_source" class="text-[10px] font-bold text-outline tracking-[0.1em] uppercase ml-1 block">Word source</label>\n                                <div class="relative group">\n                                    <select id="word_source" name="word_source" class="w-full bg-[#0d0f0f] border border-white/10 text-on-surface rounded-lg px-4 py-3 appearance-none focus:border-primary/40 focus:ring-1 focus:ring-primary/40 transition-all outline-none text-sm font-medium">\n                                        '
        for (l_1_value, l_1_label) in environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'word_sources'):
            _loop_vars = {}
            pass
            yield '\n                                            <option value="'
            yield escape(l_1_value)
            yield '" '
            yield escape(('selected' if (l_1_value == 'my_words') else ''))
            yield '>'
            yield escape(l_1_label)
            yield '</option>\n                                        '
        l_1_value = l_1_label = missing
        yield '\n                                    </select>\n                                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-outline text-sm">expand_more</span>\n                                </div>\n                            </div>\n\n                            <!-- Difficulty -->\n                            <div class="space-y-2">\n                                <label for="difficulty" class="text-[10px] font-bold text-outline tracking-[0.1em] uppercase ml-1 block">Difficulty</label>\n                                <div class="relative group">\n                                    <select id="difficulty" name="difficulty" class="w-full bg-[#0d0f0f] border border-white/10 text-on-surface rounded-lg px-4 py-3 appearance-none focus:border-primary/40 focus:ring-1 focus:ring-primary/40 transition-all outline-none text-sm font-medium">\n                                        '
        for l_1_value in environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'difficulty_options'):
            _loop_vars = {}
            pass
            yield '\n                                            <option value="'
            yield escape(l_1_value)
            yield '">'
            yield escape(l_1_value)
            yield '</option>\n                                        '
        l_1_value = missing
        yield '\n                                    </select>\n                                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-outline text-sm">expand_more</span>\n                                </div>\n                            </div>\n\n                            <!-- Number of Questions -->\n                            <div class="space-y-2">\n                                <label for="question_count" class="text-[10px] font-bold text-outline tracking-[0.1em] uppercase ml-1 block">Number of questions</label>\n                                <div class="relative group">\n                                    <select id="question_count" name="question_count" class="w-full bg-[#0d0f0f] border border-white/10 text-on-surface rounded-lg px-4 py-3 appearance-none focus:border-primary/40 focus:ring-1 focus:ring-primary/40 transition-all outline-none text-sm font-medium">\n                                        '
        for l_1_value in environment.getattr((undefined(name='quiz_setup') if l_0_quiz_setup is missing else l_0_quiz_setup), 'question_counts'):
            _loop_vars = {}
            pass
            yield '\n                                            <option value="'
            yield escape(l_1_value)
            yield '" '
            yield escape(('selected' if (l_1_value == 10) else ''))
            yield '>'
            yield escape(l_1_value)
            yield ' '
            yield escape(('Question' if (l_1_value == 1) else 'Questions'))
            yield '</option>\n                                        '
        l_1_value = missing
        yield '\n                                    </select>\n                                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-outline text-sm">expand_more</span>\n                                </div>\n                            </div>\n                        </div>\n\n                        <!-- Custom Instruction -->\n                        <div class="space-y-2">\n                            <label for="custom_quiz_instruction" class="text-[10px] font-bold text-outline tracking-[0.1em] uppercase ml-1 block">Custom quiz instruction (Optional)</label>\n                            <div class="ai-input-enhanced-shell">\n                                <textarea id="custom_quiz_instruction" name="custom_quiz_instruction" class="ai-input-enhanced ai-input-enhanced-textarea w-full min-h-[3.5rem] text-on-surface resize-y text-sm font-medium" placeholder="Describe how you want this quiz tailored..." rows="2"></textarea>\n                            </div>\n                        </div>\n\n                        <button type="submit" class="btn-stitch-glow w-full py-4 rounded-lg font-headline font-extrabold text-sm uppercase tracking-[0.2em] mt-6 flex items-center justify-center gap-2 cursor-pointer">\n                            Start Quiz\n                            <span class="material-symbols-outlined text-xl" data-icon="bolt">bolt</span>\n                        </button>\n                    </form>\n                </div>\n            </div>\n        </main>\n\n\n    '
    elif (undefined(name='question') if l_0_question is missing else l_0_question):
        pass
        yield '\n        <!-- Dynamic AJAX Wrapper -->\n        <div id="quiz-ajax-realm" class="flex flex-col items-center justify-center w-full min-h-screen">\n            <!-- Shared JS for the Quiz Interactivity -->\n            <script>\n                async function prefetchUpcomingQuizQuestions() {\n                    const prefetchUrl = "'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_prefetch', _block_vars=_block_vars))
        yield '";\n                    if (!prefetchUrl || window.quizPrefetchActive) {\n                        return;\n                    }\n\n                    window.quizPrefetchActive = true;\n                    try {\n                        await fetch(prefetchUrl, {\n                            method: \'POST\',\n                            headers: {\n                                \'X-Requested-With\': \'XMLHttpRequest\'\n                            }\n                        });\n                    } catch (err) {\n                        // Keep the quiz flow smooth even if prefetch is unavailable.\n                    } finally {\n                        window.quizPrefetchActive = false;\n                    }\n                }\n\n                function showQuitModal() {\n                    document.getElementById(\'quit-modal\').classList.remove(\'hidden\');\n                    document.getElementById(\'quit-modal\').classList.add(\'flex\');\n                }\n                function hideQuitModal() {\n                    document.getElementById(\'quit-modal\').classList.remove(\'flex\');\n                    document.getElementById(\'quit-modal\').classList.add(\'hidden\');\n                }\n\n                // Smooth AJAX submission for zero-flicker test taking!\n                function bindFastQuizForm() {\n                    const form = document.getElementById("quiz-question-form");\n                    if (!form) return;\n                    \n                    form.addEventListener("submit", async (e) => {\n                        e.preventDefault();\n                        \n                        // Interaction freeze state\n                        const subBtn = form.querySelector(\'button[type="submit"]\');\n                        if (subBtn) {\n                            subBtn.style.opacity = \'0.7\';\n                            subBtn.disabled = true;\n                        }\n                        \n                        try {\n                            const formData = new FormData(form);\n                            // Fast background fetch\n                            const response = await fetch(form.action, {\n                                method: \'POST\',\n                                body: formData,\n                            });\n                            \n                            // If python hits a final result redirect\n                            if (response.redirected && (response.url.includes("result=1") || response.url.includes("dashboard"))) {\n                                window.location.href = response.url;\n                                return;\n                            }\n                            \n                            // Otherwise inject the next fresh card instantly\n                            const html = await response.text();\n                            const parser = new DOMParser();\n                            const doc = parser.parseFromString(html, \'text/html\');\n                            \n                            const newRealm = doc.getElementById(\'quiz-ajax-realm\');\n                            if (newRealm) {\n                                document.getElementById(\'quiz-ajax-realm\').innerHTML = newRealm.innerHTML;\n                                bindFastQuizForm(); // Re-hook listeners\n                            } else {\n                                window.location.reload(); // Fallback\n                            }\n                        } catch (err) {\n                            window.location.reload();\n                        }\n                    });\n                }\n                \n                // Init on load\n                if (typeof window.quizFormBound === \'undefined\') {\n                    document.addEventListener("DOMContentLoaded", () => {\n                        bindFastQuizForm();\n                        prefetchUpcomingQuizQuestions();\n                    });\n                    window.quizFormBound = true;\n                } else {\n                    bindFastQuizForm();\n                    prefetchUpcomingQuizQuestions();\n                }\n            </script>\n\n            <!-- Dynamic Quit Quiz Modal -->\n            <div id="quit-modal" class="hidden fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm items-center justify-center p-4">\n                <div class="bg-surface-container-low border border-white/10 rounded-xl p-8 max-w-sm w-full shadow-2xl">\n                    <h3 class="text-xl font-headline font-bold text-on-surface mb-2">Quit session?</h3>\n                    <p class="text-sm text-outline mb-8">Your current progress and score will be evaluated on the result screen.</p>\n                    <div class="flex gap-4">\n                        <button onclick="hideQuitModal()" type="button" class="btn-ghost-neutral flex-1 py-3 px-4 text-xs font-bold rounded-lg cursor-pointer text-center">Resume</button>\n                        <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_start', _block_vars=_block_vars))
        yield '" class="flex-1 m-0 block">\n                            <input type="hidden" name="action" value="quit">\n                            <button type="submit" class="btn-danger-solid w-full py-3 px-4 text-xs font-bold rounded-lg cursor-pointer transition-all">End Quiz</button>\n                        </form>\n                    </div>\n                </div>\n            </div>\n\n            <!-- Single Page Quiz Canvas -->\n            <main class="min-h-[calc(100vh-4rem)] w-full flex items-center justify-center bg-quiz-gradient px-4 pt-4 sm:pt-8 overflow-y-auto relative">\n                <div class="w-full max-w-2xl relative z-10 flex flex-col justify-center py-2 sm:py-4">\n                    <div class="flex justify-between items-end mb-2 sm:mb-3 px-1 shrink-0">\n                        <div>\n                            <p class="text-primary text-[9px] sm:text-[10px] font-bold tracking-[0.2em] uppercase mb-0.5 font-headline">Session Progress</p>\n                            <h2 class="text-on-surface font-headline text-xl sm:text-2xl font-light">Question <span class="font-bold">'
        yield escape((undefined(name='question_number') if l_0_question_number is missing else l_0_question_number))
        yield '</span> / '
        yield escape((undefined(name='total_questions') if l_0_total_questions is missing else l_0_total_questions))
        yield '</h2>\n                        </div>\n                        <button type="button" onclick="showQuitModal()" class="btn-ghost-dark group flex items-center gap-1.5 text-[10px] sm:text-xs font-bold uppercase tracking-wider px-3 py-2 rounded-lg outline-none cursor-pointer">\n                            <span class="material-symbols-outlined text-[14px] sm:text-[16px]">close</span>\n                            Quit\n                        </button>\n                    </div>\n\n                    <div class="quiz-shell-focus bg-surface-container-low rounded-xl overflow-hidden shadow-2xl relative border border-white/5 flex flex-col max-h-[min(78vh,720px)] transition-opacity duration-200">\n                        <!-- Progress Bar -->\n                        <div class="absolute top-0 left-0 w-full h-1 bg-surface-container-highest shrink-0">\n                            '
        l_0_progress_pct = ((((undefined(name='question_number') if l_0_question_number is missing else l_0_question_number) - 1) / (undefined(name='total_questions') if l_0_total_questions is missing else l_0_total_questions)) * 100)
        _block_vars['progress_pct'] = l_0_progress_pct
        yield '\n                            '
        if ((undefined(name='progress_pct') if l_0_progress_pct is missing else l_0_progress_pct) == 0):
            pass
            l_0_progress_pct = 2
            _block_vars['progress_pct'] = l_0_progress_pct
        yield '\n                            <div class="h-full bg-primary shadow-[0_0_8px_rgba(157,208,205,0.4)] transition-all duration-700 ease-out" style="width: '
        yield escape((undefined(name='progress_pct') if l_0_progress_pct is missing else l_0_progress_pct))
        yield '%"></div>\n                        </div>\n                        \n                        <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_start', _block_vars=_block_vars))
        yield '" class="flex flex-col flex-1 overflow-hidden p-5 sm:p-8 m-0 pt-6 sm:pt-8" id="quiz-question-form">\n                            <!-- Instruction -->\n                            <div class="flex items-center gap-2 mb-3 sm:mb-4 shrink-0">\n                                <span class="h-[1px] w-6 bg-primary opacity-40"></span>\n                                <p class="text-primary text-[8px] sm:text-[9px] font-bold tracking-[0.2em] uppercase">'
        yield escape((environment.getattr((undefined(name='question') if l_0_question is missing else l_0_question), 'subtitle') or 'Select the correct answer'))
        yield '</p>\n                            </div>\n                            \n                            <!-- Target Word / Prompt -->\n                            <div class="mb-4 sm:mb-5 min-h-0 overflow-y-auto no-scrollbar pr-1">\n                                <h1 class="font-headline text-lg sm:text-xl md:text-2xl font-bold tracking-tight text-on-surface leading-snug mb-1 break-words">\n                                    '
        yield escape(environment.getattr((undefined(name='question') if l_0_question is missing else l_0_question), 'prompt'))
        yield '\n                                </h1>\n                            </div>\n                            \n                            <!-- Options Content Space -->\n                            <div class="w-full flex-1 min-h-0 mb-4 sm:mb-5 flex flex-col justify-center">\n                                <div class="space-y-2">\n                                    '
        if (environment.getattr((undefined(name='question') if l_0_question is missing else l_0_question), 'question_type') == 'fill_blank'):
            pass
            yield '\n                                        <div class="bg-[#0d0f0f] border border-white/10 rounded-lg p-2 focus-within:border-primary/40 focus-within:ring-1 focus-within:ring-primary/40 transition-all flex items-center mt-2">\n                                            <input id="answer" name="answer" type="text" required autocomplete="off" class="w-full bg-transparent border-none text-on-surface text-base md:text-lg font-medium outline-none p-3 placeholder:text-outline/30 box-border break-words" placeholder="Type your answer here..." autofocus>\n                                        </div>\n                                    '
        else:
            pass
            yield '\n                                        '
            for l_1_option in environment.getattr((undefined(name='question') if l_0_question is missing else l_0_question), 'options'):
                _loop_vars = {}
                pass
                yield '\n                                            <label class="group relative flex items-center p-2.5 sm:p-3 rounded-lg bg-[#0d0f0f] hover:bg-surface-bright cursor-pointer transition-all duration-200 border border-transparent hover:border-primary/20 m-0 w-full box-border">\n                                                <input type="radio" name="answer" value="'
                yield escape(l_1_option)
                yield '" required class="peer hidden" />\n                                                <div class="w-3.5 h-3.5 sm:w-4 sm:h-4 min-w-[0.875rem] sm:min-w-[1rem] rounded-full border border-outline-variant flex items-center justify-center group-hover:border-primary peer-checked:border-primary peer-checked:bg-primary transition-all mr-3">\n                                                    <div class="w-1.5 h-1.5 rounded-full bg-[#00201f] opacity-0 peer-checked:opacity-100"></div>\n                                                </div>\n                                                <span class="text-on-surface group-hover:text-primary transition-colors text-[13px] sm:text-sm font-medium leading-normal flex-1">'
                yield escape(l_1_option)
                yield '</span>\n                                            </label>\n                                        '
            l_1_option = missing
            yield '\n                                    '
        yield '\n                                </div>\n                            </div>\n\n                            <!-- Action Footer -->\n                            <div class="flex items-center justify-between pt-4 sm:pt-5 border-t border-white/5 shrink-0 mt-auto">\n                                <div class="flex gap-1.5">\n                                    '
        for l_1_i in context.call((undefined(name='range') if l_0_range is missing else l_0_range), 1, 6, _block_vars=_block_vars):
            _loop_vars = {}
            pass
            yield '\n                                        <div class="w-1.5 h-1.5 rounded-full '
            yield escape(('bg-primary' if (l_1_i <= (undefined(name='question_number') if l_0_question_number is missing else l_0_question_number)) else 'bg-surface-container-highest'))
            yield ' transition-colors"></div>\n                                    '
        l_1_i = missing
        yield '\n                                </div>\n                                <button type="submit" class="btn-stitch-glow px-5 sm:px-6 py-3 rounded-lg font-headline font-bold text-[10px] sm:text-[11px] tracking-[0.15em] uppercase cursor-pointer">\n                                    Submit Answer\n                                </button>\n                            </div>\n                        </form>\n                    </div>\n                </div>\n            </main>\n        </div>\n    '
    yield '\n\n</div>\n\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&78=46&80=48&81=50&82=52&83=54&84=56&91=58&92=61&94=64&95=66&105=68&106=70&107=72&108=75&110=78&111=80&112=82&113=84&114=86&115=88&123=90&135=93&136=96&139=98&146=102&147=105&148=108&153=115&160=119&165=121&170=123&175=126&178=130&179=134&181=137&183=139&184=141&194=147&197=149&209=151&219=154&224=157&227=163&228=165&239=168&246=170&247=174&259=182&260=186&272=194&273=198&285=204&286=208&312=218&318=221&414=223&428=225&439=229&440=232&441=237&444=239&448=241&454=243&461=245&466=251&468=255&472=257&482=262&483=266'