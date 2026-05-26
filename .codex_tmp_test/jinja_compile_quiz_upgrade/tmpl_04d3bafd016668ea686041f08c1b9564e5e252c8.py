from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'sessions.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'sessions.html')
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
    yield 'Study Sessions | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_study_sessions = resolve('study_sessions')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n<section class="panel sessions-panel">\n    <div class="panel-heading">\n        <div>\n            <span class="eyebrow">Study sessions</span>\n            <h1>Session history</h1>\n            <p class="muted section-copy">Jump back into a previous study set whenever you want a focused review.</p>\n        </div>\n        <span class="badge">'
    yield escape(t_1((undefined(name='study_sessions') if l_0_study_sessions is missing else l_0_study_sessions)))
    yield ' total</span>\n    </div>\n\n    '
    if (undefined(name='study_sessions') if l_0_study_sessions is missing else l_0_study_sessions):
        pass
        yield '\n        <div class="sessions-list">\n            '
        for l_1_session in (undefined(name='study_sessions') if l_0_study_sessions is missing else l_0_study_sessions):
            l_1_url_for = resolve('url_for')
            _loop_vars = {}
            pass
            yield '\n                <article class="session-card">\n                    <div class="word-card-heading">\n                        <h2>Session #'
            yield escape(environment.getattr(l_1_session, 'id'))
            yield '</h2>\n                        <span class="badge">'
            yield escape(environment.getattr(l_1_session, 'word_count'))
            yield ' words</span>\n                    </div>\n                    <p><strong>Difficulty:</strong> '
            yield escape(environment.getattr(l_1_session, 'difficulty'))
            yield '</p>\n                    <p><strong>Created:</strong> '
            yield escape(context.call(environment.getattr(environment.getattr(l_1_session, 'created_at'), 'strftime'), '%Y-%m-%d', _loop_vars=_loop_vars))
            yield '</p>\n                    '
            if environment.getattr(l_1_session, 'custom_prompt'):
                pass
                yield '\n                        <p><strong>Focus:</strong> '
                yield escape(environment.getattr(l_1_session, 'custom_prompt'))
                yield '</p>\n                    '
            yield '\n                    <p><a class="button-link" href="'
            yield escape(context.call((undefined(name='url_for') if l_1_url_for is missing else l_1_url_for), 'flashcards_session', session_id=environment.getattr(l_1_session, 'id'), _loop_vars=_loop_vars))
            yield '">Open session</a></p>\n                </article>\n            '
        l_1_session = l_1_url_for = missing
        yield '\n        </div>\n    '
    else:
        pass
        yield '\n        <p class="empty-state">No study sessions yet. Generate a set of words from the dashboard to start one.</p>\n    '
    yield '\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&13=43&16=45&18=48&21=53&22=55&24=57&25=59&26=61&27=64&29=67'