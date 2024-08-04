import os
import pandas as pd
import oracledb
from paramiko import Transport, SFTPClient

def get_oracle_connection():
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    hostname = os.getenv("DB_HOSTNAME")
    database = os.getenv("DB_DATABASE")
    dsn = oracledb.makedsn(hostname, 1521, service_name=database)
    return oracledb.connect(username, password, dsn)



def fetch_data():
    connection = get_oracle_connection()
    cursor = connection.cursor()
    with open('config/query.sql', 'r') as file:
        query = file.read()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return pd.DataFrame(data, columns=columns)


def filter_and_save_data(df):
    filtered_df = df[df['status'] == 'Completed']
    filtered_df.to_csv('filtered_data.txt', sep='\t', index=False, header=False)


def transfer_file():
    hostname = os.getenv("SFTP_HOSTNAME")
    username = os.getenv("SFTP_USERNAME")
    password = os.getenv("SFTP_PASSWORD")

    transport = Transport((hostname, 22))
    transport.connect(username=username, password=password)
    sftp = SFTPClient.from_transport(transport)

    sftp.put('filtered_data.txt', '/usr/www/ncc/trashfiles/filtered_data.txt')

    sftp.close()
    transport.close()


def main():
    df = fetch_data()
    filter_and_save_data(df)
    transfer_file()


if __name__ == "__main__":
    main()
