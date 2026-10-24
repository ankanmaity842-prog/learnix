
import api from "./api";

const LEVEL_LIMITS = {
  beginner: 30,
  intermediate: 25,
  advanced: 12,
};

const DEFAULT_LANGUAGE = "en";
const DEFAULT_LEVEL = "beginner";

function buildParams(params = {}) {
  const level = LEVEL_LIMITS[params.level]
    ? params.level
    : DEFAULT_LEVEL;

  return {
    language: params.language || DEFAULT_LANGUAGE,
    level,
    limit: params.limit ?? LEVEL_LIMITS[level],
    ...params,
    // Keep the validated defaults when callers omit these fields.
    language: params.language || DEFAULT_LANGUAGE,
    level,
    limit: params.limit ?? LEVEL_LIMITS[level],
  };
}

const recommendationService = {
  async getForTopic(topic, params = {}) {
    const response = await api.get(
      `/recommendations/for-topic/${encodeURIComponent(topic)}`,
      {
        params: buildParams(params),
      }
    );

    return response.data;
  },

  async getRecommendations(params = {}) {
    const requestParams = buildParams(params);

    const response = await api.post("/recommendations/", {
      topic: params.topic,
      language: requestParams.language,
      level: requestParams.level,
      limit: requestParams.limit,
    });

    return response.data;
  },

  async getChannels(query, params = {}) {
    const response = await api.get("/recommendations/channels", {
      params: {
        query,
        language: params.language || DEFAULT_LANGUAGE,
      },
    });

    return response.data;
  },

  async getForChannel(channelId, topic, params = {}) {
    const response = await api.get(
      `/recommendations/channel/${encodeURIComponent(channelId)}`,
      {
        params: {
          topic,
          ...buildParams(params),
        },
      }
    );

    return response.data;
  },
};

export default recommendationService;
