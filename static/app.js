document.addEventListener("DOMContentLoaded", () => {
    const shouldAutofocus = document.body.classList.contains("auth-page");
    const firstInput = shouldAutofocus ? document.querySelector("input, textarea, select") : null;
    if (firstInput) {
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
});

window.addEventListener("pageshow", () => {
    hideLoadingOverlay();
});

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
        flash.remove();
    }, 2500);
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
        }, 1400 + (index * 150));
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
    form.querySelectorAll("button[type='submit'], input[type='submit']").forEach((button) => {
        if (pending) {
            button.dataset.wasDisabled = button.disabled ? "true" : "false";
            button.disabled = true;
            return;
        }

        if (button.dataset.wasDisabled !== "true") {
            button.disabled = false;
        }
        delete button.dataset.wasDisabled;
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
            const action = form.getAttribute("action") || window.location.href;
            const formData = new FormData(form);
            const messages = parseLoadingMessages(form.dataset.loadingMessages);

            showLoadingOverlay(messages);
            setFormPending(form, true);

            if (method === "GET") {
                const requestUrl = new URL(action, window.location.href);
                const params = new URLSearchParams();
                for (const [key, value] of formData.entries()) {
                    params.append(key, value);
                }
                requestUrl.search = params.toString();
                window.location.assign(requestUrl.toString());
                return;
            }

            window.setTimeout(() => {
                HTMLFormElement.prototype.submit.call(form);
            }, 10);
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

    function pushFeedbackContextToTawk() {
        if (!window.Tawk_API) {
            return;
        }

        const customAttributes = {
            "feedback-entry": "direct-message",
            "feedback-page-title": document.title.replace(/\s*\|\s*vflash\.ai\s*$/i, "").trim() || "Unknown page",
            "feedback-path": window.location.pathname || "/"
        };

        if (typeof window.Tawk_API.setAttributes === "function") {
            window.Tawk_API.setAttributes(customAttributes, function (error) {
                if (error && window.console && typeof window.console.warn === "function") {
                    window.console.warn("Tawk.to feedback metadata failed.", error);
                }
            });
        }

        if (typeof window.Tawk_API.addTags === "function") {
            const pageTag = (window.location.pathname || "home")
                .replace(/[^a-z0-9]+/gi, "-")
                .replace(/^-+|-+$/g, "")
                .toLowerCase() || "home";

            window.Tawk_API.addTags(["direct-message", `page-${pageTag}`], function (error) {
                if (error && window.console && typeof window.console.warn === "function") {
                    window.console.warn("Tawk.to feedback tags failed.", error);
                }
            });
        }
    }

    function openFeedbackChat() {
        pushFeedbackContextToTawk();

        if (!window.Tawk_API || typeof window.Tawk_API.maximize !== "function") {
            showAjaxMessage("Live chat is still loading.", "info");
            return;
        }

        const isMaximized = typeof window.Tawk_API.isChatMaximized === "function" && window.Tawk_API.isChatMaximized();

        if (isMaximized) {
            window.__tawkOpenedByCustomButton = false;
            if (typeof window.Tawk_API.minimize === "function") {
                window.Tawk_API.minimize();
            }
            if (typeof window.Tawk_API.hideWidget === "function") {
                window.Tawk_API.hideWidget();
            }
            return;
        }

        if (typeof window.Tawk_API.showWidget === "function") {
            window.__tawkOpenedByCustomButton = true;
            window.Tawk_API.showWidget();
        }

        window.Tawk_API.maximize();
    }

    openChatButtons.forEach((openChatButton) => {
        if (openChatButton.dataset.feedbackBound === "true") {
            return;
        }

        openChatButton.dataset.feedbackBound = "true";
        openChatButton.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            openFeedbackChat();
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
        return;
    }

    const flashcardMode = flashcardApp.dataset.mode || "study";
    const cards = JSON.parse(flashcardApp.dataset.cards || "[]");
    const countEl = document.querySelector("#flashcard-count");
    const wordEl = document.querySelector("#flashcard-word");
    const partOfSpeechEl = document.querySelector("#flashcard-part-of-speech");
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
    const memoryTrickEl = document.querySelector("#flashcard-memory-trick");
    const statusEl = document.querySelector("#flashcard-status");
    const markLearnedBtn = document.querySelector("#mark-learned-btn");
    const markDifficultBtn = document.querySelector("#mark-difficult-btn");
    const alreadyKnownBtn = document.querySelector("#already-known-btn");

    let currentIndex = 0;
    let touchStartX = 0;
    let touchStartY = 0;
    let touchMoved = false;
    let lastTouchInteractionAt = 0;
    let queuedStatusMessage = "";
    const swipeThreshold = 50;
    const touchClickGuardMs = 600;
    
    // Stable counters for tracking session progress easily
    const initialTotalCards = cards.length;
    let numCompletedThisSession = 0;
    const progressEl = document.querySelector("#flashcard-progress");
    
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

    function flipCard() {
        if (!hasActiveCard() || !flipCardEl) {
            return;
        }
        flipCardEl.classList.toggle("is-flipped");
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
            if (meaningEl) meaningEl.textContent = "";
            if (banglaMeaningEl) banglaMeaningEl.textContent = "";
            if (phoneticEl) phoneticEl.textContent = "";
            if (frontPhoneticEl) frontPhoneticEl.textContent = "";
            if (synonymEl) synonymEl.textContent = "";
            if (antonymEl) antonymEl.textContent = "";
            if (antonymCardEl) antonymCardEl.style.display = "";
            if (sentenceEl) sentenceEl.textContent = "";
            if (memoryTrickEl) memoryTrickEl.textContent = "";
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
            partOfSpeechEl.textContent = card.part_of_speech || "";
            partOfSpeechEl.classList.toggle("is-hidden", !card.part_of_speech);
        }
        if (meaningEl) meaningEl.textContent = card.meaning;
        if (banglaMeaningEl) banglaMeaningEl.textContent = card.bangla_meaning;
        if (phoneticEl) phoneticEl.textContent = card.phonetic;
        if (frontPhoneticEl) frontPhoneticEl.textContent = card.phonetic;
        if (synonymEl) synonymEl.textContent = card.synonym;
        if (antonymEl) antonymEl.textContent = card.antonym;
        if (antonymCardEl) antonymCardEl.style.display = card.antonym ? "" : "none";
        if (sentenceEl) sentenceEl.textContent = card.sentence;
        if (memoryTrickEl) memoryTrickEl.textContent = card.memory_trick;
        
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

        flipCard();
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

    document.addEventListener("keydown", (event) => {
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
    });

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

    renderCard();
}

function initUsageTracking() {
    const usageEndpoint = document.body.dataset.usageEndpoint;
    if (!usageEndpoint) {
        return;
    }

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
    const quitButton = document.querySelector("#quit-quiz-btn");
    const continueQuizButton = document.querySelector("#continue-quiz-btn");
    const quitModal = document.querySelector("#quit-quiz-modal");

    if (quitButton && quitModal) {
        quitButton.addEventListener("click", () => {
            quitModal.classList.remove("is-hidden");
            quitModal.setAttribute("aria-hidden", "false");
        });
    }

    if (continueQuizButton && quitModal) {
        continueQuizButton.addEventListener("click", () => {
            quitModal.classList.add("is-hidden");
            quitModal.setAttribute("aria-hidden", "true");
        });
    }

    if (!quizForm) {
        return;
    }

    let isSubmitting = false;
    let prefetchStarted = false;
    const correctAnswer = JSON.parse(quizForm.dataset.correctAnswer || '""').toLowerCase();
    const prefetchUrl = quizForm.dataset.quizPrefetchUrl || "";
    const feedbackEl = document.querySelector("#quiz-feedback");
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

        if (feedbackEl) {
            feedbackEl.textContent = isCorrect ? "Correct answer" : `Correct answer: ${correctAnswer}`;
            feedbackEl.classList.toggle("is-correct", isCorrect);
            feedbackEl.classList.toggle("is-wrong", !isCorrect);
        }

        if (optionEls.length) {
            optionEls.forEach((optionEl) => {
                const optionValue = JSON.parse(optionEl.dataset.optionValue || '""').toLowerCase();
                optionEl.classList.toggle("is-correct", optionValue === correctAnswer);
                optionEl.classList.toggle("is-wrong", optionValue === submittedAnswer && optionValue !== correctAnswer);
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
