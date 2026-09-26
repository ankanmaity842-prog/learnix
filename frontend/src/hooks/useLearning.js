import { useCallback, useState } from "react";
import learningService from "../services/learningService";

export function useLearning() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startLearning = useCallback(async (data) => {
    setLoading(true);
    setError(null);

    try {
      return await learningService.startSession(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to start learning session."
      );

      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProgress = useCallback(async (id, data) => {
    setLoading(true);
    setError(null);

    try {
      return await learningService.updateProgress(
        id,
        data
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to update progress."
      );

      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    startLearning,
    updateProgress,
  };
}