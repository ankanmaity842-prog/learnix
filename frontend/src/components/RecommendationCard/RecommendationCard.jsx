import DifficultyBadge from "../DifficultyBadge/DifficultyBadge";
import "./RecommendationCard.css";

function RecommendationCard({
  recommendation,
}) {
  return (
    <article className="recommendation-card">
      <div>
        <span className="recommendation-label">
          Recommended for you
        </span>

        <h3>{recommendation.title}</h3>

        <p>
          {recommendation.reason ||
            "Matches your learning preferences and current level."}
        </p>
      </div>

      <div className="recommendation-score">
        <strong>
          {Math.round(
            recommendation.final_score * 100
          )}
          %
        </strong>

        <span>match</span>
      </div>

      <DifficultyBadge
        level={
          recommendation.difficulty ||
          "beginner"
        }
      />
    </article>
  );
}

export default RecommendationCard;