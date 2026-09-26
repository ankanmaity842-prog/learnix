export function formatDuration(seconds) {
  if (!Number.isFinite(seconds)) {
    return "0:00";
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  return `${minutes}:${String(
    remainingSeconds
  ).padStart(2, "0")}`;
}

export function formatNumber(value) {
  return new Intl.NumberFormat().format(
    Number(value) || 0
  );
}

export function formatPercentage(value) {
  return `${Math.round(
    Number(value) * 100
  )}%`;
}