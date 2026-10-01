import sqlite3

from enum import Enum
from pydantic import BaseModel


class LocalLLMStatus(str, Enum):

    REGISTERED = "registered"
    INSTALLED = "installed"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


class LocalLLM(BaseModel):

    name: str
    runtime: str
    endpoint: str
    model_id: str

    status: LocalLLMStatus = (
        LocalLLMStatus.REGISTERED
    )

    default: bool = False


class LocalLLMRegistry:

    def __init__(
        self,
        database_path: str = "memory/local_llm.db"
    ):

        self.database_path = database_path

        self._create_table()
        self._upgrade_table()

    def _connect(self):

        return sqlite3.connect(
            self.database_path
        )

    def _create_table(self):

        with self._connect() as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS local_llms (
                    model_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    runtime TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    status TEXT NOT NULL
                        DEFAULT 'registered',
                    is_default INTEGER NOT NULL
                        DEFAULT 0
                )
            """)

    def _upgrade_table(self):

        with self._connect() as connection:

            columns = connection.execute(
                """
                PRAGMA table_info(local_llms)
                """
            ).fetchall()

            column_names = {
                column[1]
                for column in columns
            }

            # Old versions of Converted OS used an
            # "enabled" column. Rebuild the table without it.
            if "enabled" in column_names:

                connection.execute(
                    """
                    ALTER TABLE local_llms
                    RENAME TO local_llms_old
                    """
                )

                connection.execute("""
                    CREATE TABLE local_llms (
                        model_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        runtime TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        status TEXT NOT NULL
                            DEFAULT 'registered',
                        is_default INTEGER NOT NULL
                            DEFAULT 0
                    )
                """)

                connection.execute("""
                    INSERT INTO local_llms
                    (
                        model_id,
                        name,
                        runtime,
                        endpoint,
                        status,
                        is_default
                    )
                    SELECT
                        model_id,
                        name,
                        runtime,
                        endpoint,
                        CASE
                            WHEN status IS NOT NULL
                            THEN status
                            ELSE 'registered'
                        END,
                        is_default
                    FROM local_llms_old
                """)

                connection.execute(
                    """
                    DROP TABLE local_llms_old
                    """
                )

            # Add status if an older database does not have it.
            columns = connection.execute(
                """
                PRAGMA table_info(local_llms)
                """
            ).fetchall()

            column_names = {
                column[1]
                for column in columns
            }

            if "status" not in column_names:

                connection.execute(
                    """
                    ALTER TABLE local_llms
                    ADD COLUMN status TEXT
                    DEFAULT 'registered'
                    """
                )

    def add_model(
        self,
        name: str,
        runtime: str,
        endpoint: str,
        model_id: str,
        default: bool = False,
        status: LocalLLMStatus = (
            LocalLLMStatus.REGISTERED
        ),
    ) -> LocalLLM:

        if default:
            self.clear_default()

        with self._connect() as connection:

            connection.execute(
                """
                INSERT OR REPLACE INTO local_llms
                (
                    model_id,
                    name,
                    runtime,
                    endpoint,
                    status,
                    is_default
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    model_id,
                    name,
                    runtime,
                    endpoint,
                    status.value,
                    int(default),
                ),
            )

        return LocalLLM(
            name=name,
            runtime=runtime,
            endpoint=endpoint,
            model_id=model_id,
            status=status,
            default=default,
        )

    def remove_model(
        self,
        model_id: str
    ) -> bool:

        with self._connect() as connection:

            cursor = connection.execute(
                """
                DELETE FROM local_llms
                WHERE model_id = ?
                """,
                (model_id,),
            )

        return cursor.rowcount > 0

    def get_model(
        self,
        model_id: str
    ) -> LocalLLM | None:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    name,
                    runtime,
                    endpoint,
                    model_id,
                    status,
                    is_default
                FROM local_llms
                WHERE model_id = ?
                """,
                (model_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_model(row)

    def get_default(self) -> LocalLLM | None:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    name,
                    runtime,
                    endpoint,
                    model_id,
                    status,
                    is_default
                FROM local_llms
                WHERE is_default = 1
                AND status = 'installed'
                LIMIT 1
                """
            ).fetchone()

        if row is None:
            return None

        return self._row_to_model(row)

    def set_default(
        self,
        model_id: str
    ) -> bool:

        model = self.get_model(model_id)

        if model is None:
            return False

        if model.status != LocalLLMStatus.INSTALLED:

            print(
                "[LOCAL AI] Cannot set default: "
                "model is not installed"
            )

            return False

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE local_llms
                SET is_default = 0
                """
            )

            connection.execute(
                """
                UPDATE local_llms
                SET is_default = 1
                WHERE model_id = ?
                """,
                (model_id,),
            )

        return True

    def set_status(
        self,
        model_id: str,
        status: LocalLLMStatus
    ) -> bool:

        model = self.get_model(model_id)

        if model is None:
            return False

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE local_llms
                SET status = ?
                WHERE model_id = ?
                """,
                (
                    status.value,
                    model_id,
                ),
            )

            if status != LocalLLMStatus.INSTALLED:

                connection.execute(
                    """
                    UPDATE local_llms
                    SET is_default = 0
                    WHERE model_id = ?
                    """,
                    (model_id,),
                )

        return True

    def clear_default(self):

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE local_llms
                SET is_default = 0
                """
            )

    def list_models(self) -> list[LocalLLM]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    name,
                    runtime,
                    endpoint,
                    model_id,
                    status,
                    is_default
                FROM local_llms
                ORDER BY name
                """
            ).fetchall()

        return [
            self._row_to_model(row)
            for row in rows
        ]

    def _row_to_model(
        self,
        row
    ) -> LocalLLM:

        return LocalLLM(
            name=row[0],
            runtime=row[1],
            endpoint=row[2],
            model_id=row[3],
            status=LocalLLMStatus(row[4]),
            default=bool(row[5]),
        )
