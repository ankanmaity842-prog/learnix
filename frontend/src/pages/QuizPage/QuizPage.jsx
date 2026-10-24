
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import "./QuizPage.css";

function QuizPage() {
  const location = useLocation();

  const quiz = location.state?.quiz;
  const videoTitle = location.state?.videoTitle || quiz?.topic;

  const questions = quiz?.questions || [];

  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState({});
  const [finished, setFinished] = useState(false);

  if (!questions.length) {
    return (
      <main className="quiz-page">
        <section className="quiz-card">
          <h1>No quiz loaded</h1>
          <p>
            Generate a quiz from a video first. If you refreshed
            this page, its temporary quiz data may have been lost.
          </p>
          <Link to="/search">Return to search</Link>
        </section>
      </main>
    );
  }

  const question = questions[current];
  const selected = answers[current];

  const correctAnswer = (item) =>
    String(item.correct_answer || "").toUpperCase();

  const score = questions.reduce((total, item, index) => {
    const selectedOption = answers[index];
    const expected = correctAnswer(item);

    const selectedLetter =
      typeof selectedOption === "number"
        ? String.fromCharCode(65 + selectedOption)
        : selectedOption;

    return total + (selectedLetter === expected ? 1 : 0);
  }, 0);

  const progress = finished
    ? 100
    : ((current + 1) / questions.length) * 100;

  const handleNext = () => {
    if (selected === undefined) return;

    if (current === questions.length - 1) {
      setFinished(true);
    } else {
      setCurrent((previous) => previous + 1);
    }
  };

  const restart = () => {
    setCurrent(0);
    setAnswers({});
    setFinished(false);
  };

  return (
    <main className="quiz-page">
      <section className="quiz-header">
        <span>VIDEO KNOWLEDGE CHECK</span>
        <h1>{finished ? "Quiz completed" : "Test your understanding"}</h1>
        <p>{videoTitle}</p>

        <div className="quiz-progress">
          <div>
            <span>
              {finished
                ? "Completed"
                : `Question ${current + 1} of ${questions.length}`}
            </span>
            <strong>{Math.round(progress)}%</strong>
          </div>

          <div className="quiz-progress-bar">
            <span style={{ width: `${progress}%` }} />
          </div>
        </div>
      </section>

      <section className="quiz-card">
        {finished ? (
          <>
            <span className="question-label">YOUR RESULT</span>
            <h2>
              You scored {score} out of {questions.length}
            </h2>
            <p>
              {score === questions.length
                ? "Excellent work! You answered every question correctly."
                : "Review the explanations below to revisit concepts from the lesson."}
            </p>

            <div className="quiz-review">
              {questions.map((item, index) => {
                const selectedOption = answers[index];
                const selectedLetter =
                  typeof selectedOption === "number"
                    ? String.fromCharCode(65 + selectedOption)
                    : selectedOption;

                const isCorrect =
                  selectedLetter === correctAnswer(item);

                return (
                  <article key={item.id ?? index}>
                    <h3>{index + 1}. {item.question}</h3>
                    <p>
                      Your answer:{" "}
                      {selectedOption === undefined
                        ? "Not answered"
                        : item.options[
                            typeof selectedOption === "number"
                              ? selectedOption
                              : selectedOption.charCodeAt(0) - 65
                          ]}
                    </p>
                    <p>
                      Correct answer:{" "}
                      {item.options[
                        correctAnswer(item).charCodeAt(0) - 65
                      ]}
                    </p>
                    <p>{item.explanation}</p>
                    <strong>
                      {isCorrect ? "Correct" : "Review this concept"}
                    </strong>
                  </article>
                );
              })}
            </div>

            <div className="quiz-footer">
              <button
                type="button"
                className="primary-button"
                onClick={restart}
              >
                Try again
              </button>
              <Link to="/search">Find another lesson</Link>
            </div>
          </>
        ) : (
          <>
            <span className="question-label">
              QUESTION {String(current + 1).padStart(2, "0")}
            </span>

            <h2>{question.question}</h2>

            <div className="quiz-options">
              {question.options.map((option, index) => (
                <button
                  key={`${index}-${option}`}
                  type="button"
                  className={selected === index ? "selected" : ""}
                  aria-pressed={selected === index}
                  onClick={() =>
                    setAnswers((previous) => ({
                      ...previous,
                      [current]: index,
                    }))
                  }
                >
                  <span>{String.fromCharCode(65 + index)}</span>
                  {option}
                </button>
              ))}
            </div>

            <div className="quiz-footer">
              <span>Select the best answer</span>

              <button
                type="button"
                className="primary-button"
                disabled={selected === undefined}
                onClick={handleNext}
              >
                {current === questions.length - 1
                  ? "Finish quiz"
                  : "Next question"}
              </button>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

export default QuizPage;

