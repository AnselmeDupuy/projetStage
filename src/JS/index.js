document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".incident-section");
    const modal = document.querySelector(".modal");
    const modalContent = document.querySelector(".modal-content");

    cards.forEach((card) => {
        card.addEventListener("click", () => {
        if (modal.style.display === "block") {
            modal.style.display = "none";
            modalContent.innerHTML = "";
        } else {
            modal.scrollTop
            modalContent.innerHTML = card.innerHTML;
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