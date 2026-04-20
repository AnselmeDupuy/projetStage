document.addEventListener("DOMContentLoaded", () => {
    const cards = Array.from(document.querySelectorAll(".incident-section"))
    const nav = document.querySelector("nav");
    const navToggleBtn = document.getElementById("nav-toggle-btn");
    const navLinks = Array.from(document.querySelectorAll("nav .nav-item a"));
    const modal = document.querySelector(".modal");
    const modalContent = document.querySelector(".modal-content");
    const navItems = Array.from(document.querySelectorAll(".nav-item"));

    const sortNewToOldBtn = document.getElementById("sort-new-to-old-btn");
    const sortOldToNewBtn = document.getElementById("sort-old-to-new-btn");
    const sortAlphabeticallyBtn = document.getElementById("sort-alphabetically-btn");
    const sortSeverityBtn = document.getElementById("sort-severity-btn");

    if (cards.length === 0 || navItems.length === 0) return;
    const cardsContainer = cards[0].parentElement;
    const navContainer = navItems[0].parentElement;

    const sortedNavItemsNewToOld = [...navItems].sort((a, b) => {
        const ta = Number(a.dataset.timeTs || 0);
        const tb = Number(b.dataset.timeTs || 0);
        return tb - ta;
    });

    const sortedNavItemsOldToNew = [...navItems].sort((a, b) => {
        const ta = Number(a.dataset.timeTs || 0);
        const tb = Number(b.dataset.timeTs || 0);
        return ta - tb;
    });

    const getLinkedCardTitle = (navItem) => {
        const link = navItem.querySelector("a");
        if (!link) return "";

        const targetCard = document.querySelector(link.getAttribute("href"));
        return targetCard?.querySelector("h1")?.textContent.trim() || "";
    };

    const sortedNavItemsAlphabetically = [...navItems].sort((a, b) => {
        const titleA = getLinkedCardTitle(a);
        const titleB = getLinkedCardTitle(b);
        return titleA.localeCompare(titleB);
    });

    const sortedNavItemsSeverity = [...navItems].sort((a, b) => {
        const severityA = Number(a.dataset.severity || 0);
        const severityB = Number(b.dataset.severity || 0);
        return severityB - severityA;
    });

    const sortedCardsNewToOld = [...cards].sort((a, b) => {
        const ta = Number(a.dataset.timeTs || 0);
        const tb = Number(b.dataset.timeTs || 0);
        return tb - ta;
    });

    const sortedCardsOldToNew = [...cards].sort((a, b) => {
        const ta = Number(a.dataset.timeTs || 0);
        const tb = Number(b.dataset.timeTs || 0);
        return ta - tb;
    });

    const sortedCardsAlphabetically = [...cards].sort((a, b) => {
        const titleA = a.querySelector("h1") ? a.querySelector("h1").textContent.trim() : "";
        const titleB = b.querySelector("h1") ? b.querySelector("h1").textContent.trim() : "";
        return titleA.localeCompare(titleB);
    });

    const sortedCardsSeverity = [...cards].sort((a, b) => {
        const severityA = Number(a.dataset.severity || 0);
        const severityB = Number(b.dataset.severity || 0);
        return severityB - severityA;
    });

    const applyOrder = (orderedCards, orderedNavItems) => {
        orderedCards.forEach((card) => cardsContainer.appendChild(card));
        orderedNavItems.forEach((item) => navContainer.appendChild(item));
    };

    if (sortNewToOldBtn) {
        sortNewToOldBtn.addEventListener("click", (event) => {
            applyOrder(sortedCardsNewToOld, sortedNavItemsNewToOld);
        });
    }

    if (sortOldToNewBtn) {
        sortOldToNewBtn.addEventListener("click", (event) => {
            applyOrder(sortedCardsOldToNew, sortedNavItemsOldToNew);

        });
    }

    if (sortAlphabeticallyBtn) {
        sortAlphabeticallyBtn.addEventListener("click", (event) => {
            applyOrder(sortedCardsAlphabetically, sortedNavItemsAlphabetically);
        });
    }

    if (sortSeverityBtn) {
        sortSeverityBtn.addEventListener("click", (event) => {
            applyOrder(sortedCardsSeverity, sortedNavItemsSeverity);
        });
    }

    if (nav && navToggleBtn) {
        navToggleBtn.addEventListener("click", () => {
            nav.classList.toggle("nav-open");
            navToggleBtn.setAttribute("aria-expanded", String(nav.classList.contains("nav-open")));
        });

        navLinks.forEach((link) => {
            link.addEventListener("click", () => {
                if (window.innerWidth <= 1100) {
                    nav.classList.remove("nav-open");
                    navToggleBtn.setAttribute("aria-expanded", "false");
                }
            });
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 1100) {
                nav.classList.remove("nav-open");
                navToggleBtn.setAttribute("aria-expanded", "false");
            }
        });
    }


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