const appShellState = {
    cache: new Map(),
    pendingPrefetches: new Map(),
    navigationToken: 0,
    cacheTtlMs: 30000,
};

document.addEventListener("DOMContentLoaded", () => {
    initImmediateControlFeedback();
    initInstantNavigation();
    bootstrapPage({ initialLoad: true });
});

function bootstrapPage({ initialLoad = false } = {}) {
    const shouldAutofocus = document.body.classList.contains("auth-page");
    const firstInput = shouldAutofocus ? document.querySelector("input, textarea, select") : null;
    if (initialLoad && firstInput) {
        firstInput.focus();
    }

    initFlashMessages();
    initNavMenu();
    initPasswordToggles();
    initAsyncPageForms();
    initAutoSubmitControls();
    initAjaxDifficultForms();
    initResponsiveSearchPlaceholders();
    initFlashcards();
    initQuizUX();
    initUsageTracking();
    initDashboardWarmups();
    initFeedbackAssistant();
    initVocabularyInputs();
    initSearchSuggestions();
    prefetchVisibleNavigationLinks();
}

function initImmediateControlFeedback() {
    if (window.__immediateControlFeedbackBound) {
        return;
    }

    window.__immediateControlFeedbackBound = true;
    const interactiveSelector = "button, a[href], input[type='button'], input[type='submit'], summary, label";

    function clearActive(el) {
        if (!el) {
            return;
        }
        window.setTimeout(() => {
            el.classList.remove("is-immediate-active");
        }, 130);
    }

    document.addEventListener("pointerdown", (event) => {
        const control = event.target.closest(interactiveSelector);
        if (!control || control.matches("[disabled], [aria-disabled='true']")) {
            return;
        }

        control.classList.add("is-immediate-active");
    }, true);

    ["pointerup", "pointercancel", "pointerleave", "click"].forEach((eventName) => {
        document.addEventListener(eventName, (event) => {
            clearActive(event.target.closest(interactiveSelector));
        }, true);
    });

    document.addEventListener("submit", (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) {
            return;
        }

        form.classList.add("is-submitting-immediate");
        form.setAttribute("aria-busy", "true");
        const submitter = event.submitter || form.querySelector("button[type='submit'], input[type='submit']");
        if (submitter) {
            submitter.classList.add("is-submitting-immediate");
        }
    }, true);
}

window.addEventListener("pageshow", () => {
    hideLoadingOverlay();
    stopPageSkeleton();
});

function getCurrentShell() {
    return document.querySelector("[data-app-shell]");
}

function normalizeAppUrl(input) {
    return new URL(input, window.location.href);
}

function isSameAppUrl(url) {
    return url.origin === window.location.origin;
}

function getCacheKey(url, method = "GET") {
    return `${method.toUpperCase()}:${url.pathname}${url.search}`;
}

function pruneShellCache() {
    const now = Date.now();
    appShellState.cache.forEach((entry, key) => {
        if ((now - entry.cachedAt) > appShellState.cacheTtlMs) {
            appShellState.cache.delete(key);
        }
    });
}

function updateBodyFromShell(shell) {
    if (!shell) {
        return;
    }

    document.body.className = shell.dataset.bodyClass || "";

    delete document.body.dataset.usageEndpoint;
    delete document.body.dataset.quizWarmupEndpoint;

    ["usageEndpoint", "quizWarmupEndpoint"].forEach((name) => {
        if (shell.dataset[name]) {
            document.body.dataset[name] = shell.dataset[name];
        }
    });
}

function startPageSkeleton() {
    return;
}

function stopPageSkeleton() {
    return;
}

function handleNavigationError() {
    stopPageSkeleton();
    hideLoadingOverlay();
    showAjaxMessage("We couldn't load that page instantly, so we kept the current view.", "error");
}

function parseHtmlPayload(html, fallbackUrl) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const shell = doc.querySelector("[data-app-shell]");
    if (!shell) {
        return null;
    }

    return {
        ok: true,
        path: fallbackUrl.pathname + fallbackUrl.search,
        title: doc.title || document.title,
        shell: shell.outerHTML,
    };
}

async function readFragmentPayload(response, requestUrl) {
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        return response.json();
    }

    const html = await response.text();
    const parsed = parseHtmlPayload(html, normalizeAppUrl(response.url || requestUrl.toString()));
    if (!parsed) {
        throw new Error("Missing app shell");
    }
    return parsed;
}

async function fetchShellPayload(url, { method = "GET", body = null, force = false } = {}) {
    const resolvedUrl = normalizeAppUrl(url);
    const normalizedMethod = method.toUpperCase();

    pruneShellCache();

    if (normalizedMethod === "GET" && !force) {
        const cached = appShellState.cache.get(getCacheKey(resolvedUrl, normalizedMethod));
        if (cached && (Date.now() - cached.cachedAt) <= appShellState.cacheTtlMs) {
            return cached.payload;
        }
    }

    const response = await fetch(resolvedUrl.toString(), {
        method: normalizedMethod,
        body,
        credentials: "same-origin",
        headers: {
            "X-App-Fragment": "1",
            "X-Requested-With": "XMLHttpRequest",
        },
    });

    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }

    const payload = await readFragmentPayload(response, resolvedUrl);
    if (normalizedMethod === "GET") {
        appShellState.cache.set(getCacheKey(resolvedUrl, normalizedMethod), {
            cachedAt: Date.now(),
            payload,
        });
    }

    return payload;
}

function runInjectedScripts(root) {
    root.querySelectorAll("script").forEach((oldScript) => {
        const newScript = document.createElement("script");
        newScript.async = false;
        Array.from(oldScript.attributes).forEach((attribute) => {
            newScript.setAttribute(attribute.name, attribute.value);
        });
        if (oldScript.textContent) {
            newScript.textContent = oldScript.textContent;
        }
        oldScript.replaceWith(newScript);
    });
}

function syncHeadAssets(nextDocument) {
    const currentHead = document.head;

    nextDocument.querySelectorAll('link[rel="stylesheet"], style[data-app-inline-style]').forEach((node) => {
        const signature = node.outerHTML;
        const exists = Array.from(currentHead.querySelectorAll('link[rel="stylesheet"], style[data-app-inline-style]'))
            .some((existing) => existing.outerHTML === signature);

        if (!exists) {
            currentHead.appendChild(node.cloneNode(true));
        }
    });
}

function applyPayloadToPage(payload, { url, historyMode = "push", preserveScroll = false } = {}) {
    const parser = new DOMParser();
    const fragmentDoc = parser.parseFromString(payload.shell, "text/html");
    const nextShell = fragmentDoc.querySelector("[data-app-shell]");
    const currentShell = getCurrentShell();

    if (!nextShell || !currentShell) {
        throw new Error("Shell swap failed");
    }

    syncHeadAssets(fragmentDoc);
    currentShell.replaceWith(nextShell);
    updateBodyFromShell(nextShell);
    document.title = payload.title || document.title;
    runInjectedScripts(nextShell);

    const targetUrl = normalizeAppUrl(url || payload.path || window.location.href);
    const historyState = { path: targetUrl.pathname + targetUrl.search };
    if (historyMode === "replace") {
        window.history.replaceState(historyState, "", targetUrl.toString());
    } else if (historyMode === "push") {
        window.history.pushState(historyState, "", targetUrl.toString());
    }

    bootstrapPage();
    stopPageSkeleton();
    hideLoadingOverlay();

    if (!preserveScroll) {
        if (targetUrl.hash) {
            const target = document.querySelector(targetUrl.hash);
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
                return;
            }
        }
        window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    }
}

