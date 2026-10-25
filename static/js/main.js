
"use strict";

/* =========================================
   CivicFix - Main JavaScript
========================================= */

document.addEventListener("DOMContentLoaded", () => {
    initMobileMenu();
    initFlashMessages();
    initConfirmActions();
});

/* Mobile navigation */
function initMobileMenu() {
    const menuToggle = document.getElementById("menuToggle");
    const navLinks = document.getElementById("navLinks");

    if (!menuToggle || !navLinks) return;

    menuToggle.addEventListener("click", () => {
        const isOpen = navLinks.classList.toggle("active");

        menuToggle.setAttribute("aria-expanded", String(isOpen));
        menuToggle.setAttribute(
            "aria-label",
            isOpen ? "Close navigation" : "Open navigation"
        );
    });

    navLinks.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            navLinks.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        });
    });

    document.addEventListener("click", (event) => {
        if (
            !navLinks.contains(event.target) &&
            !menuToggle.contains(event.target)
        ) {
            navLinks.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        }
    });
}

/* Flash message dismissal */
function initFlashMessages() {
    document.querySelectorAll(".flash-message").forEach((message) => {
        message.setAttribute("role", "status");

        // Automatically hide after 7 seconds.
        window.setTimeout(() => {
            message.classList.add("flash-hidden");

            window.setTimeout(() => {
                message.remove();
            }, 300);
        }, 7000);
    });
}

/* Confirm potentially destructive actions */
function initConfirmActions() {
    document.querySelectorAll("[data-confirm]").forEach((element) => {
        element.addEventListener("click", (event) => {
            const message =
                element.dataset.confirm ||
                "Are you sure you want to continue?";

            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
}

/* Common API helper */
async function civicFixRequest(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers: {
            ...(options.headers || {})
        }
    });

    const contentType = response.headers.get("content-type") || "";

    let data;

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        data = { message: await response.text() };
    }

    if (!response.ok) {
        throw new Error(
            data.message || `Request failed (${response.status})`
        );
    }

    return data;
}

/* Make helper available to other scripts */
window.civicFixRequest = civicFixRequest;
