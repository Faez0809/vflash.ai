from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'search.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'search.html')
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
    yield 'Word Search | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_search_query = resolve('search_query')
    l_0_word = resolve('word')
    l_0_autocorrected_from = resolve('autocorrected_from')
    l_0_resolved_query = resolve('resolved_query')
    l_0_requested_part_of_speech = resolve('requested_part_of_speech')
    l_0_related_words = resolve('related_words')
    l_0_lookup_status = resolve('lookup_status')
    l_0_lookup_suggestions = resolve('lookup_suggestions')
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_2 = environment.filters['lower']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'lower' found.")
    pass
    yield '\n<section class="search-flashcard-wrap">\n    <div class="flashcard-panel search-flashcard-panel search-direct-panel">\n        <div class="search-direct-toolbar">\n            <form class="search-page-form" action="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'search_word', _block_vars=_block_vars))
    yield '" method="get" data-async-page="true" data-loading-messages=\'["Searching...","Checking database...","Generating word details..."]\'>\n                <span class="material-symbols-outlined" aria-hidden="true">search</span>\n                <input type="search" name="q" value="'
    yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
    yield '" placeholder="Search any word, phrase, or topic" data-placeholder-full="Search any word, phrase, or topic" data-placeholder-compact="Search word, phrase, or topic" aria-label="Search any word, phrase, or topic" maxlength="60" autocomplete="off">\n                <button type="submit">Search</button>\n            </form>\n            <a class="search-page-back" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '">Back to Dashboard</a>\n        </div>\n\n        <article class="search-flashcard-card search-direct-card">\n            '
    if (undefined(name='word') if l_0_word is missing else l_0_word):
        pass
        yield '\n                '
        if ((undefined(name='autocorrected_from') if l_0_autocorrected_from is missing else l_0_autocorrected_from) and (undefined(name='resolved_query') if l_0_resolved_query is missing else l_0_resolved_query)):
            pass
            yield '\n                    <section class="search-guidance-panel search-guidance-panel-success" aria-live="polite">\n                        <p class="search-guidance-eyebrow">Showing results for</p>\n                        <h2 class="search-guidance-title">'
            yield escape((undefined(name='resolved_query') if l_0_resolved_query is missing else l_0_resolved_query))
            yield '</h2>\n                        <p class="search-guidance-copy">We couldn’t find an exact match for <strong>"'
            yield escape((undefined(name='autocorrected_from') if l_0_autocorrected_from is missing else l_0_autocorrected_from))
            yield '"</strong>, so we used the closest verified word.</p>\n                    </section>\n                '
        yield '\n\n                <div class="search-direct-head">\n                    <div class="search-word-heading">\n                        <h1>'
        yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'word'))
        yield '</h1>\n                        '
        if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'part_of_speech'):
            pass
            yield '\n                            <span class="flashcard-pos">'
            yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'part_of_speech'))
            yield '</span>\n                        '
        yield '\n                    </div>\n                    <p class="search-flashcard-meaning">\n                        '
        if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'lookup_pending'):
            pass
            yield '\n                            We are preparing this word now so your card stays accurate and useful.\n                        '
        else:
            pass
            yield '\n                            '
            yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'meaning'))
            yield '\n                        '
        yield '\n                    </p>\n                </div>\n\n                '
        if (((undefined(name='requested_part_of_speech') if l_0_requested_part_of_speech is missing else l_0_requested_part_of_speech) and environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'part_of_speech')) and ((undefined(name='requested_part_of_speech') if l_0_requested_part_of_speech is missing else l_0_requested_part_of_speech) != t_2(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'part_of_speech')))):
            pass
            yield '\n                    <section class="flashcard-detail search-flashcard-detail-wide" aria-live="polite">\n                        <p class="stitch-label">Available form</p>\n                        <p>The closest saved entry for <strong>'
            yield escape((undefined(name='resolved_query') if l_0_resolved_query is missing else l_0_resolved_query))
            yield '</strong> is shown as a '
            yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'part_of_speech'))
            yield '.</p>\n                    </section>\n                '
        yield '\n\n                '
        if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'lookup_pending'):
            pass
            yield '\n                    <section class="search-pending-state search-flashcard-detail-wide" aria-live="polite">\n                        <p class="search-pending-badge">Preparing this entry</p>\n                        <h2 class="search-pending-title">This word is in our AI vocabulary queue.</h2>\n                        <p class="search-pending-copy">Search another word now, and come back to <strong>'
            yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'word'))
            yield '</strong> shortly. We keep preparing all levels of vocabulary, including advanced and rare words.</p>\n                        <p class="search-pending-note">Tip: try a close spelling or a related form while this entry finishes.</p>\n                    </section>\n                '
        else:
            pass
            yield '\n                    <div class="flashcard-back-grid search-flashcard-grid search-direct-grid">\n                        '
            if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'bangla_meaning'):
                pass
                yield '\n                        <div class="flashcard-detail">\n                            <p class="stitch-label">Bangla meaning</p>\n                            <p>'
                yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'bangla_meaning'))
                yield '</p>\n                        </div>\n                        '
            yield '\n                        '
            if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'phonetic'):
                pass
                yield '\n                        <div class="flashcard-detail">\n                            <p class="stitch-label">Pronunciation</p>\n                            <p>'
                yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'phonetic'))
                yield '</p>\n                        </div>\n                        '
            yield '\n                        '
            if (environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'synonym_hint') or environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'synonym')):
                pass
                yield '\n                        <div class="flashcard-detail">\n                            <p class="stitch-label">Synonym</p>\n                            <p>'
                yield escape((environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'synonym_hint') or environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'synonym')))
                yield '</p>\n                        </div>\n                        '
            yield '\n                        '
            if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'antonym_hint'):
                pass
                yield '\n                            <div class="flashcard-detail">\n                                <p class="stitch-label">Antonym</p>\n                                <p>'
                yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'antonym_hint'))
                yield '</p>\n                            </div>\n                        '
            yield '\n                        '
            if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'topic'):
                pass
                yield '\n                        <div class="flashcard-detail">\n                            <p class="stitch-label">Topic</p>\n                            <p>'
                yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'topic'))
                yield '</p>\n                        </div>\n                        '
            yield '\n                        '
            if environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'sentence'):
                pass
                yield '\n                        <div class="flashcard-detail search-flashcard-detail-wide">\n                            <p class="stitch-label">Sentence</p>\n                            <p>'
                yield escape(environment.getattr((undefined(name='word') if l_0_word is missing else l_0_word), 'sentence'))
                yield '</p>\n                        </div>\n                        '
            yield '\n                        '
            if (undefined(name='related_words') if l_0_related_words is missing else l_0_related_words):
                pass
                yield '\n                            <div class="flashcard-detail search-flashcard-detail-wide">\n                                <p class="stitch-label">Related forms</p>\n                                <p>'
                yield escape(t_1(context.eval_ctx, (undefined(name='related_words') if l_0_related_words is missing else l_0_related_words), ', '))
                yield '</p>\n                            </div>\n                        '
            yield '\n                    </div>\n                '
        yield '\n            '
    else:
        pass
        yield '\n                <div class="search-direct-head">\n                    <div class="search-word-heading">\n                        <h1>'
        yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
        yield '</h1>\n                    </div>\n                    <p class="search-flashcard-meaning">\n                        '
        if ((undefined(name='lookup_status') if l_0_lookup_status is missing else l_0_lookup_status) == 'suggestions'):
            pass
            yield '\n                            We couldn’t find an exact match for your input.\n                        '
        else:
            pass
            yield '\n                            This word is not available in our verified vocabulary.\n                        '
        yield '\n                    </p>\n                </div>\n\n                <section class="search-guidance-panel search-flashcard-detail-wide" aria-live="polite">\n                    <p class="search-guidance-eyebrow">Search guidance</p>\n                    <h2 class="search-guidance-title">'
        yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
        yield '</h2>\n                    '
        if (undefined(name='lookup_suggestions') if l_0_lookup_suggestions is missing else l_0_lookup_suggestions):
            pass
            yield '\n                        <p class="search-guidance-copy">You entered: <strong>"'
            yield escape((undefined(name='search_query') if l_0_search_query is missing else l_0_search_query))
            yield '"</strong></p>\n                        <p class="search-guidance-status">This word could not be matched to a verified English entry.</p>\n                        <div class="search-suggestion-list">\n                            '
            for l_1_suggestion in (undefined(name='lookup_suggestions') if l_0_lookup_suggestions is missing else l_0_lookup_suggestions):
                _loop_vars = {}
                pass
                yield '\n                                <button type="button" class="search-suggestion-chip" data-search-suggestion="'
                yield escape(l_1_suggestion)
                yield '">'
                yield escape(l_1_suggestion)
                yield '</button>\n                            '
            l_1_suggestion = missing
            yield '\n                        </div>\n                    '
        else:
            pass
            yield '\n                        <p class="search-guidance-status">We didn’t generate a definition because the spelling could not be verified safely.</p>\n                    '
        yield '\n                </section>\n            '
    yield '\n        </article>\n    </div>\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&9=57&11=59&14=61&18=63&19=66&22=69&23=71&29=74&30=76&31=79&35=82&38=88&43=91&46=94&50=99&54=102&59=107&62=110&65=113&68=116&71=119&74=122&77=125&80=128&83=131&86=134&89=137&92=140&95=143&98=146&106=153&109=155&119=162&120=164&121=167&124=169&125=173'