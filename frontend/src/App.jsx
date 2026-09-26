import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar/Navbar";
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";

import Home from "./pages/Home/Home";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Search from "./pages/Search/Search";

import Dashboard from "./pages/Dashboard/Dashboard";
import VideoLearning from "./pages/VideoLearning/VideoLearning";
import Notes from "./pages/Notes/Notes";
import QuizPage from "./pages/QuizPage/QuizPage";
import LearningPathPage from "./pages/LearningPathPage/LearningPathPage";
import KnowledgePage from "./pages/KnowledgePage/KnowledgePage";

import Profile from "./pages/Profile/Profile";
import Settings from "./pages/Settings/Settings";

import ForgotPassword from "./pages/ForgotPassword/ForgotPassword";
import ResetPassword from "./pages/ResetPassword/ResetPassword";

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        {/* Public routes */}

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/search"
          element={<Search />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        <Route
          path="/reset-password"
          element={<ResetPassword />}
        />

        {/* Protected routes */}

        <Route element={<ProtectedRoute />}>
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/video/:videoId"
            element={<VideoLearning />}
          />

          <Route
            path="/notes"
            element={<Notes />}
          />

          <Route
            path="/quiz/:quizId"
            element={<QuizPage />}
          />

          <Route
            path="/learning-path"
            element={<LearningPathPage />}
          />

          <Route
            path="/knowledge"
            element={<KnowledgePage />}
          />

          <Route
            path="/profile"
            element={<Profile />}
          />

          <Route
            path="/settings"
            element={<Settings />}
          />
        </Route>
      </Routes>
    </>
  );
}

export default App;