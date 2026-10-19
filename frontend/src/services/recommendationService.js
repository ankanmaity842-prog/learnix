import api from "./api";

const LEVEL_LIMITS = {
  beginner: 30,
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
          limit: LEVEL_LIMITS[level] || 30,
          ...params,
        },
      }
    );

    return response.data;
  },

  async getRecommendations(params = {}) {
    const level = params.level || "beginner";

    const response = await api.post("/recommendations/", {
      topic: params.topic,
      language: params.language || "en",
      level,
      limit: params.limit ?? LEVEL_LIMITS[level] ?? 30,
    });

    return response.data;
  },

  async getChannels(query, params = {}) {
    const response = await api.get("/recommendations/channels", {
      params: {
        query,
        language: "en",
        ...params,
      },
    });

    return response.data;
  },

  async getForChannel(channelId, topic, params = {}) {
    const level = params.level || "beginner";

    const response = await api.get(
      `/recommendations/channel/${encodeURIComponent(channelId)}`,
      {
        params: {
          topic,
          language: "en",
          level,
          limit: LEVEL_LIMITS[level] || 30,
          ...params,
        },
      }
    );

    return response.data;
  },
};

export default recommendationService;