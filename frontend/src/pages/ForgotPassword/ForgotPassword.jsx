
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./ForgotPassword.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

export default function ForgotPassword() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    const normalizedEmail = email.trim().toLowerCase();

    if (!normalizedEmail) {
      setError("Please enter your email address.");
      return;
    }

    try {
      setLoading(true);

      const response = await axios.post(
        `${API_URL}/auth/forgot-password`,
        { email: normalizedEmail }
      );

      const message =
        response.data?.message ||
        "If an eligible account exists, reset instructions will be sent.";

      const challengeToken = response.data?.challenge_token;

      if (challengeToken) {
        navigate("/reset-password", {
          state: {
            email: normalizedEmail,
            challengeToken,
          },
        });
        return;
      }

      // Keep the response generic to avoid revealing whether an account exists.
      setSuccess(message);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to process your request. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="forgot-page">
      <section className="forgot-card">
        <div className="forgot-icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="3"
              y="5"
              width="18"
              height="14"
              rx="3"
              stroke="currentColor"
              strokeWidth="1.8"
            />
            <path
              d="M4 7L12 13L20 7"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <h1>Forgot password?</h1>
        <p className="forgot-description">
          Enter the email address associated with your Learnix account.
          If the account is eligible, we’ll send you a 6-digit reset code.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="forgot-email">Email address</label>

          <input
            id="forgot-email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
            disabled={loading}
          />

          {error && (
            <p className="forgot-message forgot-error" role="alert">
              {error}
            </p>
          )}

          {success && (
            <p className="forgot-message forgot-success" role="status">
              {success}
            </p>
          )}

          <button
            type="submit"
            className="forgot-submit"
            disabled={loading}
          >
            {loading ? "Sending code..." : "Send reset code"}
          </button>
        </form>

        <Link to="/login" className="forgot-back-link">
          <span aria-hidden="true">←</span> Back to login
        </Link>
      </section>
    </main>
  );
}

