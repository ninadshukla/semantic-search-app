import { useState } from "react";
import "./App.css";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);

  const handleAuth = async () => {
    if (!email.trim() || !password.trim()) {
      alert("Please enter email and password.");
      return;
    }

    const endpoint = isRegistering
      ? "http://localhost:8000/auth/register"
      : "http://localhost:8000/auth/login";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Authentication failed.");
        return;
      }

      // Registration successful
      if (isRegistering) {
        alert("Registration successful! Please login.");
        setIsRegistering(false);
        return;
      }

      // Login successful
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("email", email);

      onLogin();
    } catch (error) {
      console.error(error);
      alert("Could not connect to backend.");
    }
  };

  return (
    <div className="container">
      <h1>{isRegistering ? "Register" : "Login"}</h1>

      <div className="search-bar">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleAuth();
            }
          }}
        />

        <button onClick={handleAuth}>
          {isRegistering ? "Register" : "Login"}
        </button>
      </div>

      <br />

      <button
        onClick={() => setIsRegistering(!isRegistering)}
        className="toggle-button"
      >
        {isRegistering
          ? "Already have an account? Login"
          : "Don't have an account? Register"}
      </button>
    </div>
  );
}

export default LoginPage;