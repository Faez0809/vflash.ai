from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'difficult.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'difficult.html')
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
    yield 'Difficult Words | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_user_words = resolve('user_words')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n<section class="panel list-page-panel">\n    <div class="section-heading">\n        <div>\n            <span class="eyebrow">Difficult words</span>\n            <h1>Words marked for extra attention</h1>\n            <p class="muted section-copy">Keep a sharper eye on the vocabulary that needs extra repetition.</p>\n        </div>\n        <span class="badge">'
    yield escape(t_1((undefined(name='user_words') if l_0_user_words is missing else l_0_user_words)))
    yield ' flagged</span>\n    </div>\n\n    '
    if (undefined(name='user_words') if l_0_user_words is missing else l_0_user_words):
        pass
        yield '\n        <div class="word-list">\n            '
        for l_1_item in (undefined(name='user_words') if l_0_user_words is missing else l_0_user_words):
            l_1_url_for = resolve('url_for')
            _loop_vars = {}
            pass
            yield '\n                <article class="word-card" data-user-word-card="'
            yield escape(environment.getattr(l_1_item, 'id'))
            yield '">\n                    <div class="word-card-heading">\n                        <div class="word-card-title">\n                            <h3>'
            yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'word'))
            yield '</h3>\n                            '
            if environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'part_of_speech'):
                pass
                yield '\n                                <span class="word-type">'
                yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'part_of_speech'))
                yield '</span>\n                            '
            yield '\n                        </div>\n                        <span class="status status-warning">Difficult</span>\n                    </div>\n                    <div class="word-meta">\n                        <span class="meta-pill">'
            yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'difficulty') or 'General'))
            yield '</span>\n                        <span class="meta-pill">'
            yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'topic') or 'General topic'))
            yield '</span>\n                        <span class="meta-pill">'
            yield escape(context.call(environment.getattr(environment.getattr(l_1_item, 'added_date'), 'strftime'), '%Y-%m-%d', _loop_vars=_loop_vars))
            yield '</span>\n                    </div>\n                    <dl class="word-details">\n                        <div>\n                            <dt>Meaning</dt>\n                            <dd>'
            yield escape(environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'meaning'))
            yield '</dd>\n                        </div>\n                        <div>\n                            <dt>Example sentence</dt>\n                            <dd>'
            yield escape((environment.getattr(environment.getattr(l_1_item, 'word_entry'), 'sentence') or 'No example yet.'))
            yield '</dd>\n                        </div>\n                    </dl>\n                    <div class="word-card-footer difficult-actions">\n                        '
            if environment.getattr(l_1_item, 'session_id'):
                pass
                yield '\n                            <a class="button-link" href="'
                yield escape(context.call((undefined(name='url_for') if l_1_url_for is missing else l_1_url_for), 'flashcards_session', session_id=environment.getattr(l_1_item, 'session_id'), _loop_vars=_loop_vars))
                yield '">Review</a>\n                        '
            else:
                pass
                yield '\n                            <a class="button-link" href="'
                yield escape(context.call((undefined(name='url_for') if l_1_url_for is missing else l_1_url_for), 'flashcards', _loop_vars=_loop_vars))
                yield '">Review</a>\n                        '
            yield '\n                        <form method="post" action="'
            yield escape(context.call((undefined(name='url_for') if l_1_url_for is missing else l_1_url_for), 'toggle_difficult_flag', user_word_id=environment.getattr(l_1_item, 'id'), _loop_vars=_loop_vars))
            yield '" data-ajax-difficult-form data-remove-card="true">\n                            <input type="hidden" name="next" value="'
            yield escape(context.call((undefined(name='url_for') if l_1_url_for is missing else l_1_url_for), 'difficult_words', _loop_vars=_loop_vars))
            yield '">\n                            <button type="submit" class="button-secondary">Remove from Difficult</button>\n                        </form>\n                    </div>\n                </article>\n            '
        l_1_item = l_1_url_for = missing
        yield '\n        </div>\n    '
    else:
        pass
        yield '\n        <p class="empty-state">No difficult words right now. You are caught up.</p>\n    '
    yield '\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&13=43&16=45&18=48&19=53&22=55&23=57&24=60&30=63&31=65&32=67&37=69&41=71&45=73&46=76&48=81&50=84&51=86'