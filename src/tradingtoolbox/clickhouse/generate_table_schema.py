import pandas as pd


def generate_table_schema(df: pd.DataFrame, table_name: str):
    """
    Generates the schema for a table from a pandas dataframe

    Parameters:
        df: The dataframe to generate the schema from
        table_name: The name of the table to insert the df into
    """
    schema = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    for column in df.columns:
        dtype = df[column].dtype
        if dtype == "int64":
            clickhouse_type = "Int32"
        elif dtype == "float64":
            clickhouse_type = "Float64"
        elif dtype == "bool":
            clickhouse_type = "UInt8"
        elif dtype == "datetime64[ns]" or dtype == "datetime64[ns, UTC]":
            clickhouse_type = "DateTime"
        else:
            clickhouse_type = "String"
        schema += f"{column} {clickhouse_type}, "
    schema = schema.rstrip(", ") + ") ENGINE = MergeTree ORDER BY tuple()"
    return schema