async function navigateToAppUrl(url, options = {}) {
    const resolvedUrl = normalizeAppUrl(url);
    const nextToken = ++appShellState.navigationToken;

    if (!isSameAppUrl(resolvedUrl)) {
        window.location.assign(resolvedUrl.toString());
        return;
    }

    if ((resolvedUrl.pathname + resolvedUrl.search) === (window.location.pathname + window.location.search) && !options.force) {
        if (resolvedUrl.hash) {
            const target = document.querySelector(resolvedUrl.hash);
            target?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
        return;
    }

    startPageSkeleton();

    try {
        const payload = await fetchShellPayload(resolvedUrl, {
            method: options.method || "GET",
            body: options.body || null,
            force: Boolean(options.force),
        });

        if (nextToken !== appShellState.navigationToken) {
            return;
        }

        applyPayloadToPage(payload, {
            url: resolvedUrl,
            historyMode: options.historyMode || "push",
            preserveScroll: Boolean(options.preserveScroll),
        });
    } catch (error) {
        if (options.fallbackToHardNavigation !== false) {
            window.location.assign(resolvedUrl.toString());
            return;
        }
        handleNavigationError();
    }
}

function shouldInterceptLink(link, event) {
    if (!link || event.defaultPrevented) {
        return false;
    }

    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return false;
    }

    if (link.target && link.target !== "_self") {
        return false;
    }

    if (link.hasAttribute("download") || link.dataset.noSpa === "true") {
        return false;
    }

    const href = link.getAttribute("href") || "";
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) {
        return false;
    }

    const resolvedUrl = normalizeAppUrl(href);
    if (!isSameAppUrl(resolvedUrl)) {
        return false;
    }

    if (resolvedUrl.pathname.includes("/logout")) {
        return false;
    }

    return true;
}

function shouldPrefetchLink(link) {
    if (!link || link.dataset.noSpa === "true") {
        return false;
    }

    const href = link.getAttribute("href") || "";
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) {
        return false;
    }

    const resolvedUrl = normalizeAppUrl(href);
    if (!isSameAppUrl(resolvedUrl) || resolvedUrl.pathname.includes("/logout")) {
        return false;
    }

    return true;
}

function prefetchUrl(url) {
    const resolvedUrl = normalizeAppUrl(url);
    if (!isSameAppUrl(resolvedUrl)) {
        return;
    }

    const cacheKey = getCacheKey(resolvedUrl);
    const cached = appShellState.cache.get(cacheKey);
    if (cached && (Date.now() - cached.cachedAt) <= appShellState.cacheTtlMs) {
        return;
    }

    if (appShellState.pendingPrefetches.has(cacheKey)) {
        return;
    }

    const prefetchTask = fetchShellPayload(resolvedUrl).catch(() => null).finally(() => {
        appShellState.pendingPrefetches.delete(cacheKey);
    });

    appShellState.pendingPrefetches.set(cacheKey, prefetchTask);
}

function prefetchVisibleNavigationLinks() {
    document.querySelectorAll("a[href]").forEach((link) => {
        if (!shouldPrefetchLink(link)) {
            return;
        }

        const href = link.getAttribute("href") || "";
        const resolvedUrl = normalizeAppUrl(href);
        if (resolvedUrl.pathname === window.location.pathname && resolvedUrl.search === window.location.search) {
            return;
        }

        prefetchUrl(link.href);
    });
}

function initInstantNavigation() {
    if (window.__instantNavigationBound) {
        return;
    }

    window.__instantNavigationBound = true;
    window.navigateToAppUrl = navigateToAppUrl;

    document.addEventListener("click", (event) => {
        const link = event.target.closest("a[href]");
        if (!shouldInterceptLink(link, event)) {
            return;
        }

        event.preventDefault();
        navigateToAppUrl(link.href);
    });

    document.addEventListener("pointerenter", (event) => {
        const link = event.target.closest("a[href]");
        if (shouldPrefetchLink(link)) {
            prefetchUrl(link.href);
        }
    }, true);

    document.addEventListener("focusin", (event) => {
        const link = event.target.closest("a[href]");
        if (shouldPrefetchLink(link)) {
            prefetchUrl(link.href);
        }
    });

    window.addEventListener("popstate", () => {
        navigateToAppUrl(window.location.href, {
            historyMode: "replace",
            preserveScroll: true,
            force: true,
        });
    });

    if ("requestIdleCallback" in window) {
        window.requestIdleCallback(() => {
            prefetchVisibleNavigationLinks();
        }, { timeout: 1200 });
    } else {
        window.setTimeout(prefetchVisibleNavigationLinks, 350);
    }
}

function ensureFlashStack() {
    let flashStack = document.querySelector(".flash-stack");
    if (flashStack) {
        return flashStack;
    }

    const pageShell = document.querySelector(".page-shell, .dashboard-page-shell");
    if (!pageShell) {
        return null;
    }

    flashStack = document.createElement("section");
    flashStack.className = "flash-stack flash-stack-inline";
    pageShell.prepend(flashStack);
    return flashStack;
}

function showAjaxMessage(message, category = "info") {
    const flashStack = ensureFlashStack();
    if (!flashStack || !message) {
        return;
    }

    const flash = document.createElement("div");
    flash.className = `flash flash-${category}`;
    flash.textContent = message;
    flashStack.prepend(flash);

    window.setTimeout(() => {
        flash.classList.add("is-fading");
        window.setTimeout(() => flash.remove(), 320);
    }, 5500);
}

async function postJson(url, formData = null) {
    const options = {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    };

    if (formData) {
        options.body = formData;
    }

    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error("Request failed");
    }

    return response.json();
}

function initFlashMessages() {
    const flashes = document.querySelectorAll(".flash-stack .flash");
    if (!flashes.length) {
        return;
    }

    flashes.forEach((flash, index) => {
        window.setTimeout(() => {
            flash.classList.add("is-fading");
            window.setTimeout(() => flash.remove(), 320);
        }, 4400 + (index * 150));
    });
}

let loadingOverlayTimer = null;
let loadingOverlayIndex = 0;

function parseLoadingMessages(rawValue) {
    if (!rawValue) {
        return ["Loading..."];
    }

    try {
        const parsed = JSON.parse(rawValue);
        if (Array.isArray(parsed)) {
            const messages = parsed.map((item) => String(item || "").trim()).filter(Boolean);
            if (messages.length) {
                return messages;
            }
        }
    } catch (error) {
        // Fall through to a simple string-based fallback.
    }

    const fallbackMessages = String(rawValue)
        .split("|")
        .map((item) => item.trim())
        .filter(Boolean);
    return fallbackMessages.length ? fallbackMessages : ["Loading..."];
}

