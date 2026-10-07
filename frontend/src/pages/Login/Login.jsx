import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const { login } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]:
        event.target.value,
    });

    setError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login({
        identifier:
          form.email.trim().toLowerCase(),
        password: form.password,
      });

      navigate("/dashboard", {
        replace: true,
      });
    } catch (error) {
      console.error(
        "Login failed:",
        error
      );

      const detail =
        error?.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(
          detail
            .map((item) => item?.msg)
            .filter(Boolean)
            .join(", ") ||
            "Invalid login details."
        );
      } else if (error?.request) {
        setError(
          "Unable to connect to the server. Please try again."
        );
      } else {
        setError(
          "Unable to sign in. Please check your email and password."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    const apiUrl =
      import.meta.env.VITE_API_URL ||
      "http://localhost:8000/api";

    window.location.href =
      `${apiUrl}/auth/google/login`;
  };

  return (
    <main className="auth-page">
      <section className="auth-layout">

        <div className="auth-brand-panel">
          <Link
            to="/"
            className="auth-logo"
          >
            Learnix
          </Link>

          <div>
            <span>
              PERSONALIZED LEARNING
            </span>

            <h1>
              Your knowledge.
              <br />
              Your journey.
            </h1>

            <p>
              Continue learning with
              recommendations designed
              around your goals, level
              and progress.
            </p>
          </div>

          <div className="auth-brand-footer">
            <span>
              Learn any topic
            </span>

            <span>
              Learn at your pace
            </span>
          </div>
        </div>

        <div className="auth-form-panel">
          <div className="auth-form-container">

            <div className="auth-heading">
              <span>
                WELCOME BACK
              </span>

              <h2>
                Sign in to Learnix
              </h2>

              <p>
                Continue your learning journey.
              </p>
            </div>

            <button
              type="button"
              className="google-button"
              onClick={handleGoogleLogin}
            >
              <span className="google-icon">
                G
              </span>

              <span>
                Continue with Google
              </span>
            </button>

            <div className="auth-divider">
              <span>
                or continue with email
              </span>
            </div>

            <form
              onSubmit={handleSubmit}
            >
              {error && (
                <div className="auth-error">
                  {error}
                </div>
              )}

              <div className="form-field">
                <label htmlFor="email">
                  Email address
                </label>

                <input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={handleChange}
                  autoComplete="email"
                  required
                />
              </div>

              <div className="form-field">
                <div className="field-label-row">
                  <label htmlFor="password">
                    Password
                  </label>

                  <Link to="/forgot-password">
                    Forgot password?
                  </Link>
                </div>

                <div className="password-input">
                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="Enter your password"
                    value={form.password}
                    onChange={handleChange}
                    autoComplete="current-password"
                    required
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(
                        (value) =>
                          !value
                      )
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showPassword
                      ? "Hide"
                      : "Show"}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="auth-submit"
                disabled={loading}
              >
                {loading
                  ? "Signing in..."
                  : "Sign in"}
              </button>
            </form>

            <p className="auth-switch">
              Don't have an account?{" "}
              <Link to="/register">
                Create an account
              </Link>
            </p>

          </div>
        </div>

      </section>
    </main>
  );
}

export default Login;

