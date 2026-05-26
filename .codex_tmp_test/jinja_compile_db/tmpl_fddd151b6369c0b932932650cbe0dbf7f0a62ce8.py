from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'base.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_static_asset = resolve('static_asset')
    l_0_request = resolve('request')
    l_0_current_user = resolve('current_user')
    l_0_url_for = resolve('url_for')
    l_0_get_flashed_messages = resolve('get_flashed_messages')
    l_0_body_class = missing
    try:
        t_1 = environment.filters['lower']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'lower' found.")
    try:
        t_2 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_3 = environment.filters['tojson']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'tojson' found.")
    try:
        t_4 = environment.filters['trim']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'trim' found.")
    try:
        t_5 = environment.filters['upper']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'upper' found.")
    pass
    yield '<!doctype html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <title>'
    yield from context.blocks['title'][0](context)
    yield '</title>\n    <link rel="preconnect" href="https://fonts.googleapis.com">\n    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@700;800&display=swap" rel="stylesheet">\n    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">\n    <link rel="icon" href="data:,">\n    <link rel="preload" href="'
    yield escape(context.call((undefined(name='static_asset') if l_0_static_asset is missing else l_0_static_asset), 'style.css'))
    yield '" as="style">\n    <link rel="stylesheet" href="'
    yield escape(context.call((undefined(name='static_asset') if l_0_static_asset is missing else l_0_static_asset), 'style.css'))
    yield '">\n    <link rel="preload" href="'
    yield escape(context.call((undefined(name='static_asset') if l_0_static_asset is missing else l_0_static_asset), 'app.js'))
    yield '" as="script">\n</head>\n'
    l_0_body_class = ''
    context.vars['body_class'] = l_0_body_class
    context.exported_vars.add('body_class')
    yield '\n'
    if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') in ['login', 'signup', 'forgot_password']):
        pass
        yield '\n    '
        l_0_body_class = 'auth-page'
        context.vars['body_class'] = l_0_body_class
        context.exported_vars.add('body_class')
        yield '\n'
    elif (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'dashboard'):
        pass
        yield '\n    '
        l_0_body_class = 'dashboard-page'
        context.vars['body_class'] = l_0_body_class
        context.exported_vars.add('body_class')
        yield '\n'
    elif (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'search_word'):
        pass
        yield '\n    '
        l_0_body_class = 'search-page tw-dark-page'
        context.vars['body_class'] = l_0_body_class
        context.exported_vars.add('body_class')
        yield '\n'
    elif (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') in ['words', 'flashcards', 'flashcards_session', 'review', 'review_session', 'quiz', 'quiz_start', 'profile', 'admin_dashboard', 'user_manual']):
        pass
        yield '\n    '
        l_0_body_class = 'tw-dark-page'
        context.vars['body_class'] = l_0_body_class
        context.exported_vars.add('body_class')
        yield '\n'
    yield '\n<body class="'
    yield escape((undefined(name='body_class') if l_0_body_class is missing else l_0_body_class))
    yield '" '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
        pass
        yield 'data-usage-endpoint="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'usage_ping'))
        yield '" data-quiz-warmup-endpoint="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_warmup'))
        yield '"'
    yield '>\n    <!--app-shell-start-->\n    <div data-app-shell data-body-class="'
    yield escape((undefined(name='body_class') if l_0_body_class is missing else l_0_body_class))
    yield '" '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
        pass
        yield 'data-usage-endpoint="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'usage_ping'))
        yield '" data-quiz-warmup-endpoint="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz_warmup'))
        yield '"'
    yield '>\n    '
    if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') not in ['login', 'signup', 'forgot_password', 'dashboard', 'words', 'flashcards', 'flashcards_session', 'review', 'review_session', 'quiz', 'quiz_start', 'profile', 'admin_dashboard', 'admin_logout', 'admin_update_user_restriction', 'user_manual', 'search_word']):
        pass
        yield '\n    <header class="site-header">\n        <div class="site-header-glow"></div>\n        <div class="container nav-shell">\n            <div class="brand-lockup">\n                <a class="brand" href="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'index'))
        yield '">vflash.ai</a>\n                '
        if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
            pass
            yield '\n                    <span class="brand-tag">AI vocabulary trainer</span>\n                '
        yield '\n            </div>\n            <form class="nav-search" action="'
        yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'search_word'))
        yield '" method="get" data-async-page="true" data-loading-messages=\'["Searching...","Checking database...","Generating word details..."]\'>\n                <span class="material-symbols-outlined" aria-hidden="true">search</span>\n                <input type="search" name="q" placeholder="Search any word, phrase, or topic" data-placeholder-full="Search any word, phrase, or topic" data-placeholder-compact="Search word, phrase, or topic" aria-label="Search any word, phrase, or topic" value="'
        yield escape((context.call(environment.getattr(environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'args'), 'get'), 'q', '') if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'search_word') else ''))
        yield '" maxlength="60" autocomplete="off">\n            </form>\n            <nav class="nav-links nav-links-primary nav-links-primary-shell">\n                '
        if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
            pass
            yield '\n                    <button type="button" class="nav-chat-trigger nav-header-icon" data-feedback-open-chat aria-label="Message Faez" title="Message Faez">\n                        <span class="feedback-fab-icon"><span class="material-symbols-outlined">forum</span></span>\n                    </button>\n                    <a class="'
            yield escape(('is-active' if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'dashboard') else ''))
            yield '" href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'dashboard'))
            yield '">Dashboard</a>\n                    <a class="'
            yield escape(('is-active' if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') in ['flashcards', 'flashcards_session']) else ''))
            yield '" href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards'))
            yield '">Flashcards</a>\n                    <a class="'
            yield escape(('is-active' if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'review') else ''))
            yield '" href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review'))
            yield '">Review</a>\n                    <a class="'
            yield escape(('is-active' if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') in ['quiz', 'quiz_start']) else ''))
            yield '" href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz'))
            yield '">Quiz</a>\n                    '
            if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
                pass
                yield '\n                        <a class="'
                yield escape(('is-active' if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'admin_dashboard') else ''))
                yield '" href="'
                yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard'))
                yield '">Admin Panel</a>\n                    '
            yield '\n                    <a class="nav-profile-link '
            yield escape(('is-active' if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') == 'profile') else ''))
            yield '" href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile'))
            yield '" aria-label="Profile">\n                        <span class="nav-profile-name">'
            yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))
            yield '</span>\n                        <span class="nav-profile-avatar" aria-hidden="true">'
            yield escape(t_5(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name')[:1]))
            yield '</span>\n                    </a>\n                    <div class="nav-menu" data-nav-menu>\n                        <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                            <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                        </button>\n                        <div class="nav-menu-panel nav-menu-panel-mobile" aria-hidden="true">\n                            <span class="nav-menu-email">'
            yield escape(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))
            yield '</span>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'profile'))
            yield '"><span class="material-symbols-outlined">person</span><span>Profile</span></a>\n                            '
            if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_admin'):
                pass
                yield '\n                                <a href="'
                yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'admin_dashboard'))
                yield '"><span class="material-symbols-outlined">shield_person</span><span>Admin Panel</span></a>\n                            '
            yield '\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'words'))
            yield '"><span class="material-symbols-outlined">style</span><span>My Words</span></a>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'flashcards'))
            yield '"><span class="material-symbols-outlined">amp_stories</span><span>Flashcards</span></a>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'quiz'))
            yield '"><span class="material-symbols-outlined">quiz</span><span>Quiz</span></a>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'review'))
            yield '"><span class="material-symbols-outlined">rule</span><span>Review</span></a>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'logout'))
            yield '"><span class="material-symbols-outlined">logout</span><span>Sign Out</span></a>\n                        </div>\n                    </div>\n                '
        else:
            pass
            yield '\n                    <button type="button" class="nav-chat-trigger nav-header-icon" data-feedback-open-chat aria-label="Message Faez" title="Message Faez">\n                        <span class="feedback-fab-icon"><span class="material-symbols-outlined">forum</span></span>\n                    </button>\n                    <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login'))
            yield '">Login</a>\n                    <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup'))
            yield '">Sign up</a>\n                    <a class="nav-profile-link" href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login'))
            yield '" aria-label="Account">\n                        <span class="nav-profile-name">Account</span>\n                        <span class="nav-profile-avatar nav-profile-avatar-guest" aria-hidden="true">\n                            <span class="material-symbols-outlined">person</span>\n                        </span>\n                    </a>\n                    <div class="nav-menu" data-nav-menu>\n                        <button type="button" class="nav-menu-trigger" aria-label="Open navigation menu" aria-expanded="false" title="More options">\n                            <span class="nav-menu-icon" aria-hidden="true">&#9776;</span>\n                        </button>\n                        <div class="nav-menu-panel" aria-hidden="true">\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'login'))
            yield '"><span class="material-symbols-outlined">person</span><span>Login</span></a>\n                            <a href="'
            yield escape(context.call((undefined(name='url_for') if l_0_url_for is missing else l_0_url_for), 'signup'))
            yield '"><span class="material-symbols-outlined">person_add</span><span>Sign up</span></a>\n                        </div>\n                    </div>\n                '
        yield '\n            </nav>\n        </div>\n    </header>\n    '
    yield '\n\n    <main class="'
    if (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') in ['login', 'signup', 'forgot_password']):
        pass
        yield 'auth-page-shell'
    elif (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') in ['dashboard', 'words', 'flashcards', 'flashcards_session', 'review', 'review_session', 'quiz', 'quiz_start', 'profile', 'admin_dashboard', 'user_manual', 'search_word']):
        pass
        yield 'dashboard-page-shell'
    else:
        pass
        yield 'container page-shell'
    yield '">\n        '
    l_1_messages = context.call((undefined(name='get_flashed_messages') if l_0_get_flashed_messages is missing else l_0_get_flashed_messages), with_categories=True)
    pass
    yield '\n            '
    if l_1_messages:
        pass
        yield '\n                <section class="flash-stack">\n                    '
        for (l_2_category, l_2_message) in l_1_messages:
            _loop_vars = {}
            pass
            yield '\n                        <div class="flash flash-'
            yield escape(l_2_category)
            yield '">'
            yield escape(l_2_message)
            yield '</div>\n                    '
        l_2_category = l_2_message = missing
        yield '\n                </section>\n            '
    yield '\n        '
    l_1_messages = missing
    yield '\n\n        '
    yield from context.blocks['content'][0](context)
    yield '\n    </main>\n\n    <div class="loading-overlay" data-loading-overlay aria-hidden="true">\n        <div class="loading-overlay-backdrop"></div>\n        <div class="loading-overlay-card" role="status" aria-live="polite" aria-atomic="true">\n            <div class="loading-overlay-spinner" aria-hidden="true"></div>\n            <p class="loading-overlay-label">vflash.ai</p>\n            <h2 class="loading-overlay-title" data-loading-status>Loading...</h2>\n            <p class="loading-overlay-copy">Please stay here while we prepare your content.</p>\n        </div>\n    </div>\n    </div>\n    <!--app-shell-end-->\n\n\n    <script src="'
    yield escape(context.call((undefined(name='static_asset') if l_0_static_asset is missing else l_0_static_asset), 'app.js'))
    yield '" defer></script>\n    <style>\n        body {\n            padding-bottom: max(0px, env(safe-area-inset-bottom));\n        }\n    </style>\n    <script type="text/javascript">\n        var Tawk_API = window.Tawk_API = window.Tawk_API || {};\n        var Tawk_LoadStart = window.Tawk_LoadStart = new Date();\n        var __tawkIsLoaded = false;\n\n        '
    if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated'):
        pass
        yield '\n        (function () {\n            var visitorName = '
        yield escape(t_3(context.eval_ctx, t_4(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'display_name'))))
        yield ';\n            var visitorEmail = '
        yield escape(t_3(context.eval_ctx, t_1(t_4(environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'email')))))
        yield ';\n            var emailPattern = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n            var visitor = { name: visitorName };\n            if (emailPattern.test(visitorEmail)) {\n                visitor.email = visitorEmail;\n            }\n            Tawk_API.visitor = visitor;\n        })();\n        '
    yield '\n\n        function waitForTawk(callback) {\n            if (\n                typeof Tawk_API !== "undefined" &&\n                Tawk_API.onLoad &&\n                typeof Tawk_API.showWidget === "function" &&\n                typeof Tawk_API.maximize === "function"\n            ) {\n                callback();\n            } else {\n                setTimeout(function () { waitForTawk(callback); }, 100);\n            }\n        }\n\n        function openChat() {\n            waitForTawk(function () {\n                try {\n                    Tawk_API.showWidget();\n                    Tawk_API.maximize();\n                } catch (e) {\n                    console.error("Tawk error:", e);\n                }\n            });\n        }\n\n        Tawk_API.onLoad = function () {\n            __tawkIsLoaded = true;\n\n            if (typeof Tawk_API.hideWidget === "function") {\n                Tawk_API.hideWidget();\n            }\n\n            if (typeof Tawk_API.setAttributes === "function") {\n                Tawk_API.setAttributes(\n                    {\n                        "visitor-role": '
    yield escape(t_3(context.eval_ctx, ('authenticated-user' if environment.getattr((undefined(name='current_user') if l_0_current_user is missing else l_0_current_user), 'is_authenticated') else 'guest')))
    yield ',\n                        "visitor-page": '
    yield escape(t_3(context.eval_ctx, t_2(context.eval_ctx, (environment.getattr((undefined(name='request') if l_0_request is missing else l_0_request), 'endpoint') or 'unknown'), '_', '-')))
    yield '\n                    },\n                    function (error) {\n                        if (error && window.console && typeof window.console.warn === "function") {\n                            window.console.warn("Tawk visitor metadata failed.", error);\n                        }\n                    }\n                );\n            }\n\n        };\n\n        if (!window.__tawkWidgetLoaded && !document.getElementById("tawkto-script")) {\n            window.__tawkWidgetLoaded = true;\n            (function () {\n                var s1 = document.createElement("script");\n                var s0 = document.getElementsByTagName("script")[0];\n                s1.id = "tawkto-script";\n                s1.async = true;\n                s1.src = "https://embed.tawk.to/69d4db892767f61c30801122/1jljnj4bo";\n                s1.charset = "UTF-8";\n                s1.setAttribute("crossorigin", "*");\n                s0.parentNode.insertBefore(s1, s0);\n            })();\n        }\n\n        window.openChat = openChat;\n        window.waitForTawk = waitForTawk;\n    </script>\n</body>\n</html>'

def block_title(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield 'vflash.ai'

def block_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

blocks = {'title': block_title, 'content': block_content}
debug_info = '6=48&12=50&13=52&14=54&16=56&17=60&18=63&19=67&20=70&21=74&22=77&23=81&24=84&26=89&28=99&29=109&34=112&35=114&39=118&41=120&44=122&48=125&49=129&50=133&51=137&52=141&53=144&55=149&56=153&57=155&64=157&65=159&66=161&67=164&69=167&70=169&71=171&72=173&73=175&80=180&81=182&82=184&93=186&94=188&103=192&105=205&107=208&108=212&114=221&130=223&141=225&143=228&144=230&188=233&189=235&6=238&114=248'