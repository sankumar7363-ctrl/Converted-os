from core.task_engine.task_engine import TaskEngine


class FakeToolAgent:
    pass


print("\n=== TASK ENGINE TOOL AGENT TEST ===")

tool_agent = FakeToolAgent()

engine = TaskEngine(
    tool_agent=tool_agent
)

assert engine.tool_agent is tool_agent

print("[TEST] ToolAgent injected successfully")
print("[TEST] TaskEngine retained ToolAgent reference")

print("\n=== TASK ENGINE TOOL AGENT TEST PASSED ===")
