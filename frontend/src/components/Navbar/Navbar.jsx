
import { useState } from "react";
import { Link, NavLink } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import ProfileMenu from "../ProfileMenu/ProfileMenu";

import "./Navbar.css";

function Navbar() {
  const [open, setOpen] = useState(false);

  const {
    user,
    loading,
    logout,
  } = useAuth();

  const closeMenu = () => {
    setOpen(false);
  };

  const handleLogout = async () => {
    closeMenu();

    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <header className="navbar">
      <div className="navbar-inner">

        {/* Brand */}
        <Link
          to="/"
          className="brand"
          onClick={closeMenu}
          aria-label="Learnix home"
        >
          <span className="brand-mark">
            L
          </span>

          <span className="brand-name">
            Learnix
          </span>
        </Link>

        {/* Mobile menu button */}
        <button
          type="button"
          className="menu-button"
          onClick={() =>
            setOpen((value) => !value)
          }
          aria-label={
            open
              ? "Close navigation"
              : "Open navigation"
          }
          aria-expanded={open}
          aria-controls="learnix-navigation"
        >
          <span />
          <span />
          <span />
        </button>

        {/* Navigation */}
        <nav
          id="learnix-navigation"
          className={`nav-links ${
            open ? "open" : ""
          }`}
        >
          <NavLink
            to="/"
            end
            onClick={closeMenu}
          >
            Home
          </NavLink>

          <NavLink
            to="/search"
            onClick={closeMenu}
          >
            Explore
          </NavLink>

          {user && (
            <>
              <NavLink
                to="/dashboard"
                onClick={closeMenu}
              >
                Dashboard
              </NavLink>

              <NavLink
                to="/learning-path"
                onClick={closeMenu}
              >
                Learning Path
              </NavLink>
            </>
          )}

          {/* Authentication */}
          <div className="nav-auth">

            {!loading && user ? (
              <>
                <ProfileMenu
                  user={user}
                  onNavigate={closeMenu}
                />

                <button
                  type="button"
                  className="nav-logout"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </>
            ) : (
              !loading && (
                <Link
                  to="/login"
                  className="nav-login"
                  onClick={closeMenu}
                >
                  Login
                </Link>
              )
            )}

          </div>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;

