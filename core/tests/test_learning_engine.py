from core.learning.learning_engine import LearningEngine
from core.models.experience import OutcomeStatus


def test_successful_experience():
    engine = LearningEngine()

    results = [
        {
            "step_index": 0,
            "tool": "create_file",
            "status": "success",
            "success": True,
            "result": "Created index.html",
        },
        {
            "step_index": 1,
            "tool": "create_file",
            "status": "success",
            "success": True,
            "result": "Created style.css",
        },
    ]

    experience = engine.create_experience(
        goal="Create a web page",
        results=results,
    )

    assert experience.goal == "Create a web page"
    assert experience.outcome == OutcomeStatus.SUCCESS
    assert len(experience.steps) == 2
    assert experience.steps[0].tool_name == "create_file"
    assert experience.steps[0].success is True
    assert experience.learning_signal is not None
    assert experience.learning_signal.useful is True


def test_failed_experience():
    engine = LearningEngine()

    results = [
        {
            "step_index": 0,
            "tool": "create_file",
            "status": "success",
            "success": True,
        },
        {
            "step_index": 1,
            "tool": "missing_tool",
            "status": "failure",
            "success": False,
            "error": "Tool not found",
        },
    ]

    experience = engine.create_experience(
        goal="Create a web page",
        results=results,
        recovery_used=True,
    )

    assert experience.outcome == OutcomeStatus.PARTIAL
    assert experience.recovery_used is True
    assert len(experience.steps) == 2
    assert experience.steps[1].success is False
    assert experience.steps[1].error == "Tool not found"
    assert experience.learning_signal is not None
    assert experience.learning_signal.improvement is not None


def test_empty_results_are_failure():
    engine = LearningEngine()

    experience = engine.create_experience(
        goal="Create a web page",
        results=[],
    )

    assert experience.outcome == OutcomeStatus.FAILURE
    assert experience.steps == []
    assert experience.learning_signal is not None
    assert experience.learning_signal.useful is False

def test_store_experience(tmp_path):
    from memory.store import MemoryStore

    database_path = tmp_path / "learning_test.db"

    memory = MemoryStore(str(database_path))
    engine = LearningEngine(memory=memory)

    experience = engine.create_experience(
        goal="Create a web page",
        results=[
            {
                "step_index": 0,
                "tool": "create_file",
                "status": "success",
                "success": True,
            }
        ],
    )

    stored = engine.store_experience(experience)

    assert stored["type"] == "experience"
    assert "Create a web page" in stored["content"]
    assert "success" in stored["content"].lower()

    memories = memory.get_all()

    assert len(memories) == 1
    assert memories[0]["type"] == "experience"
    assert "Create a web page" in memories[0]["content"]

def test_find_relevant_experiences(tmp_path):
    from memory.store import MemoryStore

    database_path = tmp_path / "retrieval_test.db"

    memory = MemoryStore(str(database_path))
    engine = LearningEngine(memory=memory)

    experience = engine.create_experience(
        goal="Create a web page",
        results=[
            {
                "step_index": 0,
                "tool": "create_file",
                "status": "success",
                "success": True,
            }
        ],
    )

    engine.store_experience(experience)

    results = engine.find_relevant_experiences(
        goal="Create a web page"
    )

    assert len(results) == 1
    assert results[0]["type"] == "experience"
    assert "Create a web page" in results[0]["content"]
