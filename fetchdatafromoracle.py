import cx_Oracle
import csv

# Oracle database connection details
db_username = "your_username"
db_password = "your_password"
db_dsn = "your_dsn"  # Format: host:port/service_name

# Table names
source_table = "source_table"
destination_table = "destination_table"

# Fetch data from the source table
def fetch_data_to_csv(conn, table_name, csv_filename):
    cursor = conn.cursor()
    sql_query = f"SELECT * FROM {table_name}"
    
    cursor.execute(sql_query)
    
    with open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])  # Write column headers
        
        for row in cursor.fetchall():
            csv_writer.writerow(row)
    
    cursor.close()

# Copy data from the source table to the destination table
def copy_data_to_destination(conn, source_table_name, destination_table_name):
    cursor = conn.cursor()
    sql_query = f"INSERT INTO {destination_table_name} SELECT * FROM {source_table_name}"
    
    cursor.execute(sql_query)
    conn.commit()
    cursor.close()

try:
    # Connect to the Oracle database
    connection = cx_Oracle.connect(user=db_username, password=db_password, dsn=db_dsn)

    # Specify the CSV filename to save the data
    csv_filename = "data.csv"

    # Fetch data from the source table and save it to a CSV file
    fetch_data_to_csv(connection, source_table, csv_filename)

    # Copy data from the source table to the destination table
    copy_data_to_destination(connection, source_table, destination_table)

    # Close the database connection
    connection.close()

    print("Data fetched and saved to CSV file. Data copied to the destination table.")
except cx_Oracle.Error as error:
    print(f"Error: {error}")
