import csv
import sys
import mysql.connector
from mysql.connector import Error

BATCH_SIZE = 5000  # Process records in chunks to satisfy O(batch_size) memory space complexity


def setup_database_schema(cursor):
    """
    Creates necessary tables and indexes if they do not exist.
    Adds composite index to support O(log N) filtering on course_id and SPI.
    """
    create_students_table = """
    CREATE TABLE IF NOT EXISTS Students (
        student_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        spi DECIMAL(3, 2) NOT NULL,
        INDEX idx_spi (spi)
    );
    """

    create_registrations_table = """
    CREATE TABLE IF NOT EXISTS CourseRegistration (
        registration_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(50) NOT NULL,
        course_id VARCHAR(50) NOT NULL,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
        INDEX idx_course_id (course_id),
        INDEX idx_course_student (course_id, student_id)
    );
    """

    cursor.execute(create_students_table)
    cursor.execute(create_registrations_table)


def load_students_from_csv(cursor, db_connection, student_csv_path):
    """
    Reads student.csv line-by-line and inserts data in batches using parameterized queries.
    """
    query = """
    INSERT INTO Students (student_id, name, spi)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE name = VALUES(name), spi = VALUES(spi);
    """

    batch = []
    with open(student_csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip header if present (uncomment if header row exists):
        # next(reader, None)

        for row in reader:
            if not row or len(row) < 3:
                continue
            student_id, name, spi = row[0].strip(), row[1].strip(), float(row[2].strip())
            batch.append((student_id, name, spi))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(query, batch)
                db_connection.commit()
                batch.clear()

        if batch:
            cursor.executemany(query, batch)
            db_connection.commit()


def load_registrations_from_csv(cursor, db_connection, registration_csv_path):
    """
    Reads registration.csv line-by-line and inserts data in batches using parameterized queries.
    """
    query = """
    INSERT INTO CourseRegistration (student_id, course_id)
    VALUES (%s, %s);
    """

    batch = []
    with open(registration_csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip header if present (uncomment if header row exists):
        # next(reader, None)

        for row in reader:
            if not row or len(row) < 2:
                continue
            student_id, course_id = row[0].strip(), row[1].strip()
            batch.append((student_id, course_id))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(query, batch)
                db_connection.commit()
                batch.clear()

        if batch:
            cursor.executemany(query, batch)
            db_connection.commit()


def query_analytics(cursor, target_course_id: str, spi_threshold: float):
    """
    Queries students registered for target_course_id with SPI > spi_threshold.
    Sorts output by SPI descending, then student_id ascending.
    """
    # Parameterized SQL query ensuring security against SQL Injection
    query = """
    SELECT 
        s.student_id, 
        s.name, 
        s.spi, 
        r.course_id
    FROM CourseRegistration r
    JOIN Students s ON r.student_id = s.student_id
    WHERE r.course_id = %s AND s.spi > %s
    ORDER BY s.spi DESC, s.student_id ASC;
    """

    cursor.execute(query, (target_course_id, spi_threshold))

    # Fetch and print results row-by-row
    for student_id, name, spi, course_id in cursor.fetchall():
        print(f"{student_id} {name} {float(spi)} {course_id}")


def run_analytics_engine(db_config, student_csv, registration_csv, course_id, spi_threshold):
    """
    Main driver function establishing database lifecycle with exception safety.
    """
    connection = None
    cursor = None
    try:
        # Establish connection to MySQL
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()

            # 1. Database & Table setup
            setup_database_schema(cursor)

            # 2. Bulk load data from CSVs
            load_students_from_csv(cursor, connection, student_csv)
            load_registrations_from_csv(cursor, connection, registration_csv)

            # 3. Query and display analytics
            query_analytics(cursor, course_id, spi_threshold)

    except Error as db_err:
        print(f"Database Error: {db_err}", file=sys.stderr)
    except FileNotFoundError as fnf_err:
        print(f"File Error: {fnf_err}", file=sys.stderr)
    except Exception as general_err:
        print(f"Unexpected Error: {general_err}", file=sys.stderr)
    finally:
        # Resource cleanup
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    # Database Configuration
    db_credentials = {
        'host': 'localhost',
        'database': 'university_db',
        'user': 'root',
        'password': 'your_password'
    }

    # Target parameters
    target_course = "PY101"
    threshold_spi = 8.0

    student_file = "student.csv"
    registration_file = "registration.csv"

    run_analytics_engine(
        db_credentials, student_file, registration_file, target_course, threshold_spi
    )
