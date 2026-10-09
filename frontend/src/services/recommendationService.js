import api from "./api";

const LEVEL_LIMITS = {
  beginner: 45,
  intermediate: 25,
  advanced: 12,
};

const recommendationService = {
  async getForTopic(topic, params = {}) {
    const level = params.level || "beginner";

    const response = await api.get(
      `/recommendations/for-topic/${encodeURIComponent(topic)}`,
      {
        params: {
          language: "en",
          level,
          limit: LEVEL_LIMITS[level] || 45,
          ...params,
        },
      }
    );

    return response.data;
  },

  async getRecommendations(params = {}) {
    const level = params.level || "beginner";

    const response = await api.get(
      "/recommendations",
      {
        params: {
          language: "en",
          level,
          limit: LEVEL_LIMITS[level] || 45,
          ...params,
        },
      }
    );

    return response.data;
  },

  async getChannels(query, params = {}) {
    const response = await api.get(
      "/recommendations/channels",
      {
        params: {
          query,
          language: "en",
          ...params,
        },
      }
    );

    return response.data;
  },
};

export default recommendationService;