from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'profile.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'profile.html')
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
    yield 'Profile | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_current_user = resolve('current_user')
    l_0_total_learned = resolve('total_learned')
    l_0_total_generated = resolve('total_generated')
    l_0_overall_completion = resolve('overall_completion')
    l_0_study_streak = resolve('study_streak')
    l_0_curriculum_progress = resolve('curriculum_progress')
    l_0_total_sessions = resolve('total_sessions')
    l_0_total_words = resolve('total_words')
    l_0_latest_quiz = resolve('latest_quiz')
    l_0_quiz_metrics = resolve('quiz_metrics')
    l_0_usage_metrics = resolve('usage_metrics')
    l_0_weekly_activity = resolve('weekly_activity')
    try:
        t_1 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_2 = environment.filters['round']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'round' found.")
    try:
        t_3 = environment.filters['title']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'title' found.")
    pass
    yield '\n<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>\n<style>\n    body.tw-dark-page {\n        background-color: #121414 !important;\n        color: #e2e2e2 !important;\n    }\n    .material-symbols-outlined {\n        font-variation-settings: \'FILL\' 0, \'wght\' 300, \'GRAD\' 0, \'opsz\' 24;\n    }\n    .tw-scope input, .tw-scope select, .tw-scope textarea {\n        color: #e2e2e2 !important;\n        background-color: transparent !important;\n    }\n    .page-shell { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }\n    .no-scrollbar::-webkit-scrollbar {\n        display: none;\n    }\n</style>\n<div class="tw-scope font-body antialiased bg-[#121414] min-h-screen text-[#e2e2e2]">\n    <header class="bg-[#121414]/80 backdrop-blur-xl fixed top-0 w-full z-50 border-b border-white/[0.05] shadow-lg">\n        <div class="app-topbar-row flex justify-between items-center h-16 px-4 sm:px-6 max-w-screen-2xl mx-auto font-headline tracking-tight gap-3 sm:gap-6">\n            <div class="app-topbar-brand-group flex items-center gap-4 sm:gap-8 min-w-0">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'index', _block_vars=_block_vars))
    yield '" class="text-2xl font-bold tracking-tighter text-primary no-underline">vflash.ai</a>\n                <nav class="hidden md:flex items-center gap-6 text-sm font-semibold pt-1">\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">Dashboard</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">My Words</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '">Flashcards</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">Review</a>\n                    <a class="text-primary/60 hover:text-primary transition-all no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', _block_vars=_block_vars))
    yield '">Quiz</a>\n                    <a class="text-primary border-b-2 border-primary pb-[0.2rem] no-underline" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '">Profile</a>\n                </nav>\n            </div>\n            <div class="app-topbar-actions flex items-center gap-4">\n                <button type="button" class="nav-chat-trigger nav-header-icon" data-feedback-open-chat aria-label="Message Faez" title="Message Faez">\n                    <span class="feedback-fab-icon"><span class="material-symbols-outlined">forum</span></span>\n                </button>\n                '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
        pass
        yield '\n                    <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', _block_vars=_block_vars))
        yield '" class="hidden md:inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-[0.72rem] font-bold uppercase tracking-[0.18em] text-primary no-underline transition-all hover:bg-primary/15 hover:brightness-110">Admin Panel</a>\n                '
    yield '\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '" class="flex items-center gap-3 text-primary no-underline hover:brightness-125 transition-all outline-none">\n                    <span class="text-sm font-semibold tracking-wide hidden sm:block">'
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
    yield '"><span class="material-symbols-outlined">logout</span><span>Sign Out</span></a>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </header>\n\n    <main class="pt-24 pb-12 px-4 sm:px-6 max-w-screen-2xl mx-auto">\n        <section class="mb-8">\n            <div class="rounded-3xl border border-white/[0.05] bg-[radial-gradient(circle_at_top,rgba(157,208,205,0.12),transparent_40%),linear-gradient(180deg,rgba(30,32,32,0.98),rgba(18,20,20,0.98))] p-6 md:p-8 shadow-[0_48px_48px_-12px_rgba(45,95,93,0.16)]">\n                <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-3">Profile</p>\n                <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">\n                    <div class="max-w-2xl">\n                        <h1 class="font-headline text-3xl md:text-5xl font-extrabold tracking-tight text-on-surface mb-0">Your learning progress and settings.</h1>\n                    </div>\n                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 min-w-[280px]">\n                        <div class="rounded-2xl border border-white/[0.06] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Learned</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape((undefined(name='total_learned') if l_0_total_learned is missing else l_0_total_learned))
    yield '</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.06] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Explored</p>\n                            <strong class="text-2xl font-headline text-primary">'
    yield escape((undefined(name='total_generated') if l_0_total_generated is missing else l_0_total_generated))
    yield '</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.06] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Completion</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape((undefined(name='overall_completion') if l_0_overall_completion is missing else l_0_overall_completion))
    yield '%</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.06] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Streak</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape((undefined(name='study_streak') if l_0_study_streak is missing else l_0_study_streak))
    yield '</strong>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </section>\n\n        <section class="grid grid-cols-1 xl:grid-cols-[1.1fr_1.4fr] gap-6 items-start">\n            <div class="space-y-6">\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Curriculum</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Level Progress</h2>\n                    </div>\n                    <div class="space-y-4">\n                        '
    for l_1_item in (undefined(name='curriculum_progress') if l_0_curriculum_progress is missing else l_0_curriculum_progress):
        l_1_explored_percent = missing
        _loop_vars = {}
        pass
        yield '\n                            '
        l_1_explored_percent = (((environment.getattr(l_1_item, 'generated') / environment.getattr(l_1_item, 'total_words')) * 100) if environment.getattr(l_1_item, 'total_words') else 0)
        _loop_vars['explored_percent'] = l_1_explored_percent
        yield '\n                            <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                                <div class="flex items-center justify-between gap-4 mb-3">\n                                    <div>\n                                        <strong class="font-headline text-lg text-on-surface">'
        yield escape(t_3(t_1(context.eval_ctx, environment.getattr(l_1_item, 'label'), '_', ' ')))
        yield '</strong>\n                                        <p class="text-xs text-on-surface-variant mt-1 mb-0">'
        yield escape(environment.getattr(l_1_item, 'learned'))
        yield ' learned · '
        yield escape(environment.getattr(l_1_item, 'generated'))
        yield ' explored · '
        yield escape(environment.getattr(l_1_item, 'unseen_remaining'))
        yield ' unseen</p>\n                                    </div>\n                                    <span class="text-sm font-bold text-primary">'
        yield escape(environment.getattr(l_1_item, 'completion'))
        yield '%</span>\n                                </div>\n                                <div class="h-2 rounded-full bg-white/10 overflow-hidden">\n                                    <span class="block h-full rounded-full bg-gradient-to-r from-primary to-secondary" style="width: '
        yield escape(t_2((undefined(name='explored_percent') if l_1_explored_percent is missing else l_1_explored_percent), 1))
        yield '%;"></span>\n                                </div>\n                            </article>\n                        '
    l_1_item = l_1_explored_percent = missing
    yield '\n                    </div>\n                </section>\n\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Account</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Snapshot</h2>\n                    </div>\n                    <dl class="space-y-4">\n                        <div class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <dt class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Nickname</dt>\n                            <dd class="m-0 text-lg text-on-surface font-semibold">'
    yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))
    yield '</dd>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <dt class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Email</dt>\n                            <dd class="m-0 text-sm md:text-base text-on-surface break-all">'
    yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'email'))
    yield '</dd>\n                        </div>\n                        <div class="grid grid-cols-2 gap-4">\n                            <div class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                                <dt class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Study Sessions</dt>\n                                <dd class="m-0 text-2xl font-headline text-on-surface">'
    yield escape((undefined(name='total_sessions') if l_0_total_sessions is missing else l_0_total_sessions))
    yield '</dd>\n                            </div>\n                            <div class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                                <dt class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Saved Words</dt>\n                                <dd class="m-0 text-2xl font-headline text-on-surface">'
    yield escape((undefined(name='total_words') if l_0_total_words is missing else l_0_total_words))
    yield '</dd>\n                            </div>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <dt class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Latest Quiz</dt>\n                            <dd class="m-0 text-sm md:text-base text-on-surface">\n                                '
    if (undefined(name='latest_quiz') if l_0_latest_quiz is missing else l_0_latest_quiz):
        pass
        yield '\n                                    '
        yield escape(environment.getattr((undefined(name='latest_quiz') if l_0_latest_quiz is missing else l_0_latest_quiz), 'score'))
        yield '/'
        yield escape((environment.getattr((undefined(name='latest_quiz') if l_0_latest_quiz is missing else l_0_latest_quiz), 'answered_questions') or environment.getattr((undefined(name='latest_quiz') if l_0_latest_quiz is missing else l_0_latest_quiz), 'total_questions')))
        yield '\n                                    '
        if environment.getattr((undefined(name='latest_quiz') if l_0_latest_quiz is missing else l_0_latest_quiz), 'was_quit'):
            pass
            yield '<span class="text-[#ffb4ab]">(quit)</span>'
        yield '\n                                    on '
        yield escape(context.call(environment.getattr(environment.getattr((undefined(name='latest_quiz') if l_0_latest_quiz is missing else l_0_latest_quiz), 'created_at'), 'strftime'), '%Y-%m-%d', _block_vars=_block_vars))
        yield '\n                                '
    else:
        pass
        yield '\n                                    No quiz yet\n                                '
    yield '\n                            </dd>\n                        </div>\n                    </dl>\n                </section>\n\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Quiz</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Performance</h2>\n                    </div>\n                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Visits</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'total_attempts'))
    yield '</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Completed</p>\n                            <strong class="text-2xl font-headline text-primary">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'completed_attempts'))
    yield '</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Quit</p>\n                            <strong class="text-2xl font-headline text-[#ffb4ab]">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'quit_attempts'))
    yield '</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Accuracy</p>\n                            <strong class="text-2xl font-headline text-primary">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'accuracy'))
    yield '%</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Completion Rate</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'completion_rate'))
    yield '%</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Best Completed Score</p>\n                            <strong class="text-2xl font-headline text-secondary">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'best_score'))
    yield '/'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'best_total'))
    yield '</strong>\n                        </article>\n                    </div>\n                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">\n                        <div class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Correct Answers</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'correct_answers'))
    yield '</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Answered Questions</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'answered_questions'))
    yield '</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Questions Seen</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='quiz_metrics') if l_0_quiz_metrics is missing else l_0_quiz_metrics), 'configured_questions'))
    yield '</strong>\n                        </div>\n                    </div>\n                    <p class="text-xs text-on-surface-variant mt-4 mb-0">Quit quizzes are tracked, but not included in accuracy.</p>\n                </section>\n\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Usage</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">App Activity</h2>\n                    </div>\n                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Active Time</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'total_active_minutes'))
    yield 'm</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Visits</p>\n                            <strong class="text-2xl font-headline text-primary">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'total_visits'))
    yield '</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-[#0d0f0f] p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Active Days</p>\n                            <strong class="text-2xl font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'active_days'))
    yield '</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Avg / Visit</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'average_active_minutes'))
    yield 'm</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Page Views</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'total_page_views'))
    yield '</strong>\n                        </article>\n                        <article class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Last 7 Days</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'visits_last_7_days'))
    yield '</strong>\n                        </article>\n                    </div>\n                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">\n                        <div class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Longest Session</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'longest_session_minutes'))
    yield 'm</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Interactions</p>\n                            <strong class="text-lg font-headline text-on-surface">'
    yield escape(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'total_interactions'))
    yield '</strong>\n                        </div>\n                        <div class="rounded-2xl border border-white/[0.05] bg-black/20 p-4">\n                            <p class="text-[10px] uppercase tracking-[0.18em] text-outline font-bold mb-2">Last Seen</p>\n                            <strong class="text-sm font-headline text-on-surface">\n                                '
    if environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'last_seen_at'):
        pass
        yield '\n                                    '
        yield escape(context.call(environment.getattr(environment.getattr((undefined(name='usage_metrics') if l_0_usage_metrics is missing else l_0_usage_metrics), 'last_seen_at'), 'strftime'), '%Y-%m-%d %H:%M', _block_vars=_block_vars))
        yield '\n                                '
    else:
        pass
        yield '\n                                    No tracked activity yet\n                                '
    yield '\n                            </strong>\n                        </div>\n                    </div>\n                    <p class="text-xs text-on-surface-variant mt-4 mb-0">Only active use is counted. Background tabs do not add time.</p>\n                </section>\n\n                <section class="profile-weekly-activity-mobile rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Activity</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Weekly Activity</h2>\n                    </div>\n                    <div class="dashboard-stitch-bars mini-chart-bars">\n                        '
    for l_1_item in (undefined(name='weekly_activity') if l_0_weekly_activity is missing else l_0_weekly_activity):
        _loop_vars = {}
        pass
        yield '\n                            <div class="dashboard-stitch-bar-col">\n                                <div class="dashboard-stitch-bar-track">\n                                    <div class="dashboard-stitch-bar" style="height: '
        yield escape((environment.getattr(l_1_item, 'height') * 0.6))
        yield 'px;"></div>\n                                </div>\n                                <span class="dashboard-chart-label">'
        yield escape(environment.getattr(l_1_item, 'label')[:1])
        yield '</span>\n                            </div>\n                        '
    l_1_item = missing
    yield '\n                    </div>\n                </section>\n            </div>\n\n            <div class="space-y-6">\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Help</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Learning Support</h2>\n                        <p class="mt-2 mb-0 text-sm text-on-surface-variant">Find the guide, adjust your settings, or jump to admin tools if your account has access.</p>\n                    </div>\n                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'user_manual', _block_vars=_block_vars))
    yield '" class="rounded-2xl border border-white/[0.06] bg-[#0d0f0f] p-4 no-underline text-on-surface">\n                            <span class="material-symbols-outlined text-primary mb-2">menu_book</span>\n                            <strong class="block">Open User Guide</strong>\n                            <small class="text-on-surface-variant">Quick help for study, review, and quiz.</small>\n                        </a>\n                        '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
        pass
        yield '\n                        <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', _block_vars=_block_vars))
        yield '" class="rounded-2xl border border-primary/20 bg-primary/10 p-4 no-underline text-on-surface">\n                            <span class="material-symbols-outlined text-primary mb-2">shield_person</span>\n                            <strong class="block">Admin Panel</strong>\n                            <small class="text-on-surface-variant">Manage users and enrichment quality.</small>\n                        </a>\n                        '
    yield '\n                    </div>\n                </section>\n\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Defaults</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Study Settings</h2>\n                    </div>\n                    <form method="post" class="space-y-5">\n                        <input type="hidden" name="action" value="profile">\n                        <div class="space-y-2">\n                            <label for="nickname" class="text-[10px] font-bold text-outline tracking-[0.18em] uppercase block">Nickname</label>\n                            <input id="nickname" name="nickname" type="text" maxlength="80" value="'
    yield escape((environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'nickname') or environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name')))
    yield '" class="w-full bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-2xl px-4 py-3.5 text-sm text-on-surface outline-none box-border">\n                        </div>\n\n                        <div class="space-y-2">\n                            <label for="daily_goal" class="text-[10px] font-bold text-outline tracking-[0.18em] uppercase block">Daily Goal</label>\n                            <input id="daily_goal" name="daily_goal" type="number" min="1" max="100" value="'
    yield escape((environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'daily_goal') or 10))
    yield '" class="w-full bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-2xl px-4 py-3.5 text-sm text-on-surface outline-none box-border">\n                        </div>\n\n                        <button type="submit" class="w-full bg-gradient-to-r from-primary to-primary-container text-[#00201f] px-6 py-4 rounded-2xl font-headline font-extrabold text-sm uppercase tracking-[0.18em] hover:brightness-110 active:scale-[0.99] duration-200 border-none cursor-pointer">Save Profile</button>\n                    </form>\n                </section>\n\n                <section class="rounded-3xl border border-white/[0.05] bg-surface-container-low p-6 shadow-2xl">\n                    <div class="mb-4">\n                        <p class="text-[10px] font-bold tracking-[0.22em] text-primary uppercase mb-2">Security</p>\n                        <h2 class="font-headline text-2xl font-extrabold tracking-tight text-on-surface mb-0">Change Password</h2>\n                        <p class="mt-2 mb-0 text-sm text-on-surface-variant">Update your password here. Your account will stay signed in on this device after the change.</p>\n                    </div>\n                    <form method="post" class="space-y-5">\n                        <input type="hidden" name="action" value="password">\n                        <div class="space-y-2">\n                            <label for="current_password" class="text-[10px] font-bold text-outline tracking-[0.18em] uppercase block">Current Password</label>\n                            <input id="current_password" name="current_password" type="password" autocomplete="current-password" required class="w-full bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-2xl px-4 py-3.5 text-sm text-on-surface outline-none box-border">\n                        </div>\n                        <div class="space-y-2">\n                            <label for="new_password" class="text-[10px] font-bold text-outline tracking-[0.18em] uppercase block">New Password</label>\n                            <input id="new_password" name="new_password" type="password" minlength="8" autocomplete="new-password" required class="w-full bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-2xl px-4 py-3.5 text-sm text-on-surface outline-none box-border">\n                        </div>\n                        <div class="space-y-2">\n                            <label for="confirm_password" class="text-[10px] font-bold text-outline tracking-[0.18em] uppercase block">Confirm New Password</label>\n                            <input id="confirm_password" name="confirm_password" type="password" minlength="8" autocomplete="new-password" required class="w-full bg-[#0d0f0f] border border-white/10 focus:border-primary/40 focus:ring-1 focus:ring-primary/40 rounded-2xl px-4 py-3.5 text-sm text-on-surface outline-none box-border">\n                        </div>\n\n                        <button type="submit" class="w-full bg-gradient-to-r from-secondary to-primary text-[#1f1708] px-6 py-4 rounded-2xl font-headline font-extrabold text-sm uppercase tracking-[0.18em] hover:brightness-110 active:scale-[0.99] duration-200 border-none cursor-pointer">Update Password</button>\n                    </form>\n                </section>\n            </div>\n        </section>\n    </main>\n</div>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&28=67&30=69&31=71&32=73&33=75&34=77&35=79&42=81&43=84&45=87&46=89&56=91&57=93&58=95&59=98&61=101&62=103&63=105&64=107&65=109&66=111&84=113&88=115&92=117&96=119&111=121&112=126&116=129&117=131&119=137&122=139&137=143&141=145&146=147&150=149&156=151&157=154&158=158&159=162&176=168&180=170&184=172&188=174&192=176&196=178&202=182&206=184&210=186&224=188&228=190&232=192&236=194&240=196&244=198&250=200&254=202&259=204&260=207&276=213&279=217&281=219&296=223&301=225&302=228&320=231&325=233'