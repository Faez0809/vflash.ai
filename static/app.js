document.addEventListener("DOMContentLoaded", () => {
    const firstInput = document.querySelector("input, textarea");
    if (firstInput) {
        firstInput.focus();
    }

    const flashcardApp = document.querySelector("#flashcard-app");
    if (!flashcardApp) {
        return;
    }

    const cards = JSON.parse(flashcardApp.dataset.cards || "[]");
    const countEl = document.querySelector("#flashcard-count");
    const wordEl = document.querySelector("#flashcard-word");
    const flipCardEl = document.querySelector("#flashcard-flip");
    const meaningEl = document.querySelector("#flashcard-meaning");
    const banglaMeaningEl = document.querySelector("#flashcard-bangla-meaning");
    const sentenceEl = document.querySelector("#flashcard-sentence");
    const statusEl = document.querySelector("#flashcard-status");
    const markLearnedBtn = document.querySelector("#mark-learned-btn");
    const nextWordBtn = document.querySelector("#next-word-btn");

    let currentIndex = 0;
    let touchStartX = 0;
    let touchStartY = 0;
    const swipeThreshold = 50;
    const edgeZoneRatio = 0.22;

    function setButtonsDisabled(disabled) {
        markLearnedBtn.disabled = disabled;
        nextWordBtn.disabled = disabled;
        flipCardEl.disabled = disabled;
    }

    function hasActiveCard() {
        return cards.length && currentIndex < cards.length;
    }

    function isCoarsePointer() {
        return window.matchMedia("(pointer: coarse)").matches;
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

    async function markCurrentCardLearned() {
        const card = cards[currentIndex];
        if (!card) {
            return;
        }

        try {
            markLearnedBtn.disabled = true;
            const response = await fetch(`/flashcards/learn/${card.id}`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error("Request failed");
            }

            cards.splice(currentIndex, 1);
            if (currentIndex >= cards.length && currentIndex > 0) {
                currentIndex -= 1;
            }
            renderCard();
        } catch (error) {
            statusEl.textContent = "Could not update this word right now.";
            markLearnedBtn.disabled = false;
        }
    }

    function renderCard() {
        if (!hasActiveCard()) {
            countEl.textContent = "Study complete";
            wordEl.textContent = "No more words to study";
            meaningEl.textContent = "";
            banglaMeaningEl.textContent = "";
            sentenceEl.textContent = "";
            flipCardEl.classList.remove("is-flipped");
            statusEl.textContent = "";
            setButtonsDisabled(true);
            return;
        }

        const card = cards[currentIndex];
        countEl.textContent = `Word ${currentIndex + 1} of ${cards.length}`;
        wordEl.textContent = card.word;
        meaningEl.textContent = card.meaning;
        banglaMeaningEl.textContent = card.bangla_meaning;
        sentenceEl.textContent = card.sentence;
        flipCardEl.classList.remove("is-flipped");
        statusEl.textContent = "";
        setButtonsDisabled(false);
    }

    flipCardEl.addEventListener("click", (event) => {
        if (event.target.closest("#mark-learned-btn, #next-word-btn")) {
            return;
        }

        if (isCoarsePointer()) {
            flipCard();
            return;
        }

        const rect = flipCardEl.getBoundingClientRect();
        const relativeX = event.clientX - rect.left;
        const leftZone = rect.width * edgeZoneRatio;
        const rightZoneStart = rect.width * (1 - edgeZoneRatio);

        if (relativeX <= leftZone) {
            showPreviousCard();
        } else if (relativeX >= rightZoneStart) {
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
            markCurrentCardLearned();
        } else {
            showPreviousCard();
        }
    });

    document.addEventListener("click", (event) => {
        if (isCoarsePointer()) {
            return;
        }

        if (
            event.target.closest("#flashcard-flip") ||
            event.target.closest("#mark-learned-btn") ||
            event.target.closest("#next-word-btn")
        ) {
            return;
        }

        if (!hasActiveCard()) {
            return;
        }

        const leftZone = window.innerWidth * edgeZoneRatio;
        const rightZoneStart = window.innerWidth * (1 - edgeZoneRatio);

        if (event.clientX <= leftZone) {
            showPreviousCard();
        } else if (event.clientX >= rightZoneStart) {
            showNextCard();
        } else {
            flipCard();
        }
    });

    markLearnedBtn.addEventListener("click", () => {
        markCurrentCardLearned();
    });

    nextWordBtn.addEventListener("click", () => {
        showNextCard();
    });

    renderCard();
});
