import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

function OAuthCallback() {
  const navigate = useNavigate();

  const [searchParams] =
    useSearchParams();

  const { refreshUser } = useAuth();

  const [error, setError] =
    useState("");

  useEffect(() => {
    const completeGoogleLogin =
      async () => {
        const token =
          searchParams.get("token");

        const oauthError =
          searchParams.get("error");

        if (oauthError) {
          setError(
            "Google authentication failed. Please try again."
          );
          return;
        }

        if (!token) {
          setError(
            "Google authentication did not return a valid token."
          );
          return;
        }

        try {
          localStorage.setItem(
            "learnix_token",
            token
          );

          await refreshUser();

          window.history.replaceState(
            {},
            document.title,
            "/oauth/callback"
          );

          navigate("/dashboard", {
            replace: true,
          });
        } catch (error) {
          console.error(
            "Google authentication failed:",
            error
          );

          localStorage.removeItem(
            "learnix_token"
          );

          setError(
            "Unable to complete Google login. Please try again."
          );
        }
      };

    completeGoogleLogin();
  }, [
    navigate,
    refreshUser,
    searchParams,
  ]);

  if (error) {
    return (
      <main className="auth-page">
        <div className="auth-form-container">
          <div className="auth-error">
            {error}
          </div>

          <button
            type="button"
            className="auth-submit"
            onClick={() =>
              navigate("/login", {
                replace: true,
              })
            }
          >
            Return to login
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="auth-page">
      <div className="auth-form-container">
        <div className="auth-heading">
          <span>
            AUTHENTICATING
          </span>

          <h2>
            Signing you in...
          </h2>

          <p>
            Please wait while we complete
            your Google authentication.
          </p>
        </div>
      </div>
    </main>
  );
}

export default OAuthCallback;