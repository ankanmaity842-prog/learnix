import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useTheme } from "../../hooks/useTheme";
import "./ProfileMenu.css";

function getInitials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);

  if (parts.length === 0) {
    return "?";
  }

  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }

  return (
    parts[0].charAt(0) +
    parts[parts.length - 1].charAt(0)
  ).toUpperCase();
}

function ProfileMenu({ user, onNavigate }) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  const {
    theme,
    setTheme,
  } = useTheme();

  const initials = getInitials(user?.name);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      document.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, []);

  const closeMenu = () => {
    setIsOpen(false);

    if (onNavigate) {
      onNavigate();
    }
  };

  const handleThemeChange = (value) => {
    setTheme(value);
  };

  return (
    <div className="profile-menu" ref={menuRef}>

      <button
        type="button"
        className="profile-avatar-button"
        onClick={() => setIsOpen((value) => !value)}
        aria-label="Open profile menu"
        aria-expanded={isOpen}
      >
        <span className="profile-avatar">
          {initials}
        </span>
      </button>

      {isOpen && (
        <div
          className="profile-dropdown"
          role="menu"
        >

          {/* User information */}
          <div className="profile-header">

            <div className="profile-large-avatar">
              {initials}
            </div>

            <div className="profile-user-info">

              <strong>
                {user?.name || "Learnix User"}
              </strong>

              {user?.username && (
                <span>
                  @{user.username}
                </span>
              )}

              {user?.email && (
                <small>
                  {user.email}
                </small>
              )}

            </div>

          </div>

          <div className="profile-divider" />

          {/* Learning navigation */}
          <div className="profile-links">

            <Link
              to="/profile"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ◉
              </span>

              <span>Profile</span>
            </Link>

            <Link
              to="/dashboard"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ▣
              </span>

              <span>My Learning</span>
            </Link>

            <Link
              to="/dashboard"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ◫
              </span>

              <span>Progress</span>
            </Link>

            <Link
              to="/search"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ★
              </span>

              <span>Recommendations</span>
            </Link>

            <Link
              to="/knowledge"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ◇
              </span>

              <span>Knowledge &amp; Skills</span>
            </Link>

            <Link
              to="/notes"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ▤
              </span>

              <span>My Notes</span>
            </Link>

            <Link
              to="/learning-path"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ↗
              </span>

              <span>Learning Path</span>
            </Link>

          </div>

          <div className="profile-divider" />

          {/* Settings */}
          <div className="profile-settings">

            <Link
              to="/settings"
              onClick={closeMenu}
              role="menuitem"
            >
              <span className="profile-link-icon">
                ⚙
              </span>

              <span>Settings</span>
            </Link>

          </div>

          <div className="profile-divider" />

          {/* Theme */}
          <div className="profile-theme">

            <div className="profile-theme-heading">
              <span className="profile-link-icon">
                {theme === "dark" ? "☾" : "☀"}
              </span>

              <span>Appearance</span>
            </div>

            <div className="theme-options">

              <button
                type="button"
                className={
                  theme === "system"
                    ? "theme-option active"
                    : "theme-option"
                }
                onClick={() =>
                  handleThemeChange("system")
                }
              >
                System
              </button>

              <button
                type="button"
                className={
                  theme === "light"
                    ? "theme-option active"
                    : "theme-option"
                }
                onClick={() =>
                  handleThemeChange("light")
                }
              >
                Light
              </button>

              <button
                type="button"
                className={
                  theme === "dark"
                    ? "theme-option active"
                    : "theme-option"
                }
                onClick={() =>
                  handleThemeChange("dark")
                }
              >
                Dark
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}

export default ProfileMenu;