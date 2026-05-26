from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'admin_dashboard.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'admin_dashboard.html')
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
    yield 'Admin Panel | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_admin_email = resolve('admin_email')
    l_0_admin_summary = resolve('admin_summary')
    l_0_db_health = resolve('db_health')
    l_0_enrichment_total = resolve('enrichment_total')
    l_0_enrichment_q = resolve('enrichment_q')
    l_0_enrichment_rows = resolve('enrichment_rows')
    l_0_enrichment_page = resolve('enrichment_page')
    l_0_review_flag_total = resolve('review_flag_total')
    l_0_review_flags = resolve('review_flags')
    l_0_flag_page = resolve('flag_page')
    l_0_flag_status = resolve('flag_status')
    l_0_flag_type = resolve('flag_type')
    l_0_user_total = resolve('user_total')
    l_0_user_rows = resolve('user_rows')
    l_0_user_page = resolve('user_page')
    l_0_dh = l_0_dh_counts = l_0_dh_missing_tables = l_0_dh_warnings = missing
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_2 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_3 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_4 = environment.filters['title']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'title' found.")
    pass
    yield '\n<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>\n<style>\n    .page-shell { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }\n    .no-scrollbar::-webkit-scrollbar { display: none; }\n</style>\n<div class="tw-scope admin-shell min-h-screen bg-[#121414] text-[#e2e2e2] font-[\'Inter\']">\n    <header class="sticky top-0 z-40 border-b border-white/5 bg-[#121414]/90 backdrop-blur-xl">\n        <div class="max-w-screen-2xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">\n            <div>\n                <p class="text-[10px] uppercase tracking-[0.22em] text-[#9dd0cd] font-bold mb-1">Admin Panel</p>\n                <h1 class="font-[\'Manrope\'] text-2xl font-extrabold tracking-tight">vflash.ai control center</h1>\n            </div>\n            <div class="flex items-center gap-3">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '" class="rounded-2xl border border-white/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-[#e2e2e2] no-underline">Return to User Dashboard</a>\n                <span class="hidden md:block text-sm text-[#c0c8c7]">'
    yield escape((undefined(name='admin_email') if l_0_admin_email is missing else l_0_admin_email))
    yield '</span>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '" class="nav-profile-link" aria-label="Profile">\n                    <span class="nav-profile-name">Admin</span>\n                    <span class="nav-profile-avatar" aria-hidden="true">A</span>\n                </a>\n                <div class="nav-menu" data-nav-menu>\n                    <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                        <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                    </button>\n                    <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                        <span class="nav-menu-email">'
    yield escape((undefined(name='admin_email') if l_0_admin_email is missing else l_0_admin_email))
    yield '</span>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">dashboard</span><span>User Dashboard</span></a>\n                        <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_logout', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">logout</span><span>Logout</span></a>\n                    </div>\n                </div>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_logout', _block_vars=_block_vars))
    yield '" class="rounded-2xl border border-white/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-[#e2e2e2] no-underline">Logout</a>\n            </div>\n        </div>\n    </header>\n\n    <main class="max-w-screen-2xl mx-auto px-4 sm:px-6 py-6 sm:py-8">\n        <section class="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-4 mb-6">\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Users</p>\n                <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'total_users'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Restricted</p>\n                <strong class="font-[\'Manrope\'] text-3xl text-[#ffb4ab]">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'restricted_users'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Active 7d</p>\n                <strong class="font-[\'Manrope\'] text-3xl text-[#9dd0cd]">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'active_users_7d'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Words</p>\n                <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'total_words'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Quizzes</p>\n                <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'total_quizzes'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Visits</p>\n                <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'total_visits'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Active Hours</p>\n                <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'total_active_hours'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Flagged Enrichments</p>\n                <strong class="font-[\'Manrope\'] text-3xl text-[#dec38f]">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'flagged_enrichments'))
    yield '</strong>\n            </article>\n            <article class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-4">\n                <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Review Flags</p>\n                <strong class="font-[\'Manrope\'] text-3xl text-[#ffb4ab]">'
    yield escape(environment.getattr((undefined(name='admin_summary') if l_0_admin_summary is missing else l_0_admin_summary), 'review_flags'))
    yield '</strong>\n            </article>\n        </section>\n\n        '
    l_0_dh = t_1((undefined(name='db_health') if l_0_db_health is missing else l_0_db_health), {})
    _block_vars['dh'] = l_0_dh
    yield '\n        '
    l_0_dh_counts = context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'counts', {}, _block_vars=_block_vars)
    _block_vars['dh_counts'] = l_0_dh_counts
    yield '\n        '
    l_0_dh_missing_tables = context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'missing_tables', [], _block_vars=_block_vars)
    _block_vars['dh_missing_tables'] = l_0_dh_missing_tables
    yield '\n        '
    l_0_dh_warnings = context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'warnings', [], _block_vars=_block_vars)
    _block_vars['dh_warnings'] = l_0_dh_warnings
    yield '\n        <section class="rounded-3xl border border-white/5 bg-[#1a1c1c] p-5 mb-6">\n            <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">\n                <div>\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#9dd0cd] font-bold mb-2">Database health</p>\n                    <h2 class="font-[\'Manrope\'] text-2xl font-extrabold tracking-tight m-0">'
    yield escape(t_4(t_3(context.eval_ctx, context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'status', 'unknown', _block_vars=_block_vars), '_', ' ')))
    yield '</h2>\n                </div>\n                '
    if context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'fallback_used', False, _block_vars=_block_vars):
        pass
        yield '\n                <span class="rounded-full bg-[#93000a]/30 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ffb4ab]">Fallback DB Active</span>\n                '
    elif (not context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'healthy', False, _block_vars=_block_vars)):
        pass
        yield '\n                <span class="rounded-full bg-[#dec38f]/20 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#dec38f]">Diagnostics Unavailable</span>\n                '
    else:
        pass
        yield '\n                <span class="rounded-full bg-[#2d5f5d]/30 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#9dd0cd]">Primary DB Active</span>\n                '
    yield '\n            </div>\n            '
    if context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'error', _block_vars=_block_vars):
        pass
        yield '\n            <p class="mt-4 mb-0 text-sm text-[#ffb4ab]">Database diagnostics unavailable: '
        yield escape(context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'error', _block_vars=_block_vars))
        yield '</p>\n            '
    yield '\n            <div class="mt-5 grid gap-3 md:grid-cols-4">\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Type</p>\n                    <strong>'
    yield escape(context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'db_type', context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'database_type', 'unknown', _block_vars=_block_vars), _block_vars=_block_vars))
    if context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'provider', _block_vars=_block_vars):
        pass
        yield ' / '
        yield escape(context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'provider', _block_vars=_block_vars))
    yield '</strong>\n                </div>\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Host</p>\n                    <strong class="break-all">'
    yield escape((context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'host', _block_vars=_block_vars) or 'local file'))
    yield '</strong>\n                </div>\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Database</p>\n                    <strong class="break-all">'
    yield escape((context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'database', context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'database_name', 'unknown', _block_vars=_block_vars), _block_vars=_block_vars) or 'unknown'))
    yield '</strong>\n                </div>\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Migration</p>\n                    <strong>'
    yield escape((context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'alembic_version', context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'migration_version', 'not recorded', _block_vars=_block_vars), _block_vars=_block_vars) or 'not recorded'))
    yield '</strong>\n                </div>\n            </div>\n            <div class="mt-4 grid gap-3 md:grid-cols-3">\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Vocabulary</p>\n                    <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(context.call(environment.getattr((undefined(name='dh_counts') if l_0_dh_counts is missing else l_0_dh_counts), 'get'), 'vocabulary_master', context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'vocabulary_count', 0, _block_vars=_block_vars), _block_vars=_block_vars))
    yield '</strong>\n                </div>\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Users</p>\n                    <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(context.call(environment.getattr((undefined(name='dh_counts') if l_0_dh_counts is missing else l_0_dh_counts), 'get'), 'users', context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'user_count', 0, _block_vars=_block_vars), _block_vars=_block_vars))
    yield '</strong>\n                </div>\n                <div class="rounded-2xl border border-white/5 bg-[#0d0f0f] p-4">\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold mb-2">Enrichments</p>\n                    <strong class="font-[\'Manrope\'] text-3xl">'
    yield escape(context.call(environment.getattr((undefined(name='dh_counts') if l_0_dh_counts is missing else l_0_dh_counts), 'get'), 'vocabulary_enrichment', context.call(environment.getattr((undefined(name='dh') if l_0_dh is missing else l_0_dh), 'get'), 'enrichment_count', 0, _block_vars=_block_vars), _block_vars=_block_vars))
    yield '</strong>\n                </div>\n            </div>\n            '
    if (undefined(name='dh_missing_tables') if l_0_dh_missing_tables is missing else l_0_dh_missing_tables):
        pass
        yield '\n            <p class="mt-4 mb-0 text-sm text-[#ffb4ab]">Missing tables: '
        yield escape(t_2(context.eval_ctx, (undefined(name='dh_missing_tables') if l_0_dh_missing_tables is missing else l_0_dh_missing_tables), ', '))
        yield '. Run the Alembic migrations before using this database.</p>\n            '
    yield '\n            '
    if (undefined(name='dh_warnings') if l_0_dh_warnings is missing else l_0_dh_warnings):
        pass
        yield '\n            <p class="mt-4 mb-0 text-sm text-[#dec38f]">'
        yield escape(t_2(context.eval_ctx, (undefined(name='dh_warnings') if l_0_dh_warnings is missing else l_0_dh_warnings), ' '))
        yield '</p>\n            '
    yield '\n        </section>\n\n        <details class="rounded-3xl border border-white/5 bg-[#1a1c1c] shadow-2xl overflow-hidden mb-6" open>\n            <summary class="flex cursor-pointer items-center justify-between px-6 py-5 border-b border-white/5">\n                <div>\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#dec38f] font-bold mb-2">Enrichment cache</p>\n                    <h2 class="font-[\'Manrope\'] text-2xl font-extrabold tracking-tight">Quality audit and correction</h2>\n                </div>\n                <span class="text-xs text-[#c0c8c7]">'
    yield escape((undefined(name='enrichment_total') if l_0_enrichment_total is missing else l_0_enrichment_total))
    yield ' rows</span>\n            </summary>\n            <form method="get" class="grid gap-3 border-b border-white/5 px-6 py-4 sm:grid-cols-[1fr_auto]">\n                <input name="enrichment_q" value="'
    yield escape((undefined(name='enrichment_q') if l_0_enrichment_q is missing else l_0_enrichment_q))
    yield '" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-3 text-sm text-[#e2e2e2] outline-none" placeholder="Search enrichment cache">\n                <button class="rounded-xl bg-[#2d5f5d] px-4 py-3 text-xs font-bold uppercase tracking-[0.18em] text-[#b9ece9] border-none cursor-pointer">Filter</button>\n            </form>\n            <div class="overflow-x-auto no-scrollbar">\n                <table class="w-full min-w-[1200px]">\n                    <thead>\n                        <tr class="text-left text-[10px] uppercase tracking-[0.18em] text-[#8a9291]">\n                            <th class="px-6 py-4 font-bold">Word</th>\n                            <th class="px-6 py-4 font-bold">Score</th>\n                            <th class="px-6 py-4 font-bold">Flags</th>\n                            <th class="px-6 py-4 font-bold">Correction</th>\n                            <th class="px-6 py-4 font-bold">Delete</th>\n                        </tr>\n                    </thead>\n                    <tbody>\n                        '
    for l_1_enrichment in (undefined(name='enrichment_rows') if l_0_enrichment_rows is missing else l_0_enrichment_rows):
        l_1_admin_csrf_token = resolve('admin_csrf_token')
        _loop_vars = {}
        pass
        yield '\n                        <tr class="border-t border-white/5 align-top">\n                            <td class="px-6 py-5">\n                                <p class="font-semibold text-[#e2e2e2] m-0">'
        yield escape(environment.getattr(environment.getattr(l_1_enrichment, 'vocabulary'), 'word'))
        yield '</p>\n                                <p class="text-xs text-[#c0c8c7] mt-1 mb-0">'
        yield escape(environment.getattr(environment.getattr(l_1_enrichment, 'vocabulary'), 'level'))
        yield '</p>\n                                '
        if environment.getattr(l_1_enrichment, 'corrected_manually'):
            pass
            yield '\n                                <p class="text-[10px] text-[#9dd0cd] mt-2 mb-0 uppercase tracking-[0.14em]">Manual correction</p>\n                                '
        yield '\n                            </td>\n                            <td class="px-6 py-5 text-sm text-[#e2e2e2]">'
        yield escape(environment.getattr(l_1_enrichment, 'enrichment_quality_score'))
        yield '</td>\n                            <td class="px-6 py-5 text-xs text-[#dec38f]">'
        yield escape((environment.getattr(l_1_enrichment, 'audit_flags') or 'clean'))
        yield '</td>\n                            <td class="px-6 py-5">\n                                <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_edit_enrichment', enrichment_id=environment.getattr(l_1_enrichment, 'id'), _loop_vars=_loop_vars))
        yield '" class="grid grid-cols-2 gap-2 m-0">\n                                    <input type="hidden" name="csrf_token" value="'
        yield escape((undefined(name='admin_csrf_token') if l_1_admin_csrf_token is missing else l_1_admin_csrf_token))
        yield '">\n                                    <textarea name="definition" rows="2" class="col-span-2 rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none">'
        yield escape((environment.getattr(l_1_enrichment, 'definition') or ''))
        yield '</textarea>\n                                    <input name="pronunciation" value="'
        yield escape((environment.getattr(l_1_enrichment, 'pronunciation') or ''))
        yield '" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none" placeholder="Pronunciation">\n                                    <input name="synonyms" value="'
        yield escape((environment.getattr(l_1_enrichment, 'synonyms') or ''))
        yield '" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none" placeholder="Synonym">\n                                    <input name="antonyms" value="'
        yield escape((environment.getattr(l_1_enrichment, 'antonyms') or ''))
        yield '" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none" placeholder="Antonym">\n                                    <button type="submit" class="col-span-2 rounded-xl bg-[#2d5f5d] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#b9ece9] border-none cursor-pointer">Save Manual Correction</button>\n                                </form>\n                            </td>\n                            <td class="px-6 py-5">\n                                <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_delete_vocabulary', vocabulary_id=environment.getattr(environment.getattr(l_1_enrichment, 'vocabulary'), 'id'), _loop_vars=_loop_vars))
        yield '" class="m-0">\n                                    <input type="hidden" name="csrf_token" value="'
        yield escape((undefined(name='admin_csrf_token') if l_1_admin_csrf_token is missing else l_1_admin_csrf_token))
        yield '">\n                                    <button type="submit" class="w-full rounded-xl bg-[#93000a] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ffdad6] border-none cursor-pointer">Delete Word</button>\n                                </form>\n                            </td>\n                        </tr>\n                        '
    l_1_enrichment = l_1_admin_csrf_token = missing
    yield '\n                    </tbody>\n                </table>\n            </div>\n            <div class="flex items-center justify-between gap-3 px-6 py-4 border-t border-white/5 text-xs text-[#c0c8c7]">\n                <a class="rounded-xl border border-white/10 px-3 py-2 text-[#e2e2e2] no-underline '
    if ((undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page) <= 1):
        pass
        yield 'opacity-40 pointer-events-none'
    yield '" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', enrichment_page=((undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page) - 1), enrichment_q=(undefined(name='enrichment_q') if l_0_enrichment_q is missing else l_0_enrichment_q), _block_vars=_block_vars))
    yield '">Previous</a>\n                <span>Page '
    yield escape((undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page))
    yield '</span>\n                <a class="rounded-xl border border-white/10 px-3 py-2 text-[#e2e2e2] no-underline '
    if (((undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page) * 15) >= (undefined(name='enrichment_total') if l_0_enrichment_total is missing else l_0_enrichment_total)):
        pass
        yield 'opacity-40 pointer-events-none'
    yield '" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', enrichment_page=((undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page) + 1), enrichment_q=(undefined(name='enrichment_q') if l_0_enrichment_q is missing else l_0_enrichment_q), _block_vars=_block_vars))
    yield '">Next</a>\n            </div>\n        </details>\n\n        <details class="rounded-3xl border border-white/5 bg-[#1a1c1c] shadow-2xl overflow-hidden mb-6" open>\n            <summary class="flex cursor-pointer items-center justify-between px-6 py-5 border-b border-white/5">\n                <div>\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#ffb4ab] font-bold mb-2">Vocabulary review flags</p>\n                    <h2 class="font-[\'Manrope\'] text-2xl font-extrabold tracking-tight">Correction queue</h2>\n                </div>\n                <span class="text-xs text-[#c0c8c7]">'
    yield escape((undefined(name='review_flag_total') if l_0_review_flag_total is missing else l_0_review_flag_total))
    yield ' rows</span>\n            </summary>\n            <form method="get" class="grid gap-3 border-b border-white/5 px-6 py-4 sm:grid-cols-[1fr_1fr_auto]">\n                <select name="flag_status" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-3 text-sm text-[#e2e2e2] outline-none">\n                    '
    for l_1_status in ['pending', 'approved', 'edited', 'reassigned', 'deleted', 'all']:
        _loop_vars = {}
        pass
        yield '\n                    <option value="'
        yield escape(l_1_status)
        yield '" '
        if ((undefined(name='flag_status') if l_0_flag_status is missing else l_0_flag_status) == l_1_status):
            pass
            yield 'selected'
        yield '>'
        yield escape(t_4(l_1_status))
        yield '</option>\n                    '
    l_1_status = missing
    yield '\n                </select>\n                <select name="flag_type" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-3 text-sm text-[#e2e2e2] outline-none">\n                    <option value="">All flag types</option>\n                    '
    for l_1_type in ['malformed_word', 'suspicious_ocr', 'too_easy_for_level', 'duplicate_meaning', 'invalid_english', 'corrupted_phrase']:
        _loop_vars = {}
        pass
        yield '\n                    <option value="'
        yield escape(l_1_type)
        yield '" '
        if ((undefined(name='flag_type') if l_0_flag_type is missing else l_0_flag_type) == l_1_type):
            pass
            yield 'selected'
        yield '>'
        yield escape(l_1_type)
        yield '</option>\n                    '
    l_1_type = missing
    yield '\n                </select>\n                <button class="rounded-xl bg-[#2d5f5d] px-4 py-3 text-xs font-bold uppercase tracking-[0.18em] text-[#b9ece9] border-none cursor-pointer">Filter</button>\n            </form>\n            <div class="divide-y divide-white/5">\n                '
    for l_1_flag in (undefined(name='review_flags') if l_0_review_flags is missing else l_0_review_flags):
        l_1_admin_csrf_token = resolve('admin_csrf_token')
        _loop_vars = {}
        pass
        yield '\n                <details class="px-6 py-4">\n                    <summary class="cursor-pointer">\n                        <span class="font-semibold">'
        yield escape(environment.getattr(l_1_flag, 'original_word'))
        yield '</span>\n                        <span class="ml-2 text-xs text-[#dec38f]">'
        yield escape(environment.getattr(l_1_flag, 'flag_type'))
        yield '</span>\n                        <span class="ml-2 text-xs text-[#8a9291]">'
        yield escape(environment.getattr(l_1_flag, 'status'))
        yield '</span>\n                    </summary>\n                    <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_review_flag_action', flag_id=environment.getattr(l_1_flag, 'id'), _loop_vars=_loop_vars))
        yield '" class="mt-4 grid gap-2 md:grid-cols-4">\n                        <input type="hidden" name="csrf_token" value="'
        yield escape((undefined(name='admin_csrf_token') if l_1_admin_csrf_token is missing else l_1_admin_csrf_token))
        yield '">\n                        <input name="word" value="'
        yield escape((environment.getattr(environment.getattr(l_1_flag, 'vocabulary'), 'word') if environment.getattr(l_1_flag, 'vocabulary') else (environment.getattr(l_1_flag, 'corrected_word') or '')))
        yield '" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none" placeholder="Correct word">\n                        <select name="level" class="rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none">\n                            '
        for l_2_level in ['intermediate', 'upper_intermediate', 'advanced']:
            _loop_vars = {}
            pass
            yield '\n                            <option value="'
            yield escape(l_2_level)
            yield '" '
            if ((environment.getattr(l_1_flag, 'vocabulary') and (environment.getattr(environment.getattr(l_1_flag, 'vocabulary'), 'level') == l_2_level)) or (environment.getattr(l_1_flag, 'level') == l_2_level)):
                pass
                yield 'selected'
            yield '>'
            yield escape(l_2_level)
            yield '</option>\n                            '
        l_2_level = missing
        yield '\n                        </select>\n                        <button name="action" value="edit" class="rounded-xl bg-[#2d5f5d] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#b9ece9] border-none cursor-pointer">Edit</button>\n                        <button name="action" value="approve" class="rounded-xl border border-white/10 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#e2e2e2] bg-transparent cursor-pointer">Approve</button>\n                        <button name="action" value="reassign" class="rounded-xl bg-[#dec38f]/15 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#dec38f] border border-[#dec38f]/20 cursor-pointer">Reassign</button>\n                        <button name="action" value="delete" class="rounded-xl bg-[#93000a] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ffdad6] border-none cursor-pointer">Delete</button>\n                    </form>\n                    '
        if environment.getattr(l_1_flag, 'notes'):
            pass
            yield '<p class="mt-3 mb-0 text-xs text-[#c0c8c7]">'
            yield escape(environment.getattr(l_1_flag, 'notes'))
            yield '</p>'
        yield '\n                </details>\n                '
    l_1_flag = l_1_admin_csrf_token = missing
    yield '\n            </div>\n            <div class="flex items-center justify-between gap-3 px-6 py-4 border-t border-white/5 text-xs text-[#c0c8c7]">\n                <a class="rounded-xl border border-white/10 px-3 py-2 text-[#e2e2e2] no-underline '
    if ((undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page) <= 1):
        pass
        yield 'opacity-40 pointer-events-none'
    yield '" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', flag_page=((undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page) - 1), flag_status=(undefined(name='flag_status') if l_0_flag_status is missing else l_0_flag_status), flag_type=(undefined(name='flag_type') if l_0_flag_type is missing else l_0_flag_type), _block_vars=_block_vars))
    yield '">Previous</a>\n                <span>Page '
    yield escape((undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page))
    yield '</span>\n                <a class="rounded-xl border border-white/10 px-3 py-2 text-[#e2e2e2] no-underline '
    if (((undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page) * 15) >= (undefined(name='review_flag_total') if l_0_review_flag_total is missing else l_0_review_flag_total)):
        pass
        yield 'opacity-40 pointer-events-none'
    yield '" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', flag_page=((undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page) + 1), flag_status=(undefined(name='flag_status') if l_0_flag_status is missing else l_0_flag_status), flag_type=(undefined(name='flag_type') if l_0_flag_type is missing else l_0_flag_type), _block_vars=_block_vars))
    yield '">Next</a>\n            </div>\n        </details>\n\n        <details class="rounded-3xl border border-white/5 bg-[#1a1c1c] shadow-2xl overflow-hidden">\n            <summary class="flex cursor-pointer items-center justify-between px-6 py-5 border-b border-white/5">\n                <div>\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#9dd0cd] font-bold mb-2">Users</p>\n                    <h2 class="font-[\'Manrope\'] text-2xl font-extrabold tracking-tight">User controls</h2>\n                </div>\n                <p class="text-xs text-[#c0c8c7] m-0 hidden md:block">'
    yield escape((undefined(name='user_total') if l_0_user_total is missing else l_0_user_total))
    yield ' users. Restricted users cannot log in or use the app.</p>\n            </summary>\n\n            <div class="overflow-x-auto no-scrollbar">\n                <table class="w-full min-w-[1100px]">\n                    <thead>\n                        <tr class="text-left text-[10px] uppercase tracking-[0.18em] text-[#8a9291]">\n                            <th class="px-6 py-4 font-bold">User</th>\n                            <th class="px-6 py-4 font-bold">Joined</th>\n                            <th class="px-6 py-4 font-bold">Last Login</th>\n                            <th class="px-6 py-4 font-bold">Words</th>\n                            <th class="px-6 py-4 font-bold">Quizzes</th>\n                            <th class="px-6 py-4 font-bold">Visits</th>\n                            <th class="px-6 py-4 font-bold">Active</th>\n                            <th class="px-6 py-4 font-bold">Views</th>\n                            <th class="px-6 py-4 font-bold">Status</th>\n                            <th class="px-6 py-4 font-bold">Action</th>\n                        </tr>\n                    </thead>\n                    <tbody>\n                        '
    for l_1_row in (undefined(name='user_rows') if l_0_user_rows is missing else l_0_user_rows):
        l_1_admin_csrf_token = resolve('admin_csrf_token')
        _loop_vars = {}
        pass
        yield '\n                        <tr class="border-t border-white/5 align-top">\n                            <td class="px-6 py-5">\n                                <p class="font-semibold text-[#e2e2e2] m-0">'
        yield escape(environment.getattr(environment.getattr(l_1_row, 'user'), 'display_name'))
        yield '</p>\n                                <p class="text-xs text-[#c0c8c7] mt-1 mb-0">'
        yield escape(environment.getattr(environment.getattr(l_1_row, 'user'), 'email'))
        yield '</p>\n                                '
        if environment.getattr(environment.getattr(l_1_row, 'user'), 'restricted_reason'):
            pass
            yield '\n                                <p class="text-xs text-[#ffb4ab] mt-2 mb-0">'
            yield escape(environment.getattr(environment.getattr(l_1_row, 'user'), 'restricted_reason'))
            yield '</p>\n                                '
        yield '\n                            </td>\n                            <td class="px-6 py-5 text-sm text-[#c0c8c7]">'
        yield escape((context.call(environment.getattr(environment.getattr(environment.getattr(l_1_row, 'user'), 'created_at'), 'strftime'), '%Y-%m-%d', _loop_vars=_loop_vars) if environment.getattr(environment.getattr(l_1_row, 'user'), 'created_at') else '-'))
        yield '</td>\n                            <td class="px-6 py-5 text-sm text-[#c0c8c7]">'
        yield escape((context.call(environment.getattr(environment.getattr(environment.getattr(l_1_row, 'user'), 'last_login_at'), 'strftime'), '%Y-%m-%d %H:%M', _loop_vars=_loop_vars) if environment.getattr(environment.getattr(l_1_row, 'user'), 'last_login_at') else '-'))
        yield '</td>\n                            <td class="px-6 py-5 text-sm text-[#e2e2e2]">'
        yield escape(environment.getattr(l_1_row, 'word_count'))
        yield '</td>\n                            <td class="px-6 py-5 text-sm text-[#e2e2e2]">'
        yield escape(environment.getattr(l_1_row, 'quiz_count'))
        yield '</td>\n                            <td class="px-6 py-5 text-sm text-[#e2e2e2]">'
        yield escape(environment.getattr(l_1_row, 'visit_count'))
        yield '</td>\n                            <td class="px-6 py-5 text-sm text-[#e2e2e2]">'
        yield escape(environment.getattr(l_1_row, 'active_minutes'))
        yield 'm</td>\n                            <td class="px-6 py-5 text-sm text-[#e2e2e2]">'
        yield escape(environment.getattr(l_1_row, 'page_views'))
        yield '</td>\n                            <td class="px-6 py-5">\n                                '
        if environment.getattr(environment.getattr(l_1_row, 'user'), 'is_restricted'):
            pass
            yield '\n                                <span class="inline-flex rounded-full bg-[#93000a]/30 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ffb4ab]">Restricted</span>\n                                '
        else:
            pass
            yield '\n                                <span class="inline-flex rounded-full bg-[#2d5f5d]/30 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#9dd0cd]">Active</span>\n                                '
        yield '\n                            </td>\n                            <td class="px-6 py-5">\n                                <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_update_user_restriction', user_id=environment.getattr(environment.getattr(l_1_row, 'user'), 'id'), _loop_vars=_loop_vars))
        yield '" class="space-y-2 m-0">\n                                    <input type="hidden" name="csrf_token" value="'
        yield escape((undefined(name='admin_csrf_token') if l_1_admin_csrf_token is missing else l_1_admin_csrf_token))
        yield '">\n                                    '
        if environment.getattr(environment.getattr(l_1_row, 'user'), 'is_restricted'):
            pass
            yield '\n                                    <input type="hidden" name="action" value="unrestrict">\n                                    <button type="submit" class="w-full rounded-xl bg-[#2d5f5d] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#b9ece9] border-none cursor-pointer">Restore</button>\n                                    '
        else:
            pass
            yield '\n                                    <input type="hidden" name="action" value="restrict">\n                                    <textarea name="restricted_reason" rows="2" class="w-full rounded-xl border border-white/10 bg-[#0d0f0f] px-3 py-2 text-xs text-[#e2e2e2] outline-none" placeholder="Reason (optional)"></textarea>\n                                    <button type="submit" class="w-full rounded-xl bg-[#93000a] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ffdad6] border-none cursor-pointer">Restrict</button>\n                                    '
        yield '\n                                </form>\n                                <form method="post" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_reset_learning_journey', user_id=environment.getattr(environment.getattr(l_1_row, 'user'), 'id'), _loop_vars=_loop_vars))
        yield '" class="mt-2 m-0">\n                                    <input type="hidden" name="csrf_token" value="'
        yield escape((undefined(name='admin_csrf_token') if l_1_admin_csrf_token is missing else l_1_admin_csrf_token))
        yield '">\n                                    <button type="submit" class="w-full rounded-xl bg-[#dec38f]/15 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#dec38f] border border-[#dec38f]/20 cursor-pointer">Reset Learning Journey</button>\n                                </form>\n                                '
        if environment.getattr(l_1_row, 'last_seen_at'):
            pass
            yield '\n                                <p class="text-[10px] text-[#8a9291] mt-2 mb-0">Last seen '
            yield escape(context.call(environment.getattr(environment.getattr(l_1_row, 'last_seen_at'), 'strftime'), '%Y-%m-%d %H:%M', _loop_vars=_loop_vars))
            yield '</p>\n                                '
        yield '\n                            </td>\n                        </tr>\n                        '
    l_1_row = l_1_admin_csrf_token = missing
    yield '\n                    </tbody>\n                </table>\n            </div>\n            <div class="flex items-center justify-between gap-3 px-6 py-4 border-t border-white/5 text-xs text-[#c0c8c7]">\n                <a class="rounded-xl border border-white/10 px-3 py-2 text-[#e2e2e2] no-underline '
    if ((undefined(name='user_page') if l_0_user_page is missing else l_0_user_page) <= 1):
        pass
        yield 'opacity-40 pointer-events-none'
    yield '" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', user_page=((undefined(name='user_page') if l_0_user_page is missing else l_0_user_page) - 1), enrichment_page=(undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page), enrichment_q=(undefined(name='enrichment_q') if l_0_enrichment_q is missing else l_0_enrichment_q), flag_page=(undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page), flag_status=(undefined(name='flag_status') if l_0_flag_status is missing else l_0_flag_status), flag_type=(undefined(name='flag_type') if l_0_flag_type is missing else l_0_flag_type), _block_vars=_block_vars))
    yield '">Previous</a>\n                <span>Page '
    yield escape((undefined(name='user_page') if l_0_user_page is missing else l_0_user_page))
    yield '</span>\n                <a class="rounded-xl border border-white/10 px-3 py-2 text-[#e2e2e2] no-underline '
    if (((undefined(name='user_page') if l_0_user_page is missing else l_0_user_page) * 25) >= (undefined(name='user_total') if l_0_user_total is missing else l_0_user_total)):
        pass
        yield 'opacity-40 pointer-events-none'
    yield '" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard', user_page=((undefined(name='user_page') if l_0_user_page is missing else l_0_user_page) + 1), enrichment_page=(undefined(name='enrichment_page') if l_0_enrichment_page is missing else l_0_enrichment_page), enrichment_q=(undefined(name='enrichment_q') if l_0_enrichment_q is missing else l_0_enrichment_q), flag_page=(undefined(name='flag_page') if l_0_flag_page is missing else l_0_flag_page), flag_status=(undefined(name='flag_status') if l_0_flag_status is missing else l_0_flag_status), flag_type=(undefined(name='flag_type') if l_0_flag_type is missing else l_0_flag_type), _block_vars=_block_vars))
    yield '">Next</a>\n            </div>\n        </details>\n    </main>\n</div>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&19=77&20=79&21=81&30=83&31=85&32=87&35=89&44=91&48=93&52=95&56=97&60=99&64=101&68=103&72=105&76=107&80=109&81=112&82=115&83=118&88=121&90=123&92=126&98=133&99=136&104=139&108=145&112=147&116=149&122=151&126=153&130=155&133=157&134=160&136=163&137=166&147=169&150=171&165=173&168=178&169=180&170=182&174=186&175=188&177=190&178=192&179=194&180=196&181=198&182=200&187=202&188=204&198=208&199=214&200=216&210=222&214=224&215=228&220=238&221=242&227=252&230=257&231=259&232=261&234=263&235=265&236=267&238=269&239=273&247=283&252=291&253=297&254=299&264=305&284=307&287=312&288=314&289=316&290=319&293=322&294=324&295=326&296=328&297=330&298=332&299=334&301=336&308=343&309=345&310=347&319=354&320=356&323=358&324=361&333=366&334=372&335=374'