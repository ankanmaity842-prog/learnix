from app.ai.knowledge_graph import KnowledgeGraph


def test_add_topic():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="Machine Learning",
        prerequisites=[
            "Python",
            "Statistics",
        ],
        subtopics=[
            "Supervised Learning",
            "Unsupervised Learning",
        ],
        related_topics=[
            "Artificial Intelligence",
        ],
    )

    assert "Machine Learning" in graph.graph


def test_get_prerequisites():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="Neural Networks",
        prerequisites=[
            "Linear Algebra",
            "Gradient Descent",
        ],
    )

    prerequisites = graph.get_prerequisites(
        "Neural Networks"
    )

    assert "Linear Algebra" in prerequisites
    assert "Gradient Descent" in prerequisites


def test_get_subtopics():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="Python",
        subtopics=[
            "Variables",
            "Functions",
            "Classes",
        ],
    )

    subtopics = graph.get_subtopics(
        "Python"
    )

    assert "Variables" in subtopics
    assert "Functions" in subtopics
    assert "Classes" in subtopics


def test_get_related_topics():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="Python",
        related_topics=[
            "Programming",
            "Software Development",
        ],
    )

    related = graph.get_related_topics(
        "Python"
    )

    assert "Programming" in related
    assert "Software Development" in related


def test_learning_path():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="Machine Learning",
        prerequisites=[
            "Python",
            "Statistics",
        ],
    )

    graph.add_topic(
        topic="Python",
        prerequisites=[
            "Programming Basics",
        ],
    )

    path = graph.get_learning_path(
        "Machine Learning"
    )

    assert "Programming Basics" in path
    assert "Python" in path
    assert "Statistics" in path
    assert path[-1] == "Machine Learning"


def test_build_map():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="Machine Learning",
        prerequisites=[
            "Python",
        ],
    )

    result = graph.build_map(
        {
            "Python": 0.9,
            "Machine Learning": 0.5,
        }
    )

    assert "nodes" in result
    assert "edges" in result

    assert len(result["nodes"]) >= 2
    assert len(result["edges"]) >= 1


def test_empty_topic_is_ignored():
    graph = KnowledgeGraph()

    graph.add_topic(
        topic="   ",
        prerequisites=["Python"],
    )

    assert len(graph.graph) == 0