function showLoadingOverlay(messages = ["Loading..."]) {
    const overlay = document.querySelector("[data-loading-overlay]");
    const status = overlay?.querySelector("[data-loading-status]");
    if (!overlay || !status) {
        return;
    }

    const resolvedMessages = Array.isArray(messages) && messages.length ? messages : ["Loading..."];
    loadingOverlayIndex = 0;
    status.textContent = resolvedMessages[0];
    overlay.classList.add("is-visible");
    overlay.setAttribute("aria-hidden", "false");
    document.body.classList.add("is-busy");

    if (loadingOverlayTimer) {
        window.clearInterval(loadingOverlayTimer);
    }

    if (resolvedMessages.length > 1) {
        loadingOverlayTimer = window.setInterval(() => {
            loadingOverlayIndex = (loadingOverlayIndex + 1) % resolvedMessages.length;
            status.textContent = resolvedMessages[loadingOverlayIndex];
        }, 1400);
    }
}

function hideLoadingOverlay() {
    const overlay = document.querySelector("[data-loading-overlay]");
    if (loadingOverlayTimer) {
        window.clearInterval(loadingOverlayTimer);
        loadingOverlayTimer = null;
    }

    if (!overlay) {
        document.body.classList.remove("is-busy");
        return;
    }

    overlay.classList.remove("is-visible");
    overlay.setAttribute("aria-hidden", "true");
    document.body.classList.remove("is-busy");
}

function setFormPending(form, pending) {
    if (!form) {
        return;
    }

    form.classList.toggle("is-pending", pending);
    form.classList.toggle("is-submitting-immediate", pending);
    if (pending) {
        form.setAttribute("aria-busy", "true");
    } else {
        form.removeAttribute("aria-busy");
    }
    form.querySelectorAll("button[type='submit'], input[type='submit']").forEach((button) => {
        if (pending) {
            button.dataset.wasDisabled = button.disabled ? "true" : "false";
            button.disabled = true;
            button.classList.add("is-submitting-immediate");
            return;
        }

        if (button.dataset.wasDisabled !== "true") {
            button.disabled = false;
        }
        delete button.dataset.wasDisabled;
        button.classList.remove("is-submitting-immediate");
    });
}

async function submitAsyncPageForm(form, formData, messages) {
    const method = String(form.getAttribute("method") || "GET").toUpperCase();
    const action = form.getAttribute("action") || window.location.href;

    if (method === "GET") {
        const requestUrl = new URL(action, window.location.href);
        const params = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            params.append(key, value);
        }
        requestUrl.search = params.toString();
        await navigateToAppUrl(requestUrl.toString());
        return;
    }

    showLoadingOverlay(messages);

    const response = await fetch(action, {
        method,
        body: formData,
        credentials: "same-origin",
        headers: {
            "X-App-Fragment": "1",
            "X-Requested-With": "XMLHttpRequest",
        },
    });

    if (!response.ok) {
        throw new Error("Request failed");
    }

    const payload = await readFragmentPayload(response, normalizeAppUrl(response.url || action));
    const targetUrl = normalizeAppUrl(response.url || action);

    appShellState.cache.set(getCacheKey(targetUrl), {
        cachedAt: Date.now(),
        payload,
    });

    applyPayloadToPage(payload, {
        url: targetUrl,
        historyMode: "push",
    });
}

function initAsyncPageForms() {
    const forms = document.querySelectorAll("form[data-async-page='true']");
    if (!forms.length) {
        return;
    }

    forms.forEach((form) => {
        if (form.dataset.asyncBound === "true") {
            return;
        }

        form.dataset.asyncBound = "true";
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (form.classList.contains("is-pending")) {
                return;
            }

            if (typeof form.reportValidity === "function" && !form.reportValidity()) {
                return;
            }

            const method = String(form.getAttribute("method") || "GET").toUpperCase();
            const formData = new FormData(form);
            const messages = parseLoadingMessages(form.dataset.loadingMessages);

            setFormPending(form, true);
            submitAsyncPageForm(form, formData, messages)
                .catch(() => {
                    const action = form.getAttribute("action") || window.location.href;
                    if (method === "GET") {
                        const fallbackUrl = new URL(action, window.location.href);
                        fallbackUrl.search = new URLSearchParams(formData).toString();
                        window.location.assign(fallbackUrl.toString());
                        return;
                    }

                    HTMLFormElement.prototype.submit.call(form);
                })
                .finally(() => {
                    setFormPending(form, false);
                });
        });
    });
}

function initAutoSubmitControls() {
    const forms = document.querySelectorAll("form[data-auto-submit-controls='true']");
    if (!forms.length) {
        return;
    }

    forms.forEach((form) => {
        if (form.dataset.autoSubmitBound === "true") {
            return;
        }

        form.dataset.autoSubmitBound = "true";
        const controls = form.querySelectorAll("select, input[type='checkbox'], input[type='radio']");
        controls.forEach((control) => {
            control.addEventListener("change", () => {
                if (form.classList.contains("is-pending")) {
                    return;
                }
                if (typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                    return;
                }
                HTMLFormElement.prototype.submit.call(form);
            });
        });
    });
}

function initFeedbackAssistant() {
    const openChatButtons = document.querySelectorAll("[data-feedback-open-chat]");
    if (!openChatButtons.length) {
        return;
    }

    openChatButtons.forEach((openChatButton) => {
        if (openChatButton.dataset.feedbackBound === "true") {
            return;
        }

        openChatButton.dataset.feedbackBound = "true";
        openChatButton.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            if (typeof window.openChat === "function") {
                window.openChat();
                return;
            }
            showAjaxMessage("Live chat is still loading.", "info");
        });
    });
}

function initResponsiveSearchPlaceholders() {
    const searchInputs = Array.from(document.querySelectorAll("[data-placeholder-full][data-placeholder-compact]"));
    if (!searchInputs.length) {
        return;
    }

    const compactMedia = window.matchMedia("(max-width: 640px)");

    function updatePlaceholders() {
        const useCompact = compactMedia.matches;
        searchInputs.forEach((input) => {
            const nextPlaceholder = useCompact ? input.dataset.placeholderCompact : input.dataset.placeholderFull;
            if (!nextPlaceholder) {
                return;
            }

            input.placeholder = nextPlaceholder;
            input.setAttribute("aria-label", nextPlaceholder);
            input.setAttribute("title", input.dataset.placeholderFull || nextPlaceholder);
        });
    }

    updatePlaceholders();
    if (typeof compactMedia.addEventListener === "function") {
        compactMedia.addEventListener("change", updatePlaceholders);
    } else if (typeof compactMedia.addListener === "function") {
        compactMedia.addListener(updatePlaceholders);
    }

    window.addEventListener("resize", updatePlaceholders);
}

