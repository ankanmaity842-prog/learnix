import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../context/ThemeContext";
import "./Settings.css";

function Settings() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();

  return (
    <main className="settings-page">

      <div className="settings-container">

        <div className="settings-heading">
          <h1>Settings</h1>
          <p>
            Manage your Learnix account and preferences.
          </p>
        </div>

        <section className="settings-card">

          <div className="settings-card-heading">
            <h2>Appearance</h2>
            <p>
              Choose how Learnix looks on your device.
            </p>
          </div>

          <div className="settings-row">
            <div>
              <strong>Theme</strong>
              <span>
                Select your preferred appearance.
              </span>
            </div>

            <div className="theme-options">

              <button
                type="button"
                className={theme === "system" ? "selected" : ""}
                onClick={() => setTheme("system")}
              >
                System
              </button>

              <button
                type="button"
                className={theme === "light" ? "selected" : ""}
                onClick={() => setTheme("light")}
              >
                Light
              </button>

              <button
                type="button"
                className={theme === "dark" ? "selected" : ""}
                onClick={() => setTheme("dark")}
              >
                Dark
              </button>

            </div>
          </div>

        </section>

        <section className="settings-card">

          <div className="settings-card-heading">
            <h2>Account</h2>
            <p>
              Your Learnix account information.
            </p>
          </div>

          <div className="account-details">

            <div className="account-detail">
              <span>Full name</span>
              <strong>{user?.name || "—"}</strong>
            </div>

            <div className="account-detail">
              <span>Username</span>
              <strong>
                {user?.username
                  ? `@${user.username}`
                  : "—"}
              </strong>
            </div>

            <div className="account-detail">
              <span>Email</span>
              <strong>{user?.email || "—"}</strong>
            </div>

          </div>

        </section>

        <section className="settings-card">

          <div className="settings-card-heading">
            <h2>Security</h2>
            <p>
              Keep your Learnix account secure.
            </p>
          </div>

          <div className="settings-action">
            <div>
              <strong>Change password</strong>
              <span>
                Update your account password.
              </span>
            </div>

            <a href="/forgot-password">
              Change
            </a>
          </div>

        </section>

      </div>

    </main>
  );
}

export default Settings;