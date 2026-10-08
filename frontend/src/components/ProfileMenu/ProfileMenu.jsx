import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
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

    document.addEventListener("mousedown", handleOutsideClick);

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

    document.addEventListener("keydown", handleEscape);

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
        <div className="profile-dropdown" role="menu">
          <div className="profile-header">
            <div className="profile-large-avatar">
              {initials}
            </div>

            <div className="profile-user-info">
              <strong>
                {user?.name || "Learnix User"}
              </strong>

              {user?.username && (
                <span>@{user.username}</span>
              )}
            </div>
          </div>

          <div className="profile-divider" />

          <div className="profile-links">
            <Link
              to="/profile"
              onClick={closeMenu}
              role="menuitem"
            >
              <span>Profile</span>
            </Link>

            <Link
              to="/dashboard"
              onClick={closeMenu}
              role="menuitem"
            >
              <span>My Learning</span>
            </Link>

            <Link
              to="/settings"
              onClick={closeMenu}
              role="menuitem"
            >
              <span>Settings</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfileMenu;