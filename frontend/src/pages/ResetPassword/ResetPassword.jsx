import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import "./ResetPassword.css";
import api from "../../services/api";

function EyeIcon({ visible }) {
  return visible ? (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <circle
        cx="12"
        cy="12"
        r="2.8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M3 3l18 18"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="M10.6 6.2A9.7 9.7 0 0 1 12 6c6.5 0 10 6 10 6a18 18 0 0 1-3.1 3.4M6.3 6.9C3.6 8.5 2 12 2 12s3.5 6 10 6c1 0 1.9-.1 2.7-.4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!token) {
      setError("Invalid or missing password reset token.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post(
        "/auth/reset-password",
        {
          token,
          password,
        }
      );

      setSuccess(
        response.data?.message ||
          "Password changed successfully."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to reset your password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="reset-page">
      <section className="reset-card">
        <div className="reset-logo">L</div>

        <div className="reset-header">
          <h1>Create a new password</h1>

          <p>
            Choose a strong password for your Learnix
            account.
          </p>
        </div>

        {error && (
          <div className="reset-error">
            {error}
          </div>
        )}

        {success && (
          <div className="reset-success">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label htmlFor="reset-password">
            New password
          </label>

          <div className="reset-password-wrapper">
            <input
              id="reset-password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter new password"
              autoComplete="new-password"
              minLength={6}
              required
            />

            <button
              type="button"
              className="reset-password-toggle"
              onClick={() =>
                setShowPassword((value) => !value)
              }
              aria-label={
                showPassword
                  ? "Hide password"
                  : "Show password"
              }
            >
              <EyeIcon visible={showPassword} />
            </button>
          </div>

          <label htmlFor="reset-confirm-password">
            Confirm password
          </label>

          <div className="reset-password-wrapper">
            <input
              id="reset-confirm-password"
              type={
                showConfirmPassword
                  ? "text"
                  : "password"
              }
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
              placeholder="Confirm new password"
              autoComplete="new-password"
              minLength={6}
              required
            />

            <button
              type="button"
              className="reset-password-toggle"
              onClick={() =>
                setShowConfirmPassword(
                  (value) => !value
                )
              }
              aria-label={
                showConfirmPassword
                  ? "Hide confirm password"
                  : "Show confirm password"
              }
            >
              <EyeIcon
                visible={showConfirmPassword}
              />
            </button>
          </div>

          <button
            type="submit"
            className="reset-submit"
            disabled={loading || !token}
          >
            {loading
              ? "Updating..."
              : "Update password"}
          </button>
        </form>

        <Link
          to="/login"
          className="reset-back"
        >
          Back to login
        </Link>
      </section>
    </main>
  );
}