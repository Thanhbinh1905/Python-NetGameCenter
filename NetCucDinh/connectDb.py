import pypyodbc as odbc
import datetime

# Database connection details
DRIVER_NAME = 'SQL Server'
SERVER_NAME = 'QUANGBACH'
DATABASE_NAME = 'NetCucDinh'
UID = 'sa'
PWD = '12345'

# Function to connect to SQL Server database
def connect_sql_server():
    conn_str = f'DRIVER={DRIVER_NAME};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};UID={UID};PWD={PWD}'
    connection = odbc.connect(conn_str)
    return connection

# Function to execute an SQL query with optional parameters
def execute_query(connection, query, params=None):
    cursor = connection.cursor()
    if params is not None:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor

# Function to close cursor and connection
def close_resources(cursor, conn):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except Exception as e:
        print(f"Error while closing resources: {str(e)}")

# # Example usage: Inserting a record into Usage table
# try:
#     conn = connect_sql_server()
#     current_time = datetime.datetime.now()
#     query = "INSERT INTO Usage (SeatID, StartTime, IsActive) VALUES (?, ?, ?)"
#     cursor = execute_query(conn, query, (1, current_time, 1))
#     conn.commit()  # Commit the transaction after successful execution
#     print("Insert successful!")
# except Exception as e:
#     print(f"Error inserting record: {str(e)}")
# finally:
#     close_resources(cursor, conn)