function initPasswordToggles() {
    const buttons = document.querySelectorAll("[data-password-toggle-button]");
    if (!buttons.length) {
        return;
    }

    buttons.forEach((button) => {
        const inputId = button.getAttribute("data-password-toggle-button");
        const target = inputId ? document.getElementById(inputId) : null;
        if (!target) {
            return;
        }

        const openIcon = button.querySelector("[data-eye-open]");
        const closedIcon = button.querySelector("[data-eye-closed]");

        button.addEventListener("click", () => {
            const shouldShow = target.type === "password";
            target.type = shouldShow ? "text" : "password";
            button.setAttribute("aria-pressed", shouldShow ? "true" : "false");
            button.setAttribute("aria-label", shouldShow ? "Hide password" : "Show password");
            if (openIcon) {
                openIcon.style.display = shouldShow ? "none" : "inline-flex";
            }
            if (closedIcon) {
                closedIcon.style.display = shouldShow ? "inline-flex" : "none";
            }
        });
    });
}

function initAjaxDifficultForms() {
    const difficultForms = document.querySelectorAll("[data-ajax-difficult-form]");
    if (!difficultForms.length) {
        return;
    }

    difficultForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const submitButton = form.querySelector("button[type='submit']");
            if (submitButton) {
                submitButton.disabled = true;
            }

            try {
                const payload = await postJson(form.action, new FormData(form));
                const card = form.closest("[data-user-word-card]");

                if (form.dataset.removeCard === "true" && card && payload.is_difficult === false) {
                    card.remove();
                    const remainingCards = document.querySelectorAll("[data-user-word-card]");
                    if (!remainingCards.length) {
                        const wordList = document.querySelector(".word-list");
                        if (wordList) {
                            wordList.outerHTML = '<p class="empty-state">No difficult words right now. You are caught up.</p>';
                        }
                    }
                }

                showAjaxMessage(payload.message || "Updated successfully.", payload.is_difficult ? "success" : "info");
            } catch (error) {
                showAjaxMessage("Could not update this word right now.", "error");
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                }
            }
        });
    });
}

function initVocabularyInputs() {
    const message = "Please enter a word or short phrase for vocabulary learning.";
    const maxWords = 5;
    const maxLength = 60;
    const pattern = /^[A-Za-z]+(?:[A-Za-z\s'-]*[A-Za-z]+)?$/;
    const inputs = document.querySelectorAll("input[name='q'], input[name='custom_prompt']");

    if (!inputs.length) {
        return;
    }

    function validateInput(input) {
        const value = String(input.value || "").trim().replace(/\s+/g, " ");
        let nextMessage = "";

        if (!value) {
            input.setCustomValidity("");
            return;
        }

        if (value.length > maxLength || value.split(/\s+/).filter(Boolean).length > maxWords || !pattern.test(value)) {
            nextMessage = message;
        }

        input.setCustomValidity(nextMessage);
    }

    inputs.forEach((input) => {
        if (input.dataset.vocabValidationBound === "true") {
            return;
        }

        input.dataset.vocabValidationBound = "true";
        input.setAttribute("maxlength", String(maxLength));
        input.addEventListener("input", () => validateInput(input));
        input.addEventListener("blur", () => validateInput(input));
    });
}

function initSearchSuggestions() {
    const suggestionButtons = document.querySelectorAll("[data-search-suggestion]");
    if (!suggestionButtons.length) {
        return;
    }

    const searchForm = document.querySelector(".search-page-form");
    const searchInput = searchForm?.querySelector("input[name='q']");
    if (!searchForm || !searchInput) {
        return;
    }

    suggestionButtons.forEach((button) => {
        if (button.dataset.searchSuggestionBound === "true") {
            return;
        }

        button.dataset.searchSuggestionBound = "true";
        button.addEventListener("click", () => {
            const suggestion = String(button.dataset.searchSuggestion || "").trim();
            if (!suggestion) {
                return;
            }

            searchInput.value = suggestion;
            searchInput.dispatchEvent(new Event("input", { bubbles: true }));
            if (typeof searchForm.requestSubmit === "function") {
                searchForm.requestSubmit();
                return;
            }
            HTMLFormElement.prototype.submit.call(searchForm);
        });
    });
}

function initNavMenu() {
    const navMenus = document.querySelectorAll("[data-nav-menu]");
    if (!navMenus.length) {
        return;
    }

    function closeMenu(navMenu) {
        const trigger = navMenu.querySelector(".nav-menu-trigger");
        const panel = navMenu.querySelector(".nav-menu-panel");
        navMenu.classList.remove("is-open");
        if (trigger) {
            trigger.setAttribute("aria-expanded", "false");
        }
        if (panel) {
            panel.setAttribute("aria-hidden", "true");
        }
    }

    function closeAllMenus() {
        navMenus.forEach((menu) => closeMenu(menu));
    }

    navMenus.forEach((navMenu) => {
        if (navMenu.dataset.navMenuBound === "true") {
            return;
        }

        navMenu.dataset.navMenuBound = "true";
        const trigger = navMenu.querySelector(".nav-menu-trigger");
        const panel = navMenu.querySelector(".nav-menu-panel");
        if (!trigger) {
            return;
        }

        function openMenu() {
            closeAllMenus();
            navMenu.classList.add("is-open");
            trigger.setAttribute("aria-expanded", "true");
            if (panel) {
                panel.setAttribute("aria-hidden", "false");
            }
        }

        trigger.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            if (navMenu.classList.contains("is-open")) {
                closeMenu(navMenu);
            } else {
                openMenu();
            }
        });

        if (panel) {
            panel.addEventListener("click", (event) => {
                const navLink = event.target.closest("a");
                if (navLink) {
                    closeMenu(navMenu);
                }
            });
        }
    });

    if (!window.__navMenuGlobalBound) {
        window.__navMenuGlobalBound = true;

        document.addEventListener("click", (event) => {
            const clickedInsideAnyMenu = event.target.closest("[data-nav-menu]");
            if (!clickedInsideAnyMenu) {
                closeAllMenus();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                const openMenu = document.querySelector("[data-nav-menu].is-open");
                closeAllMenus();
                const trigger = openMenu?.querySelector(".nav-menu-trigger");
                if (trigger) {
                    trigger.focus();
                }
            }
        });
    }
}

