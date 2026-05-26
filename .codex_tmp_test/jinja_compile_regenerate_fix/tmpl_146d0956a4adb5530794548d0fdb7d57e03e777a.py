from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'dashboard.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'dashboard.html')
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
    yield 'Dashboard | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_display_name = resolve('display_name')
    l_0_current_user = resolve('current_user')
    l_0_db_fallback_active = resolve('db_fallback_active')
    l_0_last_session = resolve('last_session')
    l_0_last_session_remaining = resolve('last_session_remaining')
    l_0_words_to_review_today = resolve('words_to_review_today')
    l_0_curriculum_progress = resolve('curriculum_progress')
    l_0_recent_words = resolve('recent_words')
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
    try:
        t_4 = environment.filters['truncate']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'truncate' found.")
    try:
        t_5 = environment.filters['upper']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'upper' found.")
    pass
    yield '\n<section class="dashboard-page-wrap learning-home">\n    <header class="dashboard-topbar">\n        <div class="dashboard-topbar-main">\n            <div class="dashboard-topbar-brand">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">vflash.ai</a>\n            </div>\n            <form class="dashboard-topbar-search" action="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'search_word', _block_vars=_block_vars))
    yield '" method="get" data-async-page="true" data-loading-messages=\'["Searching...","Checking database...","Generating word details..."]\'>\n                <span class="material-symbols-outlined">search</span>\n                <input type="search" name="q" placeholder="Search any word, phrase, or topic" data-placeholder-full="Search any word, phrase, or topic" data-placeholder-compact="Search word, phrase, or topic" aria-label="Search any word, phrase, or topic" maxlength="60" autocomplete="off">\n            </form>\n            <div class="dashboard-topbar-actions">\n                <button type="button" class="dashboard-topbar-icon nav-chat-trigger" data-feedback-open-chat aria-label="Message Faez" title="Message Faez">\n                    <span class="feedback-fab-icon"><span class="material-symbols-outlined">forum</span></span>\n                </button>\n                <a class="dashboard-avatar" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '" aria-label="Profile">\n                    '
    yield escape(t_5((undefined(name='display_name') if l_0_display_name is missing else l_0_display_name)[:1]))
    yield '\n                </a>\n                <div class="nav-menu" data-nav-menu>\n                    <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                        <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                    </button>\n                    <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                        <span class="nav-menu-email">'
    yield escape((undefined(name='display_name') if l_0_display_name is missing else l_0_display_name))
    yield '</span>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person</span><span>Profile</span></a>\n                        '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
        pass
        yield '\n                        <a href="'
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
    yield '"><span class="material-symbols-outlined">logout</span><span>Sign Out</span></a>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </header>\n\n    <div class="dashboard-layout">\n        <aside class="dashboard-sidebar">\n            <div class="dashboard-sidebar-profile">\n                <div class="dashboard-sidebar-badge">\n                    <span class="material-symbols-outlined">book_2</span>\n                </div>\n                <div>\n                    <strong>'
    yield escape((undefined(name='display_name') if l_0_display_name is missing else l_0_display_name))
    yield '</strong>\n                    <span>Ready for today</span>\n                </div>\n            </div>\n\n            <nav class="dashboard-sidebar-nav">\n                <a class="is-active" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">dashboard</span>\n                    <span>Dashboard</span>\n                </a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">style</span>\n                    <span>Word Lists</span>\n                </a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">amp_stories</span>\n                    <span>Flashcards</span>\n                </a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">quiz</span>\n                    <span>Quiz</span>\n                </a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">rule</span>\n                    <span>Review</span>\n                </a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">person</span>\n                    <span>Profile</span>\n                </a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'logout', _block_vars=_block_vars))
    yield '">\n                    <span class="material-symbols-outlined">logout</span>\n                    <span>Sign Out</span>\n                </a>\n            </nav>\n            <div class="dashboard-sidebar-meta">\n                <div class="dashboard-sidebar-meta-title">vflash.ai</div>\n                <div>Vocabulary learning companion</div>\n            </div>\n        </aside>\n\n        <section class="dashboard-main learning-home-main">\n            <div class="learning-home-stack">\n                '
    if (undefined(name='db_fallback_active') if l_0_db_fallback_active is missing else l_0_db_fallback_active):
        pass
        yield '\n                <section class="learning-empty-state" style="border-color: rgba(255,180,171,0.35);">\n                    <span class="material-symbols-outlined">database_off</span>\n                    <p>Fallback database is active. Production users and progress may be unavailable until PostgreSQL reconnects.</p>\n                </section>\n                '
    yield '\n                <section class="learning-primary-actions" aria-label="Learning actions">\n                    <a class="learning-action-card learning-action-primary" href="'
    yield escape((context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards_session', session_id=environment.getattr((undefined(name='last_session') if l_0_last_session is missing else l_0_last_session), 'id'), _block_vars=_block_vars) if (undefined(name='last_session') if l_0_last_session is missing else l_0_last_session) else '#generate-section'))
    yield '">\n                        <span class="material-symbols-outlined">play_arrow</span>\n                        <div>\n                            <p>Continue Session</p>\n                            <h2>'
    yield escape(('Resume your set' if (undefined(name='last_session') if l_0_last_session is missing else l_0_last_session) else 'Begin learning'))
    yield '</h2>\n                            <small>\n                                '
    if (undefined(name='last_session') if l_0_last_session is missing else l_0_last_session):
        pass
        yield '\n                                    '
        yield escape((undefined(name='last_session_remaining') if l_0_last_session_remaining is missing else l_0_last_session_remaining))
        yield ' '
        yield escape(('word' if ((undefined(name='last_session_remaining') if l_0_last_session_remaining is missing else l_0_last_session_remaining) == 1) else 'words'))
        yield ' remaining\n                                '
    else:
        pass
        yield '\n                                    Start with a clean curated set\n                                '
    yield '\n                            </small>\n                        </div>\n                    </a>\n\n                    <a class="learning-action-card" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">\n                        <span class="material-symbols-outlined">history</span>\n                        <div>\n                            <p>Review Due</p>\n                            <h2>'
    yield escape((undefined(name='words_to_review_today') if l_0_words_to_review_today is missing else l_0_words_to_review_today))
    yield ' '
    yield escape(('word' if ((undefined(name='words_to_review_today') if l_0_words_to_review_today is missing else l_0_words_to_review_today) == 1) else 'words'))
    yield '</h2>\n                            <small>'
    yield escape(('Waiting for you' if (undefined(name='words_to_review_today') if l_0_words_to_review_today is missing else l_0_words_to_review_today) else 'Nothing urgent today'))
    yield '</small>\n                        </div>\n                    </a>\n\n                    <a class="learning-action-card" href="#generate-section">\n                        <span class="material-symbols-outlined">school</span>\n                        <div>\n                            <p>Start Practice</p>\n                            <h2>Choose a level</h2>\n                            <small>Curated words, no prompt needed</small>\n                        </div>\n                    </a>\n                </section>\n\n                <section class="learning-practice-panel" id="generate-section">\n                    <div class="learning-panel-head">\n                        <div>\n                            <p class="learning-eyebrow">Start Practice</p>\n                            <h1>Your next words are ready.</h1>\n                        </div>\n                        <span class="material-symbols-outlined">auto_stories</span>\n                    </div>\n                    <form method="post" action="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'generate_words', _block_vars=_block_vars))
    yield '" class="learning-practice-form" data-async-page="true" data-loading-messages=\'["Selecting unseen words...","Preparing examples...","Opening your session..."]\'>\n                        <label>\n                            <span>Level</span>\n                            <select id="difficulty" name="difficulty" aria-label="Difficulty">\n                                <option value="intermediate" selected>Intermediate</option>\n                                <option value="upper_intermediate">Upper Intermediate</option>\n                                <option value="advanced">Advanced</option>\n                            </select>\n                        </label>\n                        <label>\n                            <span>Count</span>\n                            <select id="word_count" name="word_count" aria-label="Number of words">\n                                <option value="5" selected>5 words</option>\n                                <option value="10">10 words</option>\n                            </select>\n                        </label>\n                        <label>\n                            <span>Mode</span>\n                            <select id="order_mode" name="order_mode" aria-label="Order mode">\n                                <option value="mixed" selected>Mixed</option>\n                                <option value="alphabetical">Alphabetical</option>\n                            </select>\n                        </label>\n                        <button type="submit">Start</button>\n                    </form>\n                </section>\n\n                <section class="learning-levels-panel">\n                    <div class="learning-section-head">\n                        <div>\n                            <p class="learning-eyebrow">Curriculum</p>\n                            <h2>Explore level by level</h2>\n                        </div>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '">More stats</a>\n                    </div>\n                    <div class="learning-level-list">\n                        '
    for l_1_item in (undefined(name='curriculum_progress') if l_0_curriculum_progress is missing else l_0_curriculum_progress):
        l_1_explored = l_1_total = l_1_explored_percent = missing
        _loop_vars = {}
        pass
        yield '\n                            '
        l_1_explored = environment.getattr(l_1_item, 'generated')
        _loop_vars['explored'] = l_1_explored
        yield '\n                            '
        l_1_total = environment.getattr(l_1_item, 'total_words')
        _loop_vars['total'] = l_1_total
        yield '\n                            '
        l_1_explored_percent = ((((undefined(name='explored') if l_1_explored is missing else l_1_explored) / (undefined(name='total') if l_1_total is missing else l_1_total)) * 100) if (undefined(name='total') if l_1_total is missing else l_1_total) else 0)
        _loop_vars['explored_percent'] = l_1_explored_percent
        yield '\n                            <article class="learning-level-row">\n                                <div>\n                                    <strong>'
        yield escape(t_3(t_1(context.eval_ctx, environment.getattr(l_1_item, 'label'), '_', ' ')))
        yield '</strong>\n                                    <span>'
        yield escape((undefined(name='explored') if l_1_explored is missing else l_1_explored))
        yield ' explored of '
        yield escape((undefined(name='total') if l_1_total is missing else l_1_total))
        yield ' words</span>\n                                </div>\n                                <div class="learning-level-meter" aria-label="'
        yield escape(environment.getattr(l_1_item, 'label'))
        yield ' explored '
        yield escape(t_2((undefined(name='explored_percent') if l_1_explored_percent is missing else l_1_explored_percent), 1))
        yield ' percent">\n                                    <span style="width: '
        yield escape(t_2((undefined(name='explored_percent') if l_1_explored_percent is missing else l_1_explored_percent), 1))
        yield '%;"></span>\n                                </div>\n                                <small>'
        yield escape(environment.getattr(l_1_item, 'unseen_remaining'))
        yield ' unseen</small>\n                            </article>\n                        '
    l_1_item = l_1_explored = l_1_total = l_1_explored_percent = missing
    yield '\n                    </div>\n                </section>\n\n                <section class="learning-recent-panel">\n                    <div class="learning-section-head">\n                        <div>\n                            <p class="learning-eyebrow">Recent Words</p>\n                            <h2>Fresh in your path</h2>\n                        </div>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">View all</a>\n                    </div>\n                    <div class="learning-recent-list">\n                        '
    t_6 = 1
    for l_1_item in (undefined(name='recent_words') if l_0_recent_words is missing else l_0_recent_words)[:4]:
        _loop_vars = {}
        pass
        yield '\n                            <article class="learning-recent-item">\n                                <div>\n                                    <strong>'
        yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'word'))
        yield '</strong>\n                                    <p>'
        yield escape(t_4(environment, environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'meaning'), 70, True, '...'))
        yield '</p>\n                                </div>\n                                <span>'
        yield escape(t_3(t_1(context.eval_ctx, environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'difficulty'), '_', ' ')))
        yield '</span>\n                            </article>\n                        '
        t_6 = 0
    l_1_item = missing
    if t_6:
        pass
        yield '\n                            <div class="learning-empty-state">\n                                <span class="material-symbols-outlined">local_library</span>\n                                <p>Your recent words will appear here after your first session.</p>\n                            </div>\n                        '
    yield '\n                    </div>\n                </section>\n            </div>\n        </section>\n    </div>\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&10=75&12=77&20=79&21=81&28=83&29=85&30=87&31=90&33=93&34=95&35=97&36=99&37=101&38=103&52=105&58=107&62=109&66=111&70=113&74=115&78=117&82=119&95=121&102=125&106=127&108=129&109=132&117=140&121=142&122=146&144=148&177=150&180=152&181=157&182=160&183=163&186=166&187=168&189=172&190=176&192=178&204=182&207=185&210=189&211=191&213=193'