from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'login.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'login.html')
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
    yield 'Sign in | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_email_value = resolve('email_value')
    l_0_login_error = resolve('login_error')
    l_0_show_forgot_password = resolve('show_forgot_password')
    pass
    yield '\n<section class="auth-shell auth-shell-split">\n    <div class="auth-pane auth-pane-form">\n        <div class="auth-mobile-bar">\n            <a class="nav-profile-link" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars))
    yield '" aria-label="Account">\n                <span class="nav-profile-name">Account</span>\n                <span class="nav-profile-avatar nav-profile-avatar-guest" aria-hidden="true"><span class="material-symbols-outlined">person</span></span>\n            </a>\n            <div class="nav-menu" data-nav-menu>\n                <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                    <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                </button>\n                <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                    <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person</span><span>Login</span></a>\n                    <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person_add</span><span>Sign up</span></a>\n                </div>\n            </div>\n        </div>\n        <div class="auth-brand">vflash.ai</div>\n        <div class="auth-form-wrap">\n            <header class="auth-copy">\n                <h1>Sign in to your study workspace</h1>\n                <p>Pick up your flashcards, reviews, and vocabulary progress in one focused place.</p>\n            </header>\n            <form method="post" class="auth-form-grid">\n                <div class="auth-field">\n                    <label for="email">Email address</label>\n                    <input id="email" name="email" type="email" placeholder="Enter your email address" value="'
    yield escape(((undefined(name='email_value') if l_0_email_value is missing else l_0_email_value) or ''))
    yield '" required>\n                </div>\n\n                <div class="auth-field">\n                    <label for="password">Password</label>\n                    <div class="auth-field-control">\n                        <input id="password" name="password" type="password" placeholder="Enter your password" required>\n                        <button type="button" class="password-toggle" data-password-toggle-button="password" aria-label="Show password" aria-pressed="false">\n                            <span data-eye-open aria-hidden="true">\n                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n                                    <path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z"></path>\n                                    <circle cx="12" cy="12" r="3"></circle>\n                                </svg>\n                            </span>\n                            <span data-eye-closed aria-hidden="true" style="display:none;">\n                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n                                    <path d="M3 3l18 18"></path>\n                                    <path d="M10.6 10.7A3 3 0 0 0 13.4 13.5"></path>\n                                    <path d="M9.9 5.1A10.9 10.9 0 0 1 12 5c6.4 0 10 7 10 7a18.7 18.7 0 0 1-4.2 4.9"></path>\n                                    <path d="M6.6 6.7A18.6 18.6 0 0 0 2 12s3.6 7 10 7a10.7 10.7 0 0 0 5-.9"></path>\n                                </svg>\n                            </span>\n                        </button>\n                    </div>\n                    '
    if (undefined(name='login_error') if l_0_login_error is missing else l_0_login_error):
        pass
        yield '\n                    <p class="auth-inline-error">'
        yield escape((undefined(name='login_error') if l_0_login_error is missing else l_0_login_error))
        yield '</p>\n                    '
    yield '\n                    '
    if (undefined(name='show_forgot_password') if l_0_show_forgot_password is missing else l_0_show_forgot_password):
        pass
        yield '\n                    <p class="auth-inline-action">\n                        <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'forgot_password', email=((undefined(name='email_value') if l_0_email_value is missing else l_0_email_value) or ''), _block_vars=_block_vars))
        yield '">Forgot your password?</a>\n                    </p>\n                    '
    yield '\n                </div>\n\n                <button type="submit" class="auth-submit">Sign in</button>\n            </form>\n            <p class="form-footer auth-footer-link">New to vflash.ai? <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup', _block_vars=_block_vars))
    yield '">Create account</a></p>\n        </div>\n        <footer class="auth-meta">\n            <span>vflash.ai - Flashcard-based vocabulary learning - by Faez Mahmud</span>\n        </footer>\n    </div>\n\n    <aside class="auth-pane auth-pane-feature">\n        <div class="auth-feature-surface">\n            <span class="auth-eyebrow">Focused flashcards</span>\n            <h2>Review vocabulary with clarity and consistency.</h2>\n            <p>vflash.ai keeps your flashcards, practice sessions, and progress in one streamlined workspace.</p>\n            <div class="auth-feature-grid">\n                <article class="auth-feature-card">\n                    <span class="auth-feature-label">Clear workflow</span>\n                    <strong>Create, study, and review flashcards</strong>\n                    <p>Move from new vocabulary to active recall without breaking your learning flow.</p>\n                </article>\n                <article class="auth-feature-card">\n                    <span class="auth-feature-label">Targeted practice</span>\n                    <strong>Study the words that matter most</strong>\n                    <p>Keep each session aligned with your goals, weak points, and review priorities.</p>\n                </article>\n            </div>\n        </div>\n    </aside>\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&9=40&18=42&19=44&32=46&56=48&57=51&59=54&61=57&68=60'