document.getElementById("signup-form").addEventListener("submit", async function(e) {
  e.preventDefault(); // Prevent default submission

  const fullName = document.getElementById("full-name").value.trim();
  const email = document.getElementById("email").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const address = document.getElementById("address").value.trim();
  const location = document.getElementById("location").value;
  const password = document.getElementById("password").value.trim();
  const confirmPassword = document.getElementById("confirm-password").value.trim();

  // Password match check
  if (password !== confirmPassword) {
    alert("Passwords do not match. Please try again.");
    return;
  }

  // Construct data object
  const signupData = { fullName, email, phone, address, location, password };

  try {
    // POST to server.js sign-up endpoint
    const response = await fetch("http://localhost:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(signupData),
    });

    const result = await response.json();
    if (response.ok && result.success) {
      alert("Sign up successful!");
      // Redirect to index.html after successful sign up
      window.location.href = "index.html";
    } else {
      alert(result.message || "Sign up failed.");
    }
  } catch (error) {
    console.error("Error during sign-up:", error);
    alert("An error occurred. Please try again.");
  }
});
