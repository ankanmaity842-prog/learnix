import "./NotesViewer.css";

function NotesViewer({
  title = "Learning Notes",
  content = "",
}) {
  const downloadNotes = () => {
    const blob = new Blob(
      [content],
      { type: "text/plain" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `${title}.txt`;
    link.click();

    URL.revokeObjectURL(url);
  };

  return (
    <section className="notes-viewer">
      <div className="notes-header">
        <div>
          <span>Generated notes</span>
          <h2>{title}</h2>
        </div>

        <button onClick={downloadNotes}>
          Download
        </button>
      </div>

      <div className="notes-content">
        {content || "No notes generated yet."}
      </div>
    </section>
  );
}

export default NotesViewer;