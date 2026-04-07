document.addEventListener("DOMContentLoaded", () => {
    const cards = Array.from(document.querySelectorAll(".incident-section"))
    const modal = document.querySelector(".modal");
    const modalContent = document.querySelector(".modal-content");

    if (cards.length === 0) return;
    const container = cards[0].parentElement;

    const sortedCardsNewToOld = cards.sort((a, b) => {
        const ta = Number(a.dataset.timeTs || 0);
        const tb = Number(b.dataset.timeTs || 0);
        return tb - ta;
    });

    const sortedCardsOldToNew = cards.sort((a, b) => {
        const ta = Number(a.dataset.timeTs || 0);
        const tb = Number(b.dataset.timeTs || 0);
        return ta - tb;
    });

    const sortedCardsAlphabetically = cards.sort((a, b) => {
        const titleA = a.querySelector("h2") ? a.querySelector("h2").textContent.trim() : "";
        const titleB = b.querySelector("h2") ? b.querySelector("h2").textContent.trim() : "";
        return titleA.localeCompare(titleB);
    });

    // sortedCardsNewToOld.forEach((card) => container.appendChild(card));
    sortedCardsOldToNew.forEach((card) => container.appendChild(card));
    // sortedCardsAlphabetically.forEach((card) => container.appendChild(card));

    cards.forEach((card) => {
        const button = card.querySelector(".toggle-details-btn");
        button.addEventListener("click", () => {
            const fullCard = document.querySelector(`#${card.getAttribute('data-product-id')}-hidden`);

            if (modal.style.display === "block") {
                modal.style.display = "none";
                modalContent.innerHTML = "";
            } else {
                modalContent.innerHTML = fullCard.innerHTML;
                modal.style.display = "block";
            }
        });
    });
    window.onclick = function(event) {
        if (event.target === modal) {
        modal.style.display = "none";
        }
    };
});