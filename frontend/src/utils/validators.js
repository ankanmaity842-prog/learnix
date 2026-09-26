export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    email.trim()
  );
}

export function isValidUsername(username) {
  return /^[a-zA-Z0-9_]{5,30}$/.test(
    username.trim()
  );
}

export function isValidPassword(password) {
  return typeof password === "string"
    && password.length >= 6;
}

export function passwordsMatch(
  password,
  confirmPassword
) {
  return password === confirmPassword;
}