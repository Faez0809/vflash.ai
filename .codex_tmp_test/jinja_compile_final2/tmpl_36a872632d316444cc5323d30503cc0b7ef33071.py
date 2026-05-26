from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'manual.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'manual.html')
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
    yield 'User Manual | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    pass
    yield '\n<section class="manual-page">\n    <div class="manual-hero">\n        <div class="manual-hero-copy">\n            <p class="manual-eyebrow">User manual</p>\n            <h1>Use vflash.ai in one clear study flow.</h1>\n            <p>Generate useful words, study them with cards, review on time, and use quizzes to measure progress.</p>\n            <div class="manual-flow-strip">\n                <span>Generate</span>\n                <span>Word Lists</span>\n                <span>Flashcards</span>\n                <span>Review</span>\n                <span>Quiz</span>\n            </div>\n        </div>\n        <div class="manual-actions">\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '#generate-section" class="manual-primary">Generate first words</a>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '" class="manual-secondary">Back to dashboard</a>\n            <div class="manual-side-note">\n                <p>Best first step</p>\n                <strong>Create a word set, then open flashcards.</strong>\n            </div>\n        </div>\n    </div>\n\n    <div class="manual-grid">\n        <article class="manual-card">\n            <div class="manual-card-top">\n                <span class="manual-icon-shell"><span class="material-symbols-outlined">neurology</span></span>\n                <span class="manual-step-number">01</span>\n            </div>\n            <h2>Generate words</h2>\n            <p>Choose a topic and difficulty, then create your first study set.</p>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
    yield '#generate-section">Open generator</a>\n        </article>\n\n        <article class="manual-card">\n            <div class="manual-card-top">\n                <span class="manual-icon-shell"><span class="material-symbols-outlined">style</span></span>\n                <span class="manual-step-number">02</span>\n            </div>\n            <h2>Open Word Lists</h2>\n            <p>Your saved words appear here with meanings, notes, and learning status.</p>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words', _block_vars=_block_vars))
    yield '">Open Word Lists</a>\n        </article>\n\n        <article class="manual-card">\n            <div class="manual-card-top">\n                <span class="manual-icon-shell"><span class="material-symbols-outlined">amp_stories</span></span>\n                <span class="manual-step-number">03</span>\n            </div>\n            <h2>Study with flashcards</h2>\n            <p>Go word by word and mark each one as learned, known, or difficult.</p>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards', _block_vars=_block_vars))
    yield '">Open flashcards</a>\n        </article>\n\n        <article class="manual-card">\n            <div class="manual-card-top">\n                <span class="manual-icon-shell"><span class="material-symbols-outlined">history</span></span>\n                <span class="manual-step-number">04</span>\n            </div>\n            <h2>Review regularly</h2>\n            <p>Come back to due words so they stay in memory longer.</p>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review', _block_vars=_block_vars))
    yield '">Open review</a>\n        </article>\n\n        <article class="manual-card">\n            <div class="manual-card-top">\n                <span class="manual-icon-shell"><span class="material-symbols-outlined">quiz</span></span>\n                <span class="manual-step-number">05</span>\n            </div>\n            <h2>Take quizzes</h2>\n            <p>Check your accuracy after studying and track your progress.</p>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz', _block_vars=_block_vars))
    yield '">Open quiz</a>\n        </article>\n\n        <article class="manual-card">\n            <div class="manual-card-top">\n                <span class="manual-icon-shell"><span class="material-symbols-outlined">person</span></span>\n                <span class="manual-step-number">06</span>\n            </div>\n            <h2>Adjust your profile</h2>\n            <p>Set your nickname, daily goal, and study focus for a cleaner routine.</p>\n            <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile', _block_vars=_block_vars))
    yield '">Open profile</a>\n        </article>\n    </div>\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&21=37&22=39&38=41&48=43&58=45&68=47&78=49&88=51'