function initFlashcards() {
    const flashcardApp = document.querySelector("#flashcard-app");
    if (!flashcardApp) {
        if (window.__flashcardKeyboardHandler) {
            document.removeEventListener("keydown", window.__flashcardKeyboardHandler);
            window.__flashcardKeyboardHandler = null;
        }
        return;
    }

    if (flashcardApp.dataset.flashcardBound === "true") {
        return;
    }
    flashcardApp.dataset.flashcardBound = "true";

    const flashcardMode = flashcardApp.dataset.mode || "study";
    const cards = JSON.parse(flashcardApp.dataset.cards || "[]");
    const originalCards = cards.map((card) => ({ ...card }));
    const countEl = document.querySelector("#flashcard-count");
    const wordEl = document.querySelector("#flashcard-word");
    const partOfSpeechEl = document.querySelector("#flashcard-part-of-speech");
    const partOfSpeechBackEl = document.querySelector("#flashcard-part-of-speech-back");
    const flipCardEl = document.querySelector("#flashcard-flip");
    const meaningEl = document.querySelector("#flashcard-meaning");
    const banglaMeaningEl = document.querySelector("#flashcard-bangla-meaning");
    const phoneticEl = document.querySelector("#flashcard-phonetic");
    const frontPhoneticEl = document.querySelector("#flashcard-front-phonetic");
    const wordBackEl = document.querySelector("#flashcard-word-back");
    const synonymEl = document.querySelector("#flashcard-synonym");
    const antonymEl = document.querySelector("#flashcard-antonym");
    const antonymCardEl = document.querySelector("#flashcard-antonym-card");
    const sentenceEl = document.querySelector("#flashcard-sentence");
    const statusEl = document.querySelector("#flashcard-status");
    const markLearnedBtn = document.querySelector("#mark-learned-btn");
    const markDifficultBtn = document.querySelector("#mark-difficult-btn");
    const alreadyKnownBtn = document.querySelector("#already-known-btn");
    const restartBtn = document.querySelector("#flashcard-restart-btn");
    const speakBtn = document.querySelector("#flashcard-speak-btn");

    let currentIndex = 0;
    let touchStartX = 0;
    let touchStartY = 0;
    let touchMoved = false;
    let lastTouchInteractionAt = 0;
    let queuedStatusMessage = "";
    const swipeThreshold = 50;
    const touchClickGuardMs = 600;
    const desktopFlashcardMedia = window.matchMedia("(min-width: 768px) and (hover: hover) and (pointer: fine)");
    let flashcardPressReleaseTimer = null;
    
    // Stable counters for tracking session progress easily
    let initialTotalCards = parseInt(flashcardApp.dataset.totalCount || cards.length, 10);
    let numCompletedThisSession = 0;
    const progressEl = document.querySelector("#flashcard-progress");
    const hiddenValuePatterns = [
        "a curated vocabulary item",
        "a simple meaning for",
        "definition is being prepared",
        "definition pending review",
        "no bangla translation",
        "no example",
        "no synonym",
        "no antonym",
        "not added yet",
        "n/a"
    ];
    
    const storageKey = `vflash.ai_last_card_id_${flashcardMode}`;
    const savedCardId = localStorage.getItem(storageKey);
    if (savedCardId && cards.length > 0) {
        const foundIndex = cards.findIndex(c => c.id == parseInt(savedCardId, 10));
        if (foundIndex !== -1) {
            currentIndex = foundIndex;
        }
    }

    function setButtonsDisabled(disabled) {
        if (markLearnedBtn) {
            markLearnedBtn.disabled = disabled;
        }
        if (markDifficultBtn) {
            markDifficultBtn.disabled = disabled;
        }
        if (alreadyKnownBtn) {
            alreadyKnownBtn.disabled = disabled;
        }
        flipCardEl.setAttribute("aria-disabled", String(disabled));
    }

    function updateDifficultButton(card) {
        if (!markDifficultBtn) {
            return;
        }
        
        const textSpan = markDifficultBtn.querySelector(".font-label") || markDifficultBtn;
        const iconSpan = markDifficultBtn.querySelector(".material-symbols-outlined");

        if (!card) {
            textSpan.textContent = "Difficult";
            if (iconSpan) iconSpan.textContent = "error";
            markDifficultBtn.classList.remove("is-active");
            return;
        }

        textSpan.textContent = card.is_difficult ? "Saved" : "Difficult";
        if (iconSpan) iconSpan.textContent = card.is_difficult ? "error" : "error"; 
        // Can keep icon as error or change to something else if desired.
        markDifficultBtn.classList.toggle("is-active", card.is_difficult);
    }

    function hasActiveCard() {
        return cards.length && currentIndex < cards.length;
    }

    function cleanDisplayValue(value) {
        const cleaned = String(value || "").trim();
        const lower = cleaned.toLowerCase();
        if (!cleaned || hiddenValuePatterns.some((pattern) => lower.includes(pattern))) {
            return "";
        }
        return cleaned;
    }

    function setField(fieldName, element, value) {
        const cleaned = cleanDisplayValue(value);
        if (element) {
            element.textContent = cleaned;
        }
        const wrapper = document.querySelector(`[data-flashcard-field="${fieldName}"]`);
        if (wrapper) {
            wrapper.hidden = !cleaned;
        }
    }

    function isDesktopFlashcardInteraction() {
        return desktopFlashcardMedia.matches;
    }

    function syncFlashcardInteractionMode() {
        if (!flipCardEl) {
            return;
        }
        flipCardEl.classList.toggle("is-desktop-clickable", isDesktopFlashcardInteraction());
        if (!isDesktopFlashcardInteraction()) {
            flipCardEl.classList.remove("is-pressing");
        }
    }

    function setFlashcardPressState(isPressing) {
        if (!flipCardEl || !isDesktopFlashcardInteraction()) {
            return;
        }
        flipCardEl.classList.toggle("is-pressing", isPressing);
    }

    function releaseFlashcardPressState() {
        if (flashcardPressReleaseTimer) {
            window.clearTimeout(flashcardPressReleaseTimer);
        }
        flashcardPressReleaseTimer = window.setTimeout(() => {
            setFlashcardPressState(false);
        }, 120);
    }

    function handleDesktopFlashcardClick(event) {
        if (!flipCardEl) {
            return;
        }

        const bounds = flipCardEl.getBoundingClientRect();
        if (!bounds.width) {
            flipCard();
            return;
        }

        const relativeX = event.clientX - bounds.left;
        const clickRatio = relativeX / bounds.width;

        if (clickRatio <= 0.3) {
            showPreviousCard();
            return;
        }

        if (clickRatio >= 0.7) {
            showNextCard();
            return;
        }

        flipCard();
    }

    function flipCard() {
        if (!hasActiveCard() || !flipCardEl) {
            return;
        }
        flipCardEl.classList.toggle("is-flipped");
    }

    function speakCurrentCard() {
        const card = cards[currentIndex];
        if (!card || !("speechSynthesis" in window)) {
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(card.word);
        utterance.lang = "en-US";
        utterance.rate = 0.86;
        window.speechSynthesis.speak(utterance);
    }

    function showNextCard() {
        if (!hasActiveCard()) {
            renderCard();
            return;
        }
        if (currentIndex < cards.length - 1) {
            currentIndex += 1;
        }
        renderCard();
    }

    function showPreviousCard() {
        if (!hasActiveCard()) {
            renderCard();
            return;
        }
        if (currentIndex > 0) {
            currentIndex -= 1;
        }
        renderCard();
    }

    async function completeCurrentCard() {
        const card = cards[currentIndex];
        if (!card || !markLearnedBtn) {
            return;
        }

        try {
            markLearnedBtn.disabled = true;
            const actionPath = flashcardMode === "review" ? `/review/complete/${card.id}` : `/flashcards/learn/${card.id}`;
            const payload = await postJson(actionPath);
            queuedStatusMessage = payload.message || (flashcardMode === "review" ? "Marked as reviewed." : "Marked as learned.");
            cards.splice(currentIndex, 1);
            numCompletedThisSession += 1;
            if (currentIndex >= cards.length && currentIndex > 0) {
                currentIndex -= 1;
            }
            renderCard();
        } catch (error) {
            statusEl.textContent = "Could not update this word right now.";
            showAjaxMessage("Could not update this word right now.", "error");
            markLearnedBtn.disabled = false;
        }
    }

    async function toggleCurrentCardDifficult() {
        const card = cards[currentIndex];
        if (!card || !markDifficultBtn) {
            return;
        }

        try {
            markDifficultBtn.disabled = true;
            const payload = await postJson(`/words/difficult/${card.id}`);
            card.is_difficult = Boolean(payload.is_difficult);
            updateDifficultButton(card);
            
            statusEl.textContent = payload.message || (payload.is_difficult ? "Marked as difficult." : "Removed from difficult list.");
            statusEl.style.opacity = 0;
            requestAnimationFrame(() => {
                statusEl.style.transition = 'opacity 0.2s';
                statusEl.style.opacity = 1;
                setTimeout(() => statusEl.style.opacity = 0, 1500);
            });
        } catch (error) {
            statusEl.textContent = "Could not update difficult words right now.";
            showAjaxMessage("Could not update difficult words right now.", "error");
        } finally {
            markDifficultBtn.disabled = false;
        }
    }

    async function markCurrentCardAlreadyKnown() {
        const card = cards[currentIndex];
        if (!card || !alreadyKnownBtn) {
            return;
        }

        try {
            alreadyKnownBtn.disabled = true;
            const payload = await postJson(`/flashcards/already-known/${card.id}`);
            queuedStatusMessage = payload.message || "Marked as already known.";
            cards.splice(currentIndex, 1);
            numCompletedThisSession += 1;
            if (currentIndex >= cards.length && currentIndex > 0) {
                currentIndex -= 1;
            }
            renderCard();
        } catch (error) {
            statusEl.textContent = "Could not update this word right now.";
            showAjaxMessage("Could not update this word right now.", "error");
            alreadyKnownBtn.disabled = false;
        }
    }

    function renderCard() {
        if (!hasActiveCard()) {
            if (countEl) countEl.textContent = `0 / ${initialTotalCards} Cards`;
            if (wordEl) wordEl.textContent = "No more words to study";
            if (wordBackEl) wordBackEl.textContent = "Complete";
            if (partOfSpeechEl) {
                partOfSpeechEl.textContent = "";
                partOfSpeechEl.classList.add("is-hidden");
            }
            if (partOfSpeechBackEl) {
                partOfSpeechBackEl.textContent = "";
                partOfSpeechBackEl.hidden = true;
            }
            if (meaningEl) meaningEl.textContent = "";
            if (banglaMeaningEl) banglaMeaningEl.textContent = "";
            if (phoneticEl) phoneticEl.textContent = "";
            if (frontPhoneticEl) frontPhoneticEl.textContent = "";
            if (synonymEl) synonymEl.textContent = "";
            if (antonymEl) antonymEl.textContent = "";
            if (antonymCardEl) antonymCardEl.style.display = "";
            if (sentenceEl) sentenceEl.textContent = "";
            document.querySelectorAll("[data-flashcard-field]").forEach((field) => {
                field.hidden = true;
            });
            flipCardEl.classList.remove("is-flipped");
            if (statusEl) statusEl.textContent = queuedStatusMessage;
            setButtonsDisabled(true);
            updateDifficultButton(null);
            localStorage.removeItem(storageKey);
            if (progressEl) progressEl.style.width = '100%';
            return;
        }

        const card = cards[currentIndex];
        localStorage.setItem(storageKey, card.id);
        
        if (countEl) countEl.textContent = `${currentIndex + 1} / ${initialTotalCards} Cards`;
        
        // Update Progress Bar based on completed vs initial
        if (progressEl && initialTotalCards > 0) {
            const pct = Math.round((numCompletedThisSession / initialTotalCards) * 100);
            progressEl.style.width = `${pct}%`;
        }

        if (wordEl) wordEl.textContent = card.word;
        if (wordBackEl) wordBackEl.textContent = card.word;
        if (partOfSpeechEl) {
            const partOfSpeech = cleanDisplayValue(card.part_of_speech);
            partOfSpeechEl.textContent = partOfSpeech;
            partOfSpeechEl.classList.toggle("is-hidden", !partOfSpeech);
        }
        if (partOfSpeechBackEl) {
            const partOfSpeech = cleanDisplayValue(card.part_of_speech);
            partOfSpeechBackEl.textContent = partOfSpeech;
            partOfSpeechBackEl.hidden = !partOfSpeech;
        }
        if (meaningEl) meaningEl.textContent = cleanDisplayValue(card.meaning);
        setField("bangla", banglaMeaningEl, card.bangla_meaning);
        setField("phonetic", phoneticEl, card.phonetic);
        if (frontPhoneticEl) frontPhoneticEl.textContent = cleanDisplayValue(card.phonetic);
        setField("synonym", synonymEl, card.synonym);
        setField("antonym", antonymEl, card.antonym);
        setField("sentence", sentenceEl, card.sentence);
        
        flipCardEl.style.opacity = 0;
        requestAnimationFrame(() => {
            flipCardEl.classList.remove("is-flipped");
            flipCardEl.style.transition = 'opacity 0.2s';
            flipCardEl.style.opacity = 1;
        });

        setButtonsDisabled(false);
        updateDifficultButton(card);
        
        if (statusEl && queuedStatusMessage) {
            statusEl.textContent = queuedStatusMessage;
            statusEl.style.opacity = 0;
            requestAnimationFrame(() => {
                statusEl.style.transition = 'opacity 0.2s';
                statusEl.style.opacity = 1;
                setTimeout(() => statusEl.style.opacity = 0, 1500);
            });
            queuedStatusMessage = "";
        }
    }

    flipCardEl.addEventListener("click", (event) => {
        event.preventDefault();
        if (!hasActiveCard()) {
            return;
        }

        if ((Date.now() - lastTouchInteractionAt) <= touchClickGuardMs) {
            return;
        }

        if (isDesktopFlashcardInteraction()) {
            handleDesktopFlashcardClick(event);
            return;
        }

        flipCard();
    });

    flipCardEl.addEventListener("pointerdown", (event) => {
        if (event.pointerType !== "mouse" || !isDesktopFlashcardInteraction()) {
            return;
        }

        if (flashcardPressReleaseTimer) {
            window.clearTimeout(flashcardPressReleaseTimer);
        }
        setFlashcardPressState(true);
    });

    flipCardEl.addEventListener("pointerup", (event) => {
        if (event.pointerType !== "mouse" || !isDesktopFlashcardInteraction()) {
            return;
        }
        releaseFlashcardPressState();
    });

    flipCardEl.addEventListener("pointerleave", () => {
        if (!isDesktopFlashcardInteraction()) {
            return;
        }
        if (flashcardPressReleaseTimer) {
            window.clearTimeout(flashcardPressReleaseTimer);
        }
        setFlashcardPressState(false);
    });

    flipCardEl.addEventListener("pointercancel", () => {
        if (!isDesktopFlashcardInteraction()) {
            return;
        }
        if (flashcardPressReleaseTimer) {
            window.clearTimeout(flashcardPressReleaseTimer);
        }
        setFlashcardPressState(false);
    });

    flipCardEl.addEventListener("touchstart", (event) => {
        const touch = event.changedTouches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
        touchMoved = false;
        lastTouchInteractionAt = Date.now();
    }, { passive: true });

    flipCardEl.addEventListener("touchmove", (event) => {
        const touch = event.changedTouches[0];
        if (!touch) {
            return;
        }

        const deltaX = touch.clientX - touchStartX;
        const deltaY = touch.clientY - touchStartY;
        if (Math.abs(deltaX) > 8 || Math.abs(deltaY) > 8) {
            touchMoved = true;
        }
    }, { passive: true });

    flipCardEl.addEventListener("touchend", (event) => {
        const touch = event.changedTouches[0];
        const deltaX = touch.clientX - touchStartX;
        const deltaY = touch.clientY - touchStartY;
        lastTouchInteractionAt = Date.now();

        if (!touchMoved) {
            flipCard();
            return;
        }

        if (Math.abs(deltaY) > Math.abs(deltaX)) {
            return;
        }

        if (Math.abs(deltaX) < swipeThreshold) {
            flipCard();
            return;
        }

        if (deltaX > 0) {
            showPreviousCard();
        } else {
            showNextCard();
        }
    });

    if (window.__flashcardKeyboardHandler) {
        document.removeEventListener("keydown", window.__flashcardKeyboardHandler);
    }

    window.__flashcardKeyboardHandler = (event) => {
        const tagName = document.activeElement?.tagName;
        if (["INPUT", "TEXTAREA", "SELECT"].includes(tagName)) {
            return;
        }

        if (!hasActiveCard()) {
            return;
        }

        if (event.code === "ArrowRight") {
            event.preventDefault();
            showNextCard();
        } else if (event.code === "ArrowLeft") {
            event.preventDefault();
            showPreviousCard();
        } else if (event.code === "Space") {
            event.preventDefault();
            flipCard();
        } else if (event.code === "KeyL") {
            event.preventDefault();
            completeCurrentCard();
        } else if (event.code === "KeyD") {
            event.preventDefault();
            toggleCurrentCardDifficult();
        } else if (event.code === "KeyK") {
            event.preventDefault();
            markCurrentCardAlreadyKnown();
        }
    };

    document.addEventListener("keydown", window.__flashcardKeyboardHandler);

    if (markDifficultBtn) {
        markDifficultBtn.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            toggleCurrentCardDifficult();
        });
    }

    if (alreadyKnownBtn) {
        alreadyKnownBtn.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            markCurrentCardAlreadyKnown();
        });
    }

    if (markLearnedBtn) {
        markLearnedBtn.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            completeCurrentCard();
        });
    }

    if (restartBtn) {
        restartBtn.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            currentIndex = 0;
            numCompletedThisSession = 0;
            cards.splice(0, cards.length, ...originalCards.map((card) => ({ ...card })));
            localStorage.removeItem(storageKey);
            queuedStatusMessage = "Session restarted.";
            renderCard();
        });
    }
    if (speakBtn) {
        speakBtn.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            speakCurrentCard();
        });
    }

    syncFlashcardInteractionMode();
    if (typeof desktopFlashcardMedia.addEventListener === "function") {
        desktopFlashcardMedia.addEventListener("change", syncFlashcardInteractionMode);
    } else if (typeof desktopFlashcardMedia.addListener === "function") {
        desktopFlashcardMedia.addListener(syncFlashcardInteractionMode);
    }
    window.addEventListener("resize", syncFlashcardInteractionMode);

    renderCard();

    const sessionId = flashcardApp.dataset.sessionId;
    if (sessionId) {
        // Build a fast lookup set so duplicate detection is O(1)
        const seenCardIds = new Set(originalCards.map((c) => c.id));

        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/flashcards/session/${sessionId}/poll`);
                if (!response.ok) return;
                const data = await response.json();

                let newCardsAdded = false;
                if (data.cards && data.cards.length > 0) {
                    data.cards.forEach((newCard) => {
                        if (!seenCardIds.has(newCard.id)) {
                            seenCardIds.add(newCard.id);
                            originalCards.push({ ...newCard });
                            cards.push({ ...newCard });
                            newCardsAdded = true;
                        }
                    });
                }

                if (newCardsAdded) {
                    initialTotalCards = Math.max(initialTotalCards, originalCards.length);
                    const hadNoActiveCard = !hasActiveCard();
                    if (hadNoActiveCard && cards.length > 0) {
                        currentIndex = 0;
                        setButtonsDisabled(false);
                    }
                    renderCard();
                }

                if (data.completed) {
                    // Some words may have permanently failed enrichment (flagged for
                    // admin review). If we received fewer cards than the original
                    // target, reconcile initialTotalCards so the progress counter
                    // shows the correct total instead of being stuck at e.g. "1/10".
                    if (originalCards.length > 0 && originalCards.length < initialTotalCards) {
                        initialTotalCards = originalCards.length;
                        if (!newCardsAdded) {
                            // Re-render so the count label updates immediately
                            renderCard();
                        }
                    }
                    clearInterval(pollInterval);
                }
            } catch (err) {
                console.error("Error polling session status:", err);
            }
        }, 2500);
    }
}

function initUsageTracking() {
    if (window.__usageTrackingInitialized) {
        return;
    }

    const usageEndpoint = document.body.dataset.usageEndpoint;
    if (!usageEndpoint) {
        return;
    }

    window.__usageTrackingInitialized = true;

    const sessionStorageKey = "vflash.ai_usage_session";
    const sessionTimeoutMs = 30 * 60 * 1000;
    const activeWindowMs = 60 * 1000;
    const tickMs = 15000;

    const now = Date.now();
    let interactionCount = 0;
    let lastInteractionAt = now;
    let pendingActiveSeconds = 0;
    let lastTickAt = now;
    let isPageVisible = document.visibilityState === "visible";
    let hasFocus = document.hasFocus();

    function generateSessionKey() {
        return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    }

    function loadSessionState() {
        try {
            return JSON.parse(localStorage.getItem(sessionStorageKey) || "{}");
        } catch (error) {
            return {};
        }
    }

    function saveSessionState(state) {
        localStorage.setItem(sessionStorageKey, JSON.stringify(state));
    }

    function resolveSessionKey() {
        const saved = loadSessionState();
        if (!saved.sessionKey || !saved.lastSeenAt || (now - saved.lastSeenAt) > sessionTimeoutMs) {
            const nextState = { sessionKey: generateSessionKey(), lastSeenAt: now };
            saveSessionState(nextState);
            return nextState.sessionKey;
        }

        saved.lastSeenAt = now;
        saveSessionState(saved);
        return saved.sessionKey;
    }

    const sessionKey = resolveSessionKey();

    function updateSessionSeen() {
        const saved = loadSessionState();
        saved.sessionKey = sessionKey;
        saved.lastSeenAt = Date.now();
        saveSessionState(saved);
    }

    function isActivelyUsingApp() {
        return isPageVisible && hasFocus && (Date.now() - lastInteractionAt) <= activeWindowMs;
    }

    function registerInteraction() {
        interactionCount += 1;
        lastInteractionAt = Date.now();
        updateSessionSeen();
    }

    async function sendUsage(payload, useBeacon = false) {
        updateSessionSeen();
        const body = JSON.stringify({
            session_key: sessionKey,
            page_path: `${window.location.pathname}${window.location.search || ""}`,
            ...payload,
        });

        if (useBeacon && navigator.sendBeacon) {
            const blob = new Blob([body], { type: "application/json" });
            navigator.sendBeacon(usageEndpoint, blob);
            return;
        }

        try {
            await fetch(usageEndpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body,
                keepalive: true,
            });
        } catch (error) {
            // Swallow analytics errors so they never affect the product flow.
        }
    }

    function flushUsage(useBeacon = false) {
        const payload = {
            active_seconds: pendingActiveSeconds,
            interaction_count: interactionCount,
            page_load: false,
        };
        pendingActiveSeconds = 0;
        interactionCount = 0;
        return sendUsage(payload, useBeacon);
    }

    sendUsage({ active_seconds: 0, interaction_count: 0, page_load: true });

    ["pointerdown", "keydown", "scroll", "touchstart", "mousemove"].forEach((eventName) => {
        window.addEventListener(eventName, registerInteraction, { passive: true });
    });

    window.addEventListener("focus", () => {
        hasFocus = true;
        registerInteraction();
    });

    window.addEventListener("blur", () => {
        hasFocus = false;
    });

    document.addEventListener("visibilitychange", () => {
        isPageVisible = document.visibilityState === "visible";
        if (!isPageVisible && (pendingActiveSeconds > 0 || interactionCount > 0)) {
            flushUsage(true);
        }
    });

    window.setInterval(() => {
        const currentTime = Date.now();
        const elapsedSeconds = Math.max(0, Math.floor((currentTime - lastTickAt) / 1000));
        lastTickAt = currentTime;

        if (isActivelyUsingApp()) {
            pendingActiveSeconds += elapsedSeconds;
        }

        if (pendingActiveSeconds > 0 || interactionCount > 0) {
            flushUsage();
        }
    }, tickMs);

    window.addEventListener("pagehide", () => {
        if (pendingActiveSeconds > 0 || interactionCount > 0) {
            flushUsage(true);
        }
    });
}

function initDashboardWarmups() {
    const warmupUrl = document.body.dataset.quizWarmupEndpoint;
    if (!warmupUrl || !document.body.classList.contains("dashboard-page")) {
        return;
    }

    const warmupKey = `${window.location.pathname}${window.location.search}`;
    if (window.__lastDashboardWarmupKey === warmupKey) {
        return;
    }
    window.__lastDashboardWarmupKey = warmupKey;

    const triggerWarmup = async () => {
        try {
            await fetch(warmupUrl, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                credentials: "same-origin",
            });
        } catch (error) {
            // Keep warmup silent so it never interrupts the dashboard.
        }
    };

    if ("requestIdleCallback" in window) {
        window.requestIdleCallback(() => {
            window.setTimeout(triggerWarmup, 400);
        }, { timeout: 2200 });
        return;
    }

    window.setTimeout(triggerWarmup, 1200);
}

function initQuizUX() {
    const quizForm = document.querySelector("[data-quiz-form]");
    // Define global modal helpers on window to prevent ReferenceErrors from inline onclick handlers
    window.showQuitModal = function() {
        const modal = document.getElementById("quit-modal") || document.querySelector("#quit-quiz-modal");
        if (modal) {
            modal.style.display = "flex";
            modal.setAttribute("aria-hidden", "false");
        }
    };
    window.hideQuitModal = function() {
        const modal = document.getElementById("quit-modal") || document.querySelector("#quit-quiz-modal");
        if (modal) {
            modal.style.display = "none";
            modal.setAttribute("aria-hidden", "true");
        }
    };

    // Use stable document-level event delegation to ensure listeners survive any dynamic DOM updates or rerenders
    if (!window.__quizQuitHandlersBound) {
        window.__quizQuitHandlersBound = true;
        document.addEventListener("click", (event) => {
            const quitBtn = event.target.closest("[data-quiz-quit]") || event.target.closest("#quit-quiz-btn") || event.target.closest("button[onclick='showQuitModal()']");
            const resumeBtn = event.target.closest("[data-quiz-resume]") || event.target.closest("#continue-quiz-btn") || event.target.closest("button[onclick='hideQuitModal()']");

            if (quitBtn) {
                event.preventDefault();
                window.showQuitModal();
            }

            if (resumeBtn) {
                event.preventDefault();
                window.hideQuitModal();
            }
        });
    }

    if (!quizForm) {
        return;
    }

    let isSubmitting = false;
    let prefetchStarted = false;
    const correctAnswer = (quizForm.dataset.correctAnswer || "").trim().toLowerCase();
    const prefetchUrl = quizForm.dataset.quizPrefetchUrl || "";
    const prefetchStatusEl = document.querySelector("#quiz-prefetch-status");
    const optionEls = Array.from(document.querySelectorAll("[data-quiz-option]"));
    const answerInput = quizForm.querySelector("#answer");

    async function prefetchQuestions() {
        if (!prefetchUrl || prefetchStarted) {
            return;
        }

        prefetchStarted = true;
        if (prefetchStatusEl) {
            prefetchStatusEl.textContent = "Preparing the next questions...";
        }

        try {
            const payload = await postJson(prefetchUrl);
            if (prefetchStatusEl) {
                prefetchStatusEl.textContent = payload.generated > 0 ? "More questions are ready." : "";
            }
        } catch (error) {
            if (prefetchStatusEl) {
                prefetchStatusEl.textContent = "";
            }
        }
    }

    window.setTimeout(() => {
        prefetchQuestions();
    }, 120);

    quizForm.addEventListener("submit", (event) => {
        if (isSubmitting) {
            return;
        }

        event.preventDefault();
        const formData = new FormData(quizForm);
        const submittedAnswer = String(formData.get("answer") || "").trim().toLowerCase();
        if (!submittedAnswer) {
            return;
        }

        isSubmitting = true;
        const isCorrect = submittedAnswer === correctAnswer;

        if (optionEls.length) {
            optionEls.forEach((optionEl) => {
                const optionValue = (optionEl.dataset.optionValue || "").trim().toLowerCase();
                if (isCorrect) {
                    if (optionValue === correctAnswer) {
                        optionEl.classList.add("quiz-option-correct");
                    }
                } else {
                    if (optionValue === correctAnswer) {
                        optionEl.classList.add("quiz-option-correct");
                    } else if (optionValue === submittedAnswer) {
                        optionEl.classList.add("quiz-option-wrong");
                    }
                }
                optionEl.classList.add("is-locked");
            });
        }

        if (answerInput) {
            answerInput.classList.toggle("input-correct", isCorrect);
            answerInput.classList.toggle("input-wrong", !isCorrect);
        }

        window.setTimeout(() => {
            if (prefetchStatusEl) {
                prefetchStatusEl.textContent = "Loading the next question...";
            }
            quizForm.submit();
        }, 900);
    });
}
