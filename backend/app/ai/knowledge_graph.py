from collections import defaultdict


class KnowledgeGraph:

    def __init__(self):
        self.graph = defaultdict(set)
        self.relationships = defaultdict(set)

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship: str = "prerequisite",
    ) -> None:

        source = source.strip()
        target = target.strip()

        if not source or not target:
            return

        self.graph[target].add(source)

        self.relationships[
            relationship
        ].add(
            (
                source,
                target,
            )
        )

    def add_topic(
        self,
        topic: str,
        prerequisites: list[str] | None = None,
        subtopics: list[str] | None = None,
        related_topics: list[str] | None = None,
    ) -> None:

        topic = topic.strip()

        if not topic:
            return

        self.graph.setdefault(
            topic,
            set(),
        )

        for prerequisite in prerequisites or []:
            self.add_relationship(
                source=prerequisite,
                target=topic,
                relationship="prerequisite",
            )

        for subtopic in subtopics or []:
            self.add_relationship(
                source=topic,
                target=subtopic,
                relationship="contains",
            )

        for related_topic in related_topics or []:
            self.add_relationship(
                source=topic,
                target=related_topic,
                relationship="related",
            )

    def get_prerequisites(
        self,
        topic: str,
    ) -> list[str]:

        return sorted(
            self.graph.get(
                topic,
                set(),
            )
        )

    def get_related_topics(
        self,
        topic: str,
    ) -> list[str]:

        relationships = self.relationships.get(
            "related",
            set(),
        )

        related = []

        for source, target in relationships:

            if source == topic:
                related.append(target)

            elif target == topic:
                related.append(source)

        return sorted(
            set(related)
        )

    def get_subtopics(
        self,
        topic: str,
    ) -> list[str]:

        relationships = self.relationships.get(
            "contains",
            set(),
        )

        return sorted(
            {
                target
                for source, target in relationships
                if source == topic
            }
        )

    def build_map(
        self,
        knowledge: dict[str, float],
    ) -> dict:

        nodes = {}
        edges = []

        for topic, score in knowledge.items():

            nodes[topic] = {
                "id": topic,
                "label": topic,
                "score": float(score),
            }

        for relationship, relations in self.relationships.items():

            for source, target in relations:

                if source not in nodes:
                    nodes[source] = {
                        "id": source,
                        "label": source,
                        "score": 0.0,
                    }

                if target not in nodes:
                    nodes[target] = {
                        "id": target,
                        "label": target,
                        "score": 0.0,
                    }

                edges.append(
                    {
                        "source": source,
                        "target": target,
                        "relationship": relationship,
                    }
                )

        return {
            "nodes": list(
                nodes.values()
            ),
            "edges": edges,
        }

    def get_learning_path(
        self,
        topic: str,
    ) -> list[str]:

        visited = set()
        path = []

        def visit(current: str):

            if current in visited:
                return

            visited.add(current)

            for prerequisite in sorted(
                self.graph.get(
                    current,
                    set(),
                )
            ):
                visit(prerequisite)

            path.append(current)

        visit(topic)

        return path


knowledge_graph = KnowledgeGraph()