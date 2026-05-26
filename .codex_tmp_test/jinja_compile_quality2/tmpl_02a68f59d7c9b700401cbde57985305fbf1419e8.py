from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'error.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'error.html')
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
    l_0_error_title = resolve('error_title')
    pass
    yield escape((undefined(name='error_title') if l_0_error_title is missing else l_0_error_title))
    yield ' | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_error_code = resolve('error_code')
    l_0_error_title = resolve('error_title')
    l_0_error_message = resolve('error_message')
    l_0_current_user = resolve('current_user')
    l_0_url_for = resolve('url_for')
    pass
    yield '\n<section class="error-page">\n    <div class="panel error-panel">\n        <p class="error-eyebrow">\n            Error '
    yield escape((undefined(name='error_code') if l_0_error_code is missing else l_0_error_code))
    yield '\n        </p>\n        <h1 class="error-title">'
    yield escape((undefined(name='error_title') if l_0_error_title is missing else l_0_error_title))
    yield '</h1>\n        <p class="error-copy">'
    yield escape((undefined(name='error_message') if l_0_error_message is missing else l_0_error_message))
    yield '</p>\n        <div class="error-actions">\n            '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
        pass
        yield '\n                <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard', _block_vars=_block_vars))
        yield '" class="error-action error-action-primary">Return to dashboard</a>\n            '
    else:
        pass
        yield '\n                <a href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars))
        yield '" class="error-action error-action-primary">Return to login</a>\n            '
    yield '\n            <a href="'
    yield escape((context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'user_manual', _block_vars=_block_vars) if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated') else context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars)))
    yield '" class="error-action error-action-secondary">\n                '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
        pass
        yield 'Open user manual'
    else:
        pass
        yield 'Open sign in'
    yield '\n            </a>\n        </div>\n    </div>\n</section>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=29&9=43&11=45&12=47&14=49&15=52&17=57&19=60&20=62'