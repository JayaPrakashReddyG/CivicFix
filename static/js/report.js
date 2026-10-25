
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#issueForm");
    const messageBox = document.querySelector("#formMessage");
    const submitBtn = document.querySelector("#submitReportBtn");

    // Check whether all required HTML elements exist
    if (!form || !messageBox || !submitBtn) {
        console.error(
            "CivicFix: Report form elements not found. Check issueForm, formMessage and submitReportBtn IDs."
        );
        return;
    }

    // Safely escape text before displaying it in HTML
    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    }

    // Display a message to the user
    function showMessage(message, type) {
        messageBox.hidden = false;
        messageBox.className = `form-message ${type}`;
        messageBox.textContent = message;
    }

    // Handle issue form submission without navigating to the JSON response
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        const originalButtonText = submitBtn.textContent;

        messageBox.hidden = false;
        messageBox.className = "form-message";
        messageBox.textContent = "";

        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting your issue...";

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json"
                }
            });

            // Handle unexpected non-JSON server responses
            const contentType = response.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {
                throw new Error(
                    "The server returned an unexpected response. Please refresh the page and try again."
                );
            }

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message || "Unable to submit your issue. Please try again."
                );
            }

            const issue = result.issue || {};

            // Show the success card on the same page
            messageBox.className = "form-message success-message";
            messageBox.innerHTML = `
                <div class="success-content">
                    <div class="success-icon" aria-hidden="true">✓</div>

                    <h3>Issue Reported Successfully!</h3>

                    <p>
                        Thank you for helping improve our community.
                        Your complaint has been received successfully.
                    </p>

                    <p>
                        Our team will review your issue and work to resolve it
                        as soon as possible.
                    </p>

                    <div class="success-details">
                        <p>
                            <strong>Complaint ID:</strong>
                            #${escapeHTML(issue.id ?? "N/A")}
                        </p>

                        <p>
                            <strong>Title:</strong>
                            ${escapeHTML(issue.title ?? "Your complaint")}
                        </p>

                        <p>
                            <strong>Category:</strong>
                            ${escapeHTML(issue.category ?? "General")}
                        </p>

                        <p>
                            <strong>Status:</strong>
                            <span class="pending-status">
                                ${escapeHTML(issue.status ?? "Pending")}
                            </span>
                        </p>
                    </div>

                    <p class="success-footer">
                        You can track your complaint in
                        <strong>My Issues</strong>.
                    </p>

                    <a class="success-link" href="/api/issues/my-page">
                        View My Issues
                    </a>
                </div>
            `;

            // Reset the form after successful submission
            form.reset();

            // Clear the uploaded image preview
            const preview = document.querySelector("#uploadPreview");
            if (preview) {
                preview.hidden = true;
            }

            const imagePreview = document.querySelector("#imagePreview");
            if (imagePreview) {
                imagePreview.removeAttribute("src");
            }

            // Scroll to the success confirmation
            messageBox.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        } catch (error) {
            console.error("CivicFix issue submission error:", error);

            showMessage(
                error.message || "Something went wrong. Please try again.",
                "error-message"
            );

            messageBox.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalButtonText;
        }
    });
});
