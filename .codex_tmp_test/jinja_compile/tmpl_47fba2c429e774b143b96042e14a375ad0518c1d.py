from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'signup.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'signup.html')
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
    yield 'Create account | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    pass
    yield '\n<section class="auth-shell auth-shell-split">\n    <div class="auth-pane auth-pane-form">\n        <div class="auth-mobile-bar">\n            <a class="nav-profile-link" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup', _block_vars=_block_vars))
    yield '" aria-label="Account">\n                <span class="nav-profile-name">Account</span>\n                <span class="nav-profile-avatar nav-profile-avatar-guest" aria-hidden="true"><span class="material-symbols-outlined">person</span></span>\n            </a>\n            <div class="nav-menu" data-nav-menu>\n                <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                    <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                </button>\n                <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                    <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person</span><span>Login</span></a>\n                    <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person_add</span><span>Sign up</span></a>\n                </div>\n            </div>\n        </div>\n        <div class="auth-brand">vflash.ai</div>\n        <div class="auth-form-wrap">\n            <header class="auth-copy">\n                <h1>Create your learning workspace</h1>\n                <p>Set up your account and start building stronger vocabulary with structured daily practice.</p>\n            </header>\n            <form method="post" class="auth-form-grid">\n                <div class="auth-field">\n                    <label for="nickname">Nickname</label>\n                    <input id="nickname" name="nickname" type="text" placeholder="Choose the name you want to use" required>\n                </div>\n\n                <div class="auth-field">\n                    <label for="email">Email address</label>\n                    <input id="email" name="email" type="email" placeholder="Enter your email address" required>\n                </div>\n\n                <div class="auth-field">\n                    <label for="password">Password</label>\n                    <div class="auth-field-control">\n                        <input id="password" name="password" type="password" placeholder="Create a secure password" required>\n                        <button type="button" class="password-toggle" data-password-toggle-button="password" aria-label="Show password" aria-pressed="false">\n                            <span data-eye-open aria-hidden="true">\n                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n                                    <path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z"></path>\n                                    <circle cx="12" cy="12" r="3"></circle>\n                                </svg>\n                            </span>\n                            <span data-eye-closed aria-hidden="true" style="display:none;">\n                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n                                    <path d="M3 3l18 18"></path>\n                                    <path d="M10.6 10.7A3 3 0 0 0 13.4 13.5"></path>\n                                    <path d="M9.9 5.1A10.9 10.9 0 0 1 12 5c6.4 0 10 7 10 7a18.7 18.7 0 0 1-4.2 4.9"></path>\n                                    <path d="M6.6 6.7A18.6 18.6 0 0 0 2 12s3.6 7 10 7a10.7 10.7 0 0 0 5-.9"></path>\n                                </svg>\n                            </span>\n                        </button>\n                    </div>\n                </div>\n\n                <div class="auth-field">\n                    <label for="confirm_password">Confirm password</label>\n                    <div class="auth-field-control">\n                        <input id="confirm_password" name="confirm_password" type="password" placeholder="Re-enter your password" required>\n                        <button type="button" class="password-toggle" data-password-toggle-button="confirm_password" aria-label="Show password" aria-pressed="false">\n                            <span data-eye-open aria-hidden="true">\n                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n                                    <path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z"></path>\n                                    <circle cx="12" cy="12" r="3"></circle>\n                                </svg>\n                            </span>\n                            <span data-eye-closed aria-hidden="true" style="display:none;">\n                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n                                    <path d="M3 3l18 18"></path>\n                                    <path d="M10.6 10.7A3 3 0 0 0 13.4 13.5"></path>\n                                    <path d="M9.9 5.1A10.9 10.9 0 0 1 12 5c6.4 0 10 7 10 7a18.7 18.7 0 0 1-4.2 4.9"></path>\n                                    <path d="M6.6 6.7A18.6 18.6 0 0 0 2 12s3.6 7 10 7a10.7 10.7 0 0 0 5-.9"></path>\n                                </svg>\n                            </span>\n                        </button>\n                    </div>\n                </div>\n\n                <button type="submit" class="auth-submit">Create account</button>\n            </form>\n            <p class="form-footer auth-footer-link">Already have an account? <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars))
    yield '">Sign in</a></p>\n        </div>\n        <footer class="auth-meta">\n            <span>vflash.ai - Flashcard-based vocabulary learning - by Faez Mahmud</span>\n        </footer>\n    </div>\n\n    <aside class="auth-pane auth-pane-feature">\n        <div class="auth-feature-surface">\n            <span class="auth-eyebrow">Built for retention</span>\n            <h2>Learn new words through structured flashcard practice.</h2>\n            <p>Create your account, organize your learning, and build a vocabulary routine you can maintain with confidence.</p>\n            <div class="auth-feature-grid">\n                <article class="auth-feature-card">\n                    <span class="auth-feature-label">Visible progress</span>\n                    <strong>Know what to study next</strong>\n                    <p>See which words to learn, which flashcards to review, and where your retention is improving.</p>\n                </article>\n                <article class="auth-feature-card">\n                    <span class="auth-feature-label">Flexible practice</span>\n                    <strong>Flashcards, quizzes, and review</strong>\n                    <p>Study new vocabulary, revisit difficult words, and keep your learning moving forward.</p>\n                </article>\n            </div>\n        </div>\n    </aside>\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&9=37&18=39&19=41&88=43'