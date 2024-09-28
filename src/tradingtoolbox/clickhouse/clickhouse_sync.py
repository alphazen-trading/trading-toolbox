import pandas as pd
import clickhouse_connect
from pydantic import BaseModel, ConfigDict
from clickhouse_connect.driver.client import Client
from .generate_table_schema import generate_table_schema


class BaseCH(BaseModel):
    host: str = "localhost"
    port: int = 8123
    database: str = "default"
    user: str = "default"
    password: str = ""


class ClickhouseSync(BaseModel):
    """
    An sync clickhouse client.

    Usage:
        ```python
        from tradingtoolbox.clickhouse import ClickhouseSync

        client = ClickhouseSync.create(
            host="localhost",
            port=8123,
            user="default",
            password="",
            database="default",
        )

        # Or you can create it without passing anything, and it will use the above defaults
        async_client = ClickhouseSync.create()
        ```
    """

    client: Client

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
    )

    @classmethod
    def create(cls, **kwargs):
        base = BaseCH(**kwargs)
        kwargs["client"] = clickhouse_connect.get_client(
            host=base.host,
            port=base.port,
            username=base.user,
            password=base.password,
            database=base.database,
        )
        self = cls(**kwargs)

        return self

    def insert_df(self, df: pd.DataFrame, table_name: str, drop=False):
        """
        Parameters:
            df: The dataframe to insert
            table_name: The name of the table to insert into
            drop: Whether to drop the table if it already exists
        """
        if drop:
            self.drop_table(table_name)
        schema = generate_table_schema(df, table_name)

        self.client.command(schema)
        self.client.insert_df(table_name, df)

    def execute_command(self, msg: str):
        """
        Allows you to run any command you want

        Parameters:
            query: The query to execute
        """
        self.client.command(msg)

    # =============================================================== #

    def drop_table(self, table_name: str):
        """
        Drops a table from the database

        Parameters:
            table_name: The table's name
        """
        return self.execute_command(f"DROP TABLE IF EXISTS {table_name}")

    def create_table(
        self,
        table_name: str,
        schema: str,
        partition_key: str = "",
        order_by: str = "",
        primary_key: str = "",
        drop: bool = False,
    ):
        """
        Create a table

        Parameters:
            table_name: The name of the table
            schema: The schema of the table
            partition_key: The partition key
            order_by: The order by
            primary_key: The primary key
            drop: Whether to drop the table if it already exists
        """
        if drop:
            self.drop_table(table_name)

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

    def optimize_table(self, table_name: str):
        """
        Optimizes a table

        Parameters:
            table_name: The name of the table
        """
        command = f"OPTIMIZE TABLE {table_name} FINAL"
        return self.execute_command(command)

    def query(self, query: str):
        """
        Runs a query

        Parameters:
            query: The query to run
        """
        return self.client.query(query)

    def query_df(self, query: str):
        """
        Runs a query and returns the results as a dataframe

        Parameters:
            query: The query to run
        """
        return self.client.query_df(query)
