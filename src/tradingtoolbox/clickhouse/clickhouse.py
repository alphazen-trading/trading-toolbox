import asyncio
import clickhouse_connect

from .generate_table_schema import generate_table_schema

default_config = {
    "host": "localhost",
    "port": 8123,
    "username": "default",
    "password": "",
    "database": "default",
}


class Clickhouse:
    def __init__(self, config=default_config):
        super().__init__()
        self.client = clickhouse_connect.get_client(
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            database=config["database"],
        )

    def insert_df(self, df, table_name, drop=False):
        if drop:
            self.drop_table(table_name)
        schema = generate_table_schema(df, table_name)
        self.client.command(schema)
        self.client.insert_df(table_name, df)

    def execute_command(self, msg: str):
        self.client.command(msg)

    # =============================================================== #

    def drop_table(self, table_name):
        if self.client is None:
            return
        return self.execute_command(f"DROP TABLE IF EXISTS {table_name}")

    def create_table(
        self,
        table_name,
        schema,
        partition_key="",
        order_by="",
        primary_key="",
        drop=False,
    ):
        if drop:
            self.drop_table(table_name)

        if self.client is None:
            return
        query_string = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    {schema}
)
ENGINE = ReplacingMergeTree()
{partition_key}
{order_by}
{primary_key}
"""
        # print(query_string)
        return self.execute_command(query_string)

    def optimize_table(self, table_name):
        if self.client is None:
            return
        command = f"OPTIMIZE TABLE {table_name} FINAL"
        return self.execute_command(command)

    def query(self, query):
        return self.client.query(query)

    def query_df(self, query):
        return self.client.query_df(query)
