import { useState } from "react";

import {
  Link,
  NavLink,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

import ProfileMenu from "../ProfileMenu/ProfileMenu";

import "./Navbar.css";

function Navbar() {
  const [open, setOpen] =
    useState(false);

  const navigate = useNavigate();

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

    await logout();

    navigate("/", {
      replace: true,
    });
  };

  return (
    <header className="navbar">
      <div className="navbar-inner">

        <Link
          to="/"
          className="brand"
          onClick={closeMenu}
        >
          <span className="brand-mark">
            L
          </span>

          <span className="brand-name">
            Learnix
          </span>
        </Link>

        <button
          type="button"
          className="menu-button"
          onClick={() =>
            setOpen(
              (value) => !value
            )
          }
          aria-label={
            open
              ? "Close navigation"
              : "Open navigation"
          }
          aria-expanded={open}
        >
          <span />
          <span />
          <span />
        </button>

        <nav
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

          {!loading && user && (
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
                <>
                  <Link
                    to="/login"
                    className="nav-login"
                    onClick={closeMenu}
                  >
                    Login
                  </Link>

                  <Link
                    to="/register"
                    className="nav-register"
                    onClick={closeMenu}
                  >
                    Register
                  </Link>
                </>
              )
            )}

          </div>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;

