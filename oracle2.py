from sqlalchemy import create_engine

# Define the connection string
connection_string = "oracle+pyodbc://username:password@hostname:port/your_database"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Example: Execute a query
with engine.connect() as connection:
    result = connection.execute("SELECT * FROM your_table")
    for row in result:
        print(row)

# Close the database connection (optional)
engine.dispose()
