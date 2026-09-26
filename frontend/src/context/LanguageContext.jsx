import {
  createContext,
  useContext,
  useState,
} from "react";

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    return (
      localStorage.getItem("learnix_language") ||
      "en"
    );
  });

  const setLanguage = (value) => {
    setLanguageState(value);
    localStorage.setItem(
      "learnix_language",
      value
    );
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguageContext() {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error(
      "useLanguageContext must be used inside LanguageProvider"
    );
  }

  return context;
}