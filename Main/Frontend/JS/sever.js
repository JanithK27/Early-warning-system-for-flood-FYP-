// server.js
const express = require("express");
const cors = require("cors");
const bcrypt = require("bcrypt");           // For password hashing
const nodemailer = require("nodemailer");   // For sending emails
const { OAuth2Client } = require("google-auth-library"); // For Google sign-in

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Fake DB (in-memory) - replace with a real database in production
let users = [];
console.log(users)
// 1) Sign-Up Endpoint
app.post("/signup", async (req, res) => {
  try {
    const { fullName, email, phone, address, location, password } = req.body;

    // Check if user already exists by email
    const existingUser = users.find((user) => user.email === email);
    if (existingUser) {
      return res
        .status(400)
        .json({ success: false, message: "Email already in use." });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create new user record
    const newUser = {
      fullName,
      email,
      phone,
      address,
      location,
      password: hashedPassword, // store hashed password
    };
    users.push(newUser);

    return res.json({ success: true, message: "User registered successfully." });
  } catch (error) {
    console.error("Sign-up error:", error);
    return res
      .status(500)
      .json({ success: false, message: "Internal server error." });
  }
});

// 2) Sign-In Endpoint
app.post("/signin", async (req, res) => {
  try {
    const { email, password } = req.body;

    // Check if user exists
    const foundUser = users.find((user) => user.email === email);
    if (!foundUser) {
      return res
        .status(401)
        .json({ success: false, message: "Invalid email or password." });
    }

    // Compare the hashed password
    const match = await bcrypt.compare(password, foundUser.password);
    if (!match) {
      return res
        .status(401)
        .json({ success: false, message: "Invalid email or password." });
    }

    // Sign-in successful
    return res.json({ success: true, message: "Sign-in successful." });
  } catch (error) {
    console.error("Sign-in error:", error);
    return res
      .status(500)
      .json({ success: false, message: "Internal server error." });
  }
});

// 3) Forgot Password Endpoint
app.post("/forgot-password", async (req, res) => {
  try {
    const { email } = req.body;

    // Find user by email
    let user = users.find((u) => u.email === email);
    if (!user) {
      return res
        .status(404)
        .json({ success: false, message: "Email not found." });
    }

    // Generate a temporary password or reset token
    const tempPassword = Math.random().toString(36).substring(2, 8);

    // Hash and update user's password with the temp password
    user.password = await bcrypt.hash(tempPassword, 10);

    // Configure nodemailer transport
    let transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: "yourgmail@gmail.com",       // your Gmail
        pass: "yourgmailpassword",         // your Gmail app password
      },
    });

    // Mail options
    let mailOptions = {
      from: "yourgmail@gmail.com",
      to: email,
      subject: "FloodGuard Password Reset",
      text: `Your temporary password is: ${tempPassword}`,
    };

    // Send email
    transporter.sendMail(mailOptions, (error, info) => {
      if (error) {
        console.error(error);
        return res
          .status(500)
          .json({ success: false, message: "Email send failure." });
      }
      return res.json({
        success: true,
        message: "Email sent successfully. Please check your inbox.",
      });
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: "Server error." });
  }
});

// 4) Google Sign-In Endpoint
const googleClient = new OAuth2Client("YOUR_GOOGLE_CLIENT_ID");
app.post("/google-signin", async (req, res) => {
  try {
    const { token } = req.body;
    const ticket = await googleClient.verifyIdToken({
      idToken: token,
      audience: "YOUR_GOOGLE_CLIENT_ID",
    });

    // Extract user info from token
    const payload = ticket.getPayload();
    const email = payload.email;

    // Check if user already exists
    let user = users.find((u) => u.email === email);
    if (!user) {
      // Create new user with partial info if not found
      user = { email, password: null }; // or mark password as google login
      users.push(user);
    }

    return res.json({ success: true, message: "Google sign-in success." });
  } catch (error) {
    console.error("Google sign-in error:", error);
    return res
      .status(401)
      .json({ success: false, message: "Google sign-in failed." });
  }
});

// Start the server
app.listen(5000, () => {
  console.log("Server running on http://localhost:5000");
});
