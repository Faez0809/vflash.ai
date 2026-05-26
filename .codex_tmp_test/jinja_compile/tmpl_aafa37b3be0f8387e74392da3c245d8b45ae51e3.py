from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'admin_login.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    pass
    parent_template = environment.get_template('base.html', 'admin_login.html')
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
    yield 'Admin Login | vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_url_for = resolve('url_for')
    l_0_admin_email = resolve('admin_email')
    pass
    yield '\n<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>\n<style>\n    .page-shell { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }\n</style>\n<div class="tw-scope admin-login-shell min-h-screen bg-[#121414] text-[#e2e2e2] font-[\'Inter\'] flex items-center justify-center px-4 sm:px-6 py-8 sm:py-12">\n    <div class="auth-mobile-bar absolute top-4 left-4 right-4">\n        <a class="nav-profile-link" href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_login', _block_vars=_block_vars))
    yield '" aria-label="Admin Account">\n            <span class="nav-profile-name">Admin</span>\n            <span class="nav-profile-avatar" aria-hidden="true">A</span>\n        </a>\n        <div class="nav-menu" data-nav-menu>\n            <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n            </button>\n            <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person</span><span>User Login</span></a>\n                <a href="'
    yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup', _block_vars=_block_vars))
    yield '"><span class="material-symbols-outlined">person_add</span><span>Sign up</span></a>\n            </div>\n        </div>\n    </div>\n    <div class="w-full max-w-md rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(30,32,32,0.98),rgba(18,20,20,0.98))] p-8 shadow-[0_48px_48px_-12px_rgba(45,95,93,0.18)]">\n        <p class="text-[10px] uppercase tracking-[0.22em] text-[#9dd0cd] font-bold mb-3">Admin</p>\n        <h1 class="font-[\'Manrope\'] text-3xl font-extrabold tracking-tight mb-2">Secure control panel access</h1>\n        <p class="text-sm text-[#c0c8c7] leading-relaxed mb-6">Only the configured administrator email can open this area.</p>\n\n        <form method="post" class="space-y-4">\n            <div class="space-y-2">\n                <label for="email" class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold block">Admin Email</label>\n                <input id="email" name="email" type="email" autocomplete="username" class="w-full rounded-2xl border border-white/10 bg-[#0d0f0f] px-4 py-3 text-sm text-[#e2e2e2] outline-none focus:border-[#9dd0cd]/50 focus:ring-1 focus:ring-[#9dd0cd]/50" placeholder="'
    yield escape((undefined(name='admin_email') if l_0_admin_email is missing else l_0_admin_email))
    yield '">\n            </div>\n            <div class="space-y-2">\n                <label for="password" class="text-[10px] uppercase tracking-[0.18em] text-[#8a9291] font-bold block">Password</label>\n                <input id="password" name="password" type="password" autocomplete="current-password" class="w-full rounded-2xl border border-white/10 bg-[#0d0f0f] px-4 py-3 text-sm text-[#e2e2e2] outline-none focus:border-[#9dd0cd]/50 focus:ring-1 focus:ring-[#9dd0cd]/50" placeholder="Enter admin password">\n            </div>\n            <button type="submit" class="w-full rounded-2xl bg-gradient-to-r from-[#9dd0cd] to-[#2d5f5d] px-6 py-3.5 text-sm font-[\'Manrope\'] font-extrabold uppercase tracking-[0.18em] text-[#00201f] border-none cursor-pointer">Open Admin Panel</button>\n        </form>\n    </div>\n</div>\n'

blocks = {'title': block_title, 'content': block_content}
debug_info = '1=12&3=17&5=27&12=38&21=40&22=42&34=44'