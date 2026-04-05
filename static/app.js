document.addEventListener("DOMContentLoaded", () => {
    const firstInput = document.querySelector("input, textarea, select");
    if (firstInput) {
        firstInput.focus();
    }

    initNavMenu();
    initAjaxDifficultForms();
    initFlashcards();
    initQuizUX();
});

function ensureFlashStack() {
    let flashStack = document.querySelector(".flash-stack");
    if (flashStack) {
        return flashStack;
    }

    const pageShell = document.querySelector(".page-shell");
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

function initNavMenu() {
    const navMenu = document.querySelector("[data-nav-menu]");
    if (!navMenu) {
        return;
    }

    const trigger = navMenu.querySelector(".nav-menu-trigger");
    const panel = navMenu.querySelector(".nav-menu-panel");
    if (!trigger) {
        return;
    }

    function closeMenu() {
        navMenu.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        if (panel) {
            panel.setAttribute("aria-hidden", "true");
        }
    }

    function openMenu() {
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
            closeMenu();
        } else {
            openMenu();
        }
    });

    document.addEventListener("click", (event) => {
        if (!navMenu.classList.contains("is-open")) {
            return;
        }

        if (!navMenu.contains(event.target)) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && navMenu.classList.contains("is-open")) {
            closeMenu();
            trigger.focus();
        }
    });
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
    const synonymEl = document.querySelector("#flashcard-synonym");
    const sentenceEl = document.querySelector("#flashcard-sentence");
    const memoryTrickEl = document.querySelector("#flashcard-memory-trick");
    const statusEl = document.querySelector("#flashcard-status");
    const markLearnedBtn = document.querySelector("#mark-learned-btn");
    const markDifficultBtn = document.querySelector("#mark-difficult-btn");
    const alreadyKnownBtn = document.querySelector("#already-known-btn");

    let currentIndex = 0;
    let touchStartX = 0;
    let touchStartY = 0;
    let queuedStatusMessage = "";
    const swipeThreshold = 50;
    const leftZoneRatio = 0.26;
    const rightZoneRatio = 0.74;

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

        if (!card) {
            markDifficultBtn.textContent = "Mark as Difficult";
            markDifficultBtn.classList.remove("is-active");
            return;
        }

        markDifficultBtn.textContent = card.is_difficult ? "Difficult Saved" : "Mark Difficult";
        markDifficultBtn.classList.toggle("is-active", card.is_difficult);
    }

    function hasActiveCard() {
        return cards.length && currentIndex < cards.length;
    }

    function flipCard() {
        if (!hasActiveCard()) {
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
            showAjaxMessage(queuedStatusMessage, "success");
            cards.splice(currentIndex, 1);
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
            statusEl.textContent = payload.message || "";
            showAjaxMessage(payload.message || "", payload.is_difficult ? "success" : "info");
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
            showAjaxMessage(queuedStatusMessage, "success");
            cards.splice(currentIndex, 1);
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
            countEl.textContent = "Study complete";
            wordEl.textContent = "No more words to study";
            partOfSpeechEl.textContent = "";
            meaningEl.textContent = "";
            banglaMeaningEl.textContent = "";
            phoneticEl.textContent = "";
            synonymEl.textContent = "";
            sentenceEl.textContent = "";
            memoryTrickEl.textContent = "";
            flipCardEl.classList.remove("is-flipped");
            statusEl.textContent = queuedStatusMessage;
            setButtonsDisabled(true);
            updateDifficultButton(null);
            return;
        }

        const card = cards[currentIndex];
        countEl.textContent = `Card ${currentIndex + 1} of ${cards.length}`;
        wordEl.textContent = card.word;
        partOfSpeechEl.textContent = card.part_of_speech || "";
        partOfSpeechEl.classList.toggle("is-hidden", !card.part_of_speech);
        meaningEl.textContent = card.meaning;
        banglaMeaningEl.textContent = card.bangla_meaning;
        phoneticEl.textContent = card.phonetic;
        synonymEl.textContent = card.synonym;
        sentenceEl.textContent = card.sentence;
        memoryTrickEl.textContent = card.memory_trick;
        flipCardEl.classList.remove("is-flipped");
        setButtonsDisabled(false);
        updateDifficultButton(card);
        statusEl.textContent = queuedStatusMessage;
        queuedStatusMessage = "";
    }

    flipCardEl.addEventListener("click", (event) => {
        event.preventDefault();
        if (!hasActiveCard()) {
            return;
        }

        const rect = flipCardEl.getBoundingClientRect();
        const relativeX = (event.clientX - rect.left) / rect.width;

        if (relativeX <= leftZoneRatio) {
            showPreviousCard();
        } else if (relativeX >= rightZoneRatio) {
            showNextCard();
        } else {
            flipCard();
        }
    });

    flipCardEl.addEventListener("touchstart", (event) => {
        const touch = event.changedTouches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
    }, { passive: true });

    flipCardEl.addEventListener("touchend", (event) => {
        const touch = event.changedTouches[0];
        const deltaX = touch.clientX - touchStartX;
        const deltaY = touch.clientY - touchStartY;

        if (Math.abs(deltaX) < swipeThreshold || Math.abs(deltaX) <= Math.abs(deltaY)) {
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
