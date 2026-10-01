from core.executor.tool_catalog import ToolCatalog
from core.executor.tool_definition import ToolDefinition


class ToolSelector:

    STOP_WORDS = {
        "a",
        "an",
        "the",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "and",
        "or",
        "is",
        "are",
        "new",
        "my",
        "this",
        "that",
    }

    ACTION_WORDS = {
        "create",
        "read",
        "write",
        "open",
        "close",
        "delete",
        "remove",
        "update",
        "modify",
        "execute",
        "run",
        "install",
        "download",
        "upload",
        "search",
        "find",
        "list",
    }

    def __init__(
        self,
        catalog: ToolCatalog,
    ):

        self.catalog = catalog

    def _words(
        self,
        text: str,
    ) -> set[str]:

        return {
            word
            for word in (
                text.lower()
                .replace(",", " ")
                .replace(".", " ")
                .replace("-", " ")
                .replace("_", " ")
                .split()
            )
            if word not in self.STOP_WORDS
        }

    def _score(
        self,
        goal_words: set[str],
        tool: ToolDefinition,
    ) -> int:

        name_words = self._words(tool.name)
        description_words = self._words(
            tool.description
        )

        goal_actions = (
            goal_words.intersection(
                self.ACTION_WORDS
            )
        )

        tool_actions = (
            name_words.intersection(
                self.ACTION_WORDS
            )
        )

        # If both the goal and tool have an
        # action word, they must agree.
        if goal_actions and tool_actions:

            if not goal_actions.intersection(
                tool_actions
            ):
                return 0

        name_matches = goal_words.intersection(
            name_words
        )

        description_matches = (
            goal_words.intersection(
                description_words
            )
        )

        return (
            len(name_matches) * 3
            + len(description_matches)
        )

    def select(
        self,
        goal: str,
    ) -> list[ToolDefinition]:

        goal_words = self._words(goal)

        scored_tools = []

        for tool in self.catalog.describe_tools():

            score = self._score(
                goal_words,
                tool,
            )

            if score <= 0:
                continue

            scored_tools.append(
                (score, tool)
            )

        scored_tools.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            tool
            for score, tool in scored_tools
        ]
