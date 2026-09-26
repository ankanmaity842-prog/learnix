import "./KnowledgeMap.css";

function KnowledgeMap({
  nodes = [],
}) {
  return (
    <section className="knowledge-map">
      <div>
        <span>Learning intelligence</span>
        <h3>Knowledge map</h3>
      </div>

      <div className="knowledge-nodes">
        {nodes.map((node) => (
          <div
            className="knowledge-node"
            key={node.id}
          >
            <strong>{node.label}</strong>

            <div className="node-progress">
              <span
                style={{
                  width: `${node.score * 100}%`,
                }}
              />
            </div>

            <small>
              {Math.round(node.score * 100)}%
            </small>
          </div>
        ))}
      </div>
    </section>
  );
}

export default KnowledgeMap;