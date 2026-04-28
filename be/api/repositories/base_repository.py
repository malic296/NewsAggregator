from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from typing import Optional
from api.models import DBResult
from api.core.errors import DatabaseError

class BaseRepository:
    def __init__(self, connection_pool: ConnectionPool):
        self._pool = connection_pool
        self.PAGE_SIZE = 10

    def _execute(self, query: str, params: Optional[tuple] = None) -> DBResult:
        try:
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params or ())
                    data = []

                    if cur.description is not None:
                        data = cur.fetchall()

                    count = cur.rowcount
                    return DBResult(
                        success=True,
                        data=data,
                        row_count=count
                    )

        except Exception as e:
            return DBResult(
                success = False,
                error_message=str(e)
            )

    def _execute_transaction(self, inputs: list[tuple[str, Optional[tuple]]]) -> DBResult:
        try:
            row_count = 0
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    for input in inputs:
                        cur.execute(input[0], input[1] or ())

                        if cur.description is not None:
                            raise DatabaseError(message="This method is used only for update queries.", method="_execute_transaction")

                        row_count += cur.rowcount

            return DBResult(
                success=True,
                data=None,
                row_count=row_count
            )

        except Exception as e:
            return DBResult(
                success = False,
                error_message=str(e)
            )

    def _execute_transaction_returning(self, inputs: list[tuple[str, Optional[tuple]]]) -> DBResult:
        try:
            all_rows = []
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    for input in inputs:
                        cur.execute(input[0], input[1] or ())
                        if cur.description:
                            rows = cur.fetchall()
                            all_rows.extend(rows)

            return DBResult(
                success=True,
                data=all_rows,
                row_count=len(all_rows)
            )

        except Exception as e:
            return DBResult(
                success = False,
                error_message=str(e)
            )