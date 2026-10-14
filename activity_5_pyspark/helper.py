from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import Bucketizer


REFERENCE_YEAR = 2018

# Helper functions


def get_labels(title):
    import json

    with open("labels.json", encoding="utf-8") as file:
        return json.load(file)[title]


def start_session():
    return (
        SparkSession.builder.appName("Análise Cadastro Único")
        .master("local[*]")
        .config("spark.log.level", "ERROR")
        .getOrCreate()
    )


def start_df():
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "amostra.csv/*.csv"

    if len(sys.argv) > 2:
        sep=sys.argv[2]
    else:
        sep=','
    
    spark = start_session()
    return spark.read.csv(
        path,
        header=True,
        inferSchema=True,
        encoding="utf-8",
        sep=sep
    )


def spark_map(df, labels, input_col, output_col="mapped"):
    map = F.create_map(
        *[item for key, value in labels.items() for item in (F.lit(key), F.lit(value))]
    )

    return df.withColumn(output_col, map[F.col(input_col).cast("int")])


def spark_bucketizer(df, config, input_col, output_col="grouped"):

    # Categorize in buckets based on a config range and save on output_index_col
    output_index_col = f"{output_col}_index"
    moddf = Bucketizer(
        splits=config["delimiters"], inputCol=input_col, outputCol=output_index_col
    ).transform(df)

    # Return dataframe with index and label columns
    return spark_map(
        moddf, dict(enumerate(config["labels"])), output_index_col, output_col
    )


def calculate_age(df, col_labels=get_labels("column_labels")):
    return (
        df.dropna(subset=col_labels["birth_date"])
        .withColumn(col_labels["birth_date"], F.to_date(col_labels["birth_date"]))
        .withColumn(
            "age", F.lit(REFERENCE_YEAR) - F.year(F.col(col_labels["birth_date"]))
        )
        .filter((F.col("age") >= 0) & (F.col("age") <= 130))
    )


