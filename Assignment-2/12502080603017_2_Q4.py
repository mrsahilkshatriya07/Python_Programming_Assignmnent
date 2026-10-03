import sys
import mysql.connector
from mysql.connector import Error

# Whitelist definition mapping allowed user-facing aliases to actual SQL tables and columns
COLUMN_WHITELIST = {
    "student.id": ("Students", "student_id"),
    "student.name": ("Students", "name"),
    "student.spi": ("Students", "spi"),
    "course.id": ("Course", "course_id"),
    "course.name": ("Course", "course_name"),
    "registration.id": ("CourseRegistration", "registration_id")
}

# Whitelist allowed operators to prevent arbitrary SQL injection in condition logic
ALLOWED_OPERATORS = ["=", "!=", ">", "<", ">=", "<=", "LIKE"]


class SafeSQLQueryBuilder:
    def __init__(self):
        # Base schema relation joins
        self.base_from_clause = """
            FROM CourseRegistration cr
            JOIN Students student ON cr.student_id = student.student_id
            JOIN Course course ON cr.course_id = course.course_id
        """

    def resolve_column(self, col_identifier: str) -> str:
        """Validates and maps a user-supplied column alias to a safe table.column expression."""
        col_key = col_identifier.strip().lower()
        if col_key not in COLUMN_WHITELIST:
            raise ValueError(f"Security Violation / Invalid Column: '{col_identifier}' is not whitelisted.")
        
        table, col_name = COLUMN_WHITELIST[col_key]
        
        # Map back to query table aliases used in base FROM clause
        alias_map = {
            "Students": "student",
            "Course": "course",
            "CourseRegistration": "cr"
        }
        return f"{alias_map[table]}.{col_name}"

    def build_query(self, select_columns: list, filters: list, order_by_col: str = None, 
                    direction: str = "ASC", limit: int = 10) -> tuple:
        """
        Validates metadata and builds a parameterized SQL query along with its parameters.
        
        :param select_columns: List of column strings (e.g., ['student.name', 'course.name'])
        :param filters: List of tuples (col_name, operator, value)
        :param order_by_col: Column string for ORDER BY
        :param direction: 'ASC' or 'DESC'
        :param limit: Integer between 1 and 1000
        :return: (sql_string, params_list)
        """
        # 1. Validate and construct Projection (SELECT)
        if not select_columns:
            raise ValueError("Select columns list cannot be empty.")
        
        safe_select_cols = [self.resolve_column(col) for col in select_columns]
        select_clause = f"SELECT {', '.join(safe_select_cols)}"

        # 2. Validate and construct Filtering (WHERE)
        where_clauses = []
        query_params = []

        for col_name, op, val in filters:
            safe_col = self.resolve_column(col_name)
            op_clean = op.strip().upper()
            if op_clean not in ALLOWED_OPERATORS:
                raise ValueError(f"Security Violation: Invalid or unsafe operator '{op}'.")
            
            where_clauses.append(f"{safe_col} {op_clean} %s")
            query_params.append(val)

        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)

        # 3. Validate and construct Ordering (ORDER BY)
        order_clause = ""
        if order_by_col:
            safe_order_col = self.resolve_column(order_by_col)
            clean_direction = direction.strip().upper()
            if clean_direction not in ["ASC", "DESC"]:
                raise ValueError(f"Invalid sorting direction: '{direction}'. Must be ASC or DESC.")
            order_clause = f"ORDER BY {safe_order_col} {clean_direction}"

        # 4. Validate and construct Limit (LIMIT)
        if not isinstance(limit, int) or not (1 <= limit <= 1000):
            raise ValueError("LIMIT must be an integer between 1 and 1000.")
        limit_clause = f"LIMIT {limit}"

        # Combine SQL parts into final parameterized query
        sql_parts = [select_clause, self.base_from_clause, where_clause, order_clause, limit_clause]
        full_sql = " ".join([part.strip() for part in sql_parts if part.strip()])

        return full_sql, query_params


def execute_builder_demo(db_config, request_payload):
    """Parses input payload, builds validated SQL, and executes against MySQL database."""
    builder = SafeSQLQueryBuilder()

    try:
        # Extract inputs
        cols = request_payload.get("columns", [])
        raw_filters = request_payload.get("where", [])
        order_col = request_payload.get("order_by", None)
        direction = request_payload.get("direction", "ASC")
        limit = request_payload.get("limit", 10)

        # Build parameterized query
        sql, params = builder.build_query(
            select_columns=cols,
            filters=raw_filters,
            order_by_col=order_col,
            direction=direction,
            limit=limit
        )

        print("SQL_OK")

        # Execute query against database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # Display results
        for row in rows:
            print(" ".join(str(item) for item in row))

        cursor.close()
        connection.close()

    except ValueError as val_err:
        print(f"Validation / Security Error: {val_err}", file=sys.stderr)
    except Error as db_err:
        print(f"Database Execution Error: {db_err}", file=sys.stderr)


if __name__ == "__main__":
    # Example Database Credentials
    db_credentials = {
        'host': 'localhost',
        'database': 'university_db',
        'user': 'root',
        'password': 'your_password'
    }

    # Sample input specification matching the problem requirement
    sample_request = {
        "columns": ["student.name", "course.name"],
        "where": [("course.id", "=", "PY101")],
        "order_by": "student.spi",
        "direction": "DESC",
        "limit": 2
    }

    execute_builder_demo(db_credentials, sample_request)
