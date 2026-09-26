import { useState } from "react";
import { Link } from "react-router-dom";

import "./ForgotPassword.css";
import api from "../../services/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setMessage("");
    setError("");

    try {
      const response = await api.post(
        "/auth/forgot-password",
        { email }
      );

      setMessage(
        response.data?.message ||
          "If the email is registered, a password reset link has been sent."
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to process your request."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="forgot-page">
      <section className="forgot-card">
        <div className="forgot-logo">L</div>

        <div className="forgot-header">
          <h1>Forgot your password?</h1>

          <p>
            Enter the email associated with your Learnix
            account and we'll send you a password reset link.
          </p>
        </div>

        {message && (
          <div className="forgot-success">
            {message}
          </div>
        )}

        {error && (
          <div className="forgot-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label htmlFor="forgot-email">
            Email address
          </label>

          <input
            id="forgot-email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            placeholder="Enter your email"
            autoComplete="email"
            required
          />

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Sending..."
              : "Send reset link"}
          </button>
        </form>

        <Link
          to="/login"
          className="forgot-back"
        >
          Back to login
        </Link>
      </section>
    </main>
  );
}