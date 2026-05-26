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
    try:
        t_1 = environment.filters['title']
    except KeyError:
        @internalcode
        def t_1(*unused):
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
    yield '</strong>\n            </article>\n        </section>\n\n        <details class="rounded-3xl border border-white/5 bg-[#1a1c1c] shadow-2xl overflow-hidden mb-6" open>\n            <summary class="flex cursor-pointer items-center justify-between px-6 py-5 border-b border-white/5">\n                <div>\n                    <p class="text-[10px] uppercase tracking-[0.18em] text-[#dec38f] font-bold mb-2">Enrichment cache</p>\n                    <h2 class="font-[\'Manrope\'] text-2xl font-extrabold tracking-tight">Quality audit and correction</h2>\n                </div>\n                <span class="text-xs text-[#c0c8c7]">'
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
        yield escape(t_1(l_1_status))
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
debug_info = '1=12&3=17&5=27&19=57&20=59&21=61&30=63&31=65&32=67&35=69&44=71&48=73&52=75&56=77&60=79&64=81&68=83&72=85&76=87&86=89&89=91&104=93&107=98&108=100&109=102&113=106&114=108&116=110&117=112&118=114&119=116&120=118&121=120&126=122&127=124&137=128&138=134&139=136&149=142&153=144&154=148&159=158&160=162&166=172&169=177&170=179&171=181&173=183&174=185&175=187&177=189&178=193&186=203&191=211&192=217&193=219&203=225&223=227&226=232&227=234&228=236&229=239&232=242&233=244&234=246&235=248&236=250&237=252&238=254&240=256&247=263&248=265&249=267&258=274&259=276&262=278&263=281&272=286&273=292&274=294'