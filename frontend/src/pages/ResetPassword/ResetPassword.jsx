
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import "./ResetPassword.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

export default function ResetPassword() {
  const location = useLocation();
  const navigate = useNavigate();

  const [email, setEmail] = useState(
    location.state?.email || ""
  );
  const [challengeToken, setChallengeToken] = useState(
    location.state?.challengeToken || ""
  );
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleCodeChange = (event) => {
    const digits = event.target.value.replace(/\D/g, "").slice(0, 6);
    setCode(digits);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!email || !challengeToken) {
      setError(
        "Your reset session is missing or expired. Please request a new code."
      );
      return;
    }

    if (!/^\d{6}$/.test(code)) {
      setError("Enter the complete 6-digit verification code.");
      return;
    }

    if (password.length < 8) {
      setError("Your new password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      const response = await axios.post(
        `${API_URL}/auth/reset-password`,
        {
          email: email.trim().toLowerCase(),
          code,
          challenge_token: challengeToken,
          password,
          confirm_password: confirmPassword,
        }
      );

      setSuccess(
        response.data?.message ||
          "Your password has been reset successfully."
      );

      setCode("");
      setPassword("");
      setConfirmPassword("");

      // Allow the success message to be read before navigating.
      window.setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1500);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to reset your password. Check your code and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setSuccess("");

    if (!email.trim()) {
      setError("Please return to the previous page and enter your email.");
      return;
    }

    try {
      setResending(true);

      const response = await axios.post(
        `${API_URL}/auth/forgot-password`,
        { email: email.trim().toLowerCase() }
      );

      if (response.data?.challenge_token) {
        setChallengeToken(response.data.challenge_token);
        setCode("");
        setSuccess("A new code has been requested. Check your email.");
      } else {
        setSuccess(
          response.data?.message ||
            "If the account is eligible, a new code will be sent."
        );
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to request a new code. Please try again."
      );
    } finally {
      setResending(false);
    }
  };

  if (!email || !challengeToken) {
    return (
      <main className="reset-page">
        <section className="reset-card">
          <h1>Reset your password</h1>
          <p className="reset-description">
            Request a reset code first to begin changing your password.
          </p>
          <Link to="/forgot-password" className="reset-login-button">
            Request a reset code
          </Link>
          <Link to="/login" className="reset-back-link">
            Back to login
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="reset-page">
      <section className="reset-card">
        <div className="reset-icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="4"
              y="10"
              width="16"
              height="11"
              rx="2.5"
              stroke="currentColor"
              strokeWidth="1.8"
            />
            <path
              d="M8 10V7a4 4 0 0 1 8 0v3"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
            <circle cx="12" cy="15" r="1.2" fill="currentColor" />
          </svg>
        </div>

        <h1>Create a new password</h1>

        <p className="reset-description">
          Enter the 6-digit code sent to{" "}
          <strong className="reset-email">{email}</strong>, then choose
          your new password.
        </p>

        <form className="reset-form" onSubmit={handleSubmit}>
          <label htmlFor="reset-code">Verification code</label>
          <input
            id="reset-code"
            className="reset-code-input"
            name="code"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            placeholder="000000"
            value={code}
            onChange={handleCodeChange}
            maxLength={6}
            pattern="[0-9]{6}"
            aria-describedby="reset-code-help"
            required
            disabled={loading}
          />

          <p id="reset-code-help" className="reset-field-help">
            Enter the 6-digit code from your email.
          </p>

          <div className="reset-password-field">
            <label htmlFor="reset-password">New password</label>
            <div className="reset-password-wrapper">
              <input
                id="reset-password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="At least 8 characters"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
                disabled={loading}
              />
              <button
                type="button"
                className="reset-eye-button"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                aria-pressed={showPassword}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <div className="reset-password-field">
            <label htmlFor="reset-confirm-password">
              Confirm new password
            </label>
            <div className="reset-password-wrapper">
              <input
                id="reset-confirm-password"
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
                disabled={loading}
              />
              <button
                type="button"
                className="reset-eye-button"
                onClick={() =>
                  setShowConfirmPassword((visible) => !visible)
                }
                aria-label={
                  showConfirmPassword
                    ? "Hide confirm password"
                    : "Show confirm password"
                }
                aria-pressed={showConfirmPassword}
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {error && (
            <p className="reset-message reset-error" role="alert">
              {error}
            </p>
          )}

          {success && (
            <p className="reset-message reset-success" role="status">
              {success}
            </p>
          )}

          <button
            type="submit"
            className="reset-submit"
            disabled={loading || resending}
          >
            {loading ? "Resetting password..." : "Reset password"}
          </button>
        </form>

        <div className="reset-resend">
          <span>Didn't receive the code?</span>
          <button
            type="button"
            onClick={handleResend}
            disabled={resending || loading}
          >
            {resending ? "Requesting..." : "Send a new code"}
          </button>
        </div>

        <Link to="/login" className="reset-back-link">
          Back to login
        </Link>
      </section>
    </main>
  );
}

