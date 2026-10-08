import React from "react";
import useTheme from "../../hooks/useTheme";
import "./Settings.css";

function Settings() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="settings-page">
      <div className="settings-header">
        <span>APPEARANCE</span>

        <h1>Customize your experience</h1>

        <p>
          Choose how Learnix should look across
          your devices.
        </p>
      </div>

      <div className="settings-card">
        <div className="settings-card-header">
          <div>
            <span>THEME</span>

            <h2>Interface appearance</h2>

            <p>
              Select a theme that feels comfortable
              for your learning experience.
            </p>
          </div>
        </div>

        <div className="theme-options">
          <button
            type="button"
            className={`theme-option ${
              theme === "system"
                ? "active"
                : ""
            }`}
            onClick={() => setTheme("system")}
          >
            <div className="theme-preview system-preview">
              <div />
              <div />
            </div>

            <div className="theme-option-content">
              <strong>System</strong>

              <span>
                Follow your device preference
              </span>
            </div>

            {theme === "system" && (
              <span className="theme-check">
                ✓
              </span>
            )}
          </button>

          <button
            type="button"
            className={`theme-option ${
              theme === "light"
                ? "active"
                : ""
            }`}
            onClick={() => setTheme("light")}
          >
            <div className="theme-preview light-preview">
              <div />
              <div />
            </div>

            <div className="theme-option-content">
              <strong>Light</strong>

              <span>
                Bright and clean appearance
              </span>
            </div>

            {theme === "light" && (
              <span className="theme-check">
                ✓
              </span>
            )}
          </button>

          <button
            type="button"
            className={`theme-option ${
              theme === "dark"
                ? "active"
                : ""
            }`}
            onClick={() => setTheme("dark")}
          >
            <div className="theme-preview dark-preview">
              <div />
              <div />
            </div>

            <div className="theme-option-content">
              <strong>Dark</strong>

              <span>
                Deep aurora-inspired interface
              </span>
            </div>

            {theme === "dark" && (
              <span className="theme-check">
                ✓
              </span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings;