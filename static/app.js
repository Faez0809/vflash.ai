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
    const detailsEl = document.querySelector("#flashcard-details");
    const meaningEl = document.querySelector("#flashcard-meaning");
    const sentenceEl = document.querySelector("#flashcard-sentence");
    const statusEl = document.querySelector("#flashcard-status");
    const showMeaningBtn = document.querySelector("#show-meaning-btn");
    const markLearnedBtn = document.querySelector("#mark-learned-btn");
    const nextWordBtn = document.querySelector("#next-word-btn");

    let currentIndex = 0;

    function setButtonsDisabled(disabled) {
        showMeaningBtn.disabled = disabled;
        markLearnedBtn.disabled = disabled;
        nextWordBtn.disabled = disabled;
    }

    function renderCard() {
        if (!cards.length || currentIndex >= cards.length) {
            countEl.textContent = "Study complete";
            wordEl.textContent = "No more words to study";
            detailsEl.classList.add("is-hidden");
            statusEl.textContent = "";
            setButtonsDisabled(true);
            return;
        }

        const card = cards[currentIndex];
        countEl.textContent = `Word ${currentIndex + 1} of ${cards.length}`;
        wordEl.textContent = card.word;
        meaningEl.textContent = card.meaning;
        sentenceEl.textContent = card.sentence;
        detailsEl.classList.add("is-hidden");
        statusEl.textContent = "";
        setButtonsDisabled(false);
    }

    showMeaningBtn.addEventListener("click", () => {
        detailsEl.classList.remove("is-hidden");
    });

    markLearnedBtn.addEventListener("click", async () => {
        const card = cards[currentIndex];
        if (!card) {
            return;
        }

        try {
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
        }
    });

    nextWordBtn.addEventListener("click", () => {
        if (!cards.length) {
            renderCard();
            return;
        }

        currentIndex += 1;
        renderCard();
    });

    renderCard();
});
