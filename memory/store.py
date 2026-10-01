import sqlite3
from datetime import datetime
from uuid import uuid4


class MemoryStore:

    STOP_WORDS = {
        "a",
        "an",
        "the",
        "to",
        "of",
        "for",
        "and",
        "or",
        "in",
        "on",
        "with",
        "create",
        "make",
        "build",
        "task",
        "goal",
        "result",
        "success",
        "true",
        "false",
    }

    def __init__(
        self,
        database_path: str = "memory/memory.db"
    ):
        self.database_path = database_path
        self._create_table()

    def _connect(self):
        return sqlite3.connect(
            self.database_path
        )

    def _create_table(self):

        with self._connect() as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def remember(
        self,
        memory_type: str,
        content: str
    ):

        with self._connect() as connection:

            existing = connection.execute(
                """
                SELECT id
                FROM memories
                WHERE type = ?
                AND content = ?
                LIMIT 1
                """,
                (
                    memory_type,
                    content,
                ),
            ).fetchone()

            if existing:

                print(
                    "[MEMORY] Duplicate memory skipped"
                )

                return {
                    "id": existing[0],
                    "type": memory_type,
                    "content": content,
                    "duplicate": True,
                }

        memory = {
            "id": str(uuid4()),
            "type": memory_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
        }

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO memories
                (id, type, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    memory["id"],
                    memory["type"],
                    memory["content"],
                    memory["created_at"],
                ),
            )

        return memory

    def get_all(self):

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT id, type, content, created_at
                FROM memories
                ORDER BY created_at ASC
                """
            ).fetchall()

        return [
            {
                "id": row[0],
                "type": row[1],
                "content": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    def _meaningful_words(self, text: str):

        words = set()

        for word in text.lower().split():

            word = word.strip(
                ".,!?()[]{}:;|"
            )

            if (
                len(word) > 2
                and word not in self.STOP_WORDS
            ):
                words.add(word)

        return words

    def search(
        self,
        query: str,
        limit: int = 5
    ):

        query_words = self._meaningful_words(
            query
        )

        if not query_words:
            return []

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT id, type, content, created_at
                FROM memories
                """
            ).fetchall()

        scored_results = []

        for row in rows:

            content_words = self._meaningful_words(
                row[2]
            )

            matches = query_words.intersection(
                content_words
            )

            if not matches:
                continue

            score = len(matches)

            # Give a small bonus when all
            # meaningful query words match.
            if matches == query_words:
                score += 3

            scored_results.append(
                (
                    score,
                    {
                        "id": row[0],
                        "type": row[1],
                        "content": row[2],
                        "created_at": row[3],
                    }
                )
            )

        scored_results.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            result
            for _, result in scored_results[:limit]
        ]

    def remember_experience(
        self,
        goal: str,
        success: bool,
        summary: str,
        status: str = "completed",
    ):
        content = (
            f"Goal: {goal} | "
            f"Status: {status} | "
            f"Success: {success} | "
            f"Result: {summary}"
        )

        return self.remember(
            "experience",
            content
        )
