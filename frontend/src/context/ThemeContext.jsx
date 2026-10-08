import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

export const ThemeContext = createContext(null);

function getSystemTheme() {
  return window.matchMedia(
    "(prefers-color-scheme: dark)"
  ).matches
    ? "dark"
    : "light";
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => {
    return (
      localStorage.getItem("learnix_theme") ||
      "dark"
    );
  });

  const setTheme = (newTheme) => {
    if (
      !["dark", "light", "system"].includes(newTheme)
    ) {
      return;
    }

    setThemeState(newTheme);
  };

  const toggleTheme = () => {
    setThemeState((current) => {
      if (current === "dark") {
        return "light";
      }

      return "dark";
    });
  };

  useEffect(() => {
    const root = document.documentElement;

    root.classList.remove(
      "theme-dark",
      "theme-light"
    );

    const actualTheme =
      theme === "system"
        ? getSystemTheme()
        : theme;

    root.classList.add(
      `theme-${actualTheme}`
    );

    localStorage.setItem(
      "learnix_theme",
      theme
    );
  }, [theme]);

  useEffect(() => {
    if (theme !== "system") {
      return;
    }

    const mediaQuery = window.matchMedia(
      "(prefers-color-scheme: dark)"
    );

    const handleChange = () => {
      const root = document.documentElement;

      root.classList.remove(
        "theme-dark",
        "theme-light"
      );

      root.classList.add(
        `theme-${
          mediaQuery.matches
            ? "dark"
            : "light"
        }`
      );
    };

    mediaQuery.addEventListener(
      "change",
      handleChange
    );

    return () => {
      mediaQuery.removeEventListener(
        "change",
        handleChange
      );
    };
  }, [theme]);

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        toggleTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}



