import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import Loading from "../../components/Loading/Loading";
import ErrorMessage from "../../components/ErrorMessage/ErrorMessage";
import "./Profile.css";

function getInitials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);

  if (!parts.length) return "?";

  if (parts.length === 1) {
    return parts[0][0].toUpperCase();
  }

  return (
    parts[0][0] +
    parts[parts.length - 1][0]
  ).toUpperCase();
}

function Profile() {
  const { user, loading } = useAuth();

  if (loading) {
    return <Loading fullScreen message="Loading profile..." />;
  }

  if (!user) {
    return (
      <ErrorMessage message="Unable to load your profile." />
    );
  }

  const initials = getInitials(user.name);

  return (
    <main className="profile-page">

      <section className="profile-container">

        <div className="profile-hero">

          <div className="profile-page-avatar">
            {initials}
          </div>

          <div className="profile-identity">
            <h1>{user.name}</h1>

            {user.username && (
              <p>@{user.username}</p>
            )}

            <span>{user.email}</span>
          </div>

          <Link
            to="/settings"
            className="profile-edit-button"
          >
            Settings
          </Link>

        </div>

        <section className="profile-stats">

          <div className="profile-stat">
            <strong>{user.learning_sessions_count ?? 0}</strong>
            <span>Learning Sessions</span>
          </div>

          <div className="profile-stat">
            <strong>{user.completed_videos ?? 0}</strong>
            <span>Videos Completed</span>
          </div>

          <div className="profile-stat">
            <strong>{user.topics_learned ?? 0}</strong>
            <span>Topics Learned</span>
          </div>

          <div className="profile-stat">
            <strong>{user.learning_streak ?? 0}</strong>
            <span>Day Streak</span>
          </div>

        </section>

        <section className="profile-section">

          <div className="profile-section-header">
            <div>
              <h2>Your Learning</h2>
              <p>
                Continue learning and track your progress.
              </p>
            </div>

            <Link to="/dashboard">
              View dashboard
            </Link>
          </div>

          <div className="profile-feature-grid">

            <Link
              to="/dashboard"
              className="profile-feature-card"
            >
              <span className="feature-icon">▣</span>
              <h3>My Learning</h3>
              <p>
                View your active learning sessions.
              </p>
            </Link>

            <Link
              to="/dashboard"
              className="profile-feature-card"
            >
              <span className="feature-icon">◫</span>
              <h3>Progress</h3>
              <p>
                Track your learning performance.
              </p>
            </Link>

            <Link
              to="/knowledge"
              className="profile-feature-card"
            >
              <span className="feature-icon">◇</span>
              <h3>Knowledge & Skills</h3>
              <p>
                See your strengths and knowledge gaps.
              </p>
            </Link>

            <Link
              to="/learning-path"
              className="profile-feature-card"
            >
              <span className="feature-icon">↗</span>
              <h3>Learning Path</h3>
              <p>
                Follow your personalized learning journey.
              </p>
            </Link>

          </div>

        </section>

      </section>

    </main>
  );
}

export default Profile;