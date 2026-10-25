
"use strict";

/* =========================================
   CivicFix - Location Handler
========================================= */

document.addEventListener("DOMContentLoaded", () => {
    const locationButton = document.getElementById("getLocationBtn");
    const latitudeInput = document.getElementById("latitude");
    const longitudeInput = document.getElementById("longitude");
    const locationMessage = document.getElementById("locationMessage");

    if (
        !locationButton ||
        !latitudeInput ||
        !longitudeInput
    ) {
        return;
    }

    function showMessage(message, type = "info") {
        if (!locationMessage) return;

        locationMessage.textContent = message;
        locationMessage.className = `location-message ${type}`;
        locationMessage.setAttribute("role", "status");
    }

    locationButton.addEventListener("click", () => {
        if (!("geolocation" in navigator)) {
            showMessage(
                "Your browser does not support location access.",
                "error"
            );
            return;
        }

        if (!window.isSecureContext) {
            showMessage(
                "Location access requires HTTPS or localhost.",
                "error"
            );
            return;
        }

        locationButton.disabled = true;
        showMessage("Getting your location...", "info");

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;

                latitudeInput.value = latitude.toFixed(6);
                longitudeInput.value = longitude.toFixed(6);

                showMessage(
                    "Location captured successfully.",
                    "success"
                );

                locationButton.disabled = false;
            },

            (error) => {
                let message =
                    "Unable to get your location. You can enter it manually.";

                if (error.code === error.PERMISSION_DENIED) {
                    message =
                        "Location permission denied. Allow location access or enter your address manually.";
                } else if (error.code === error.TIMEOUT) {
                    message =
                        "Location request timed out. Please try again.";
                }

                showMessage(message, "error");
                locationButton.disabled = false;
            },

            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 60000
            }
        );
    });
});
