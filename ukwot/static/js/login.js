/*
  Wait until the page has fully loaded before accessing form elements.
*/
document.addEventListener("DOMContentLoaded", function () {
  const usernameInput = document.getElementById("id_username");
  const passwordInput = document.getElementById("id_password");

  // Add helpful placeholders
  if (usernameInput) {
    usernameInput.placeholder = "Enter your username";
  }

  if (passwordInput) {
    passwordInput.placeholder = "Enter your password";
  }
});

/*
  Toggle password visibility.
  This allows users to check their input and reduces login errors.
*/
function togglePassword() {
  const passwordInput = document.getElementById("id_password");
  const toggleButton = document.querySelector(".toggle-password");

  if (!passwordInput || !toggleButton) return;

  const isHidden = passwordInput.type === "password";

  passwordInput.type = isHidden ? "text" : "password";
  toggleButton.textContent = isHidden ? "Hide" : "Show";

  // Update accessibility state
  toggleButton.setAttribute("aria-pressed", isHidden ? "true" : "false");
}