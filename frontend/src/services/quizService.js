
import api from "./api";

const quizService = {
  async generateForVideo(video, videoId, options = {}) {
    const response = await api.post("/quiz/generate", {
      video_id: videoId,
      topic: video?.title || "Video lesson",
      content: options.content || "",
      language: options.language || video?.language || "en",
      number_of_questions: options.numberOfQuestions || 10,
      difficulty: options.difficulty || "medium",
    });

    return response.data;
  },
};

export default quizService;
