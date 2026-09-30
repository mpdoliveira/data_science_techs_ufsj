from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import DataFrame

REFERENCE_YEAR = 2018


def get_labels():
    import json

    with open("labels.json") as file:
        return json.load(file)["labels"]

def start_session():
    return (
        SparkSession.builder.appName("Análise Cadastro Único")
        .master("local[*]")
        .config("spark.log.level", "ERROR")
        .getOrCreate()
    )

def read_csv():
    spark = start_session()
    return spark.read.csv(
            "amostra.csv/*.csv",
            header=True,
            inferSchema=True,
            encoding="utf-8",
        )


def age_statistics(df: DataFrame | None = None):
    if not df:
        df = read_csv()

    labels = get_labels()
    df = df.withColumn(labels["birth_date"], F.to_date(labels["birth_date"]))

    df = df.withColumn(
        "age", F.lit(REFERENCE_YEAR) - F.year(F.col(labels["birth_date"]))
    )

    df = (
        df.groupBy(labels["sex_code"], labels["race_color_code"])
        .agg(
            F.avg("age").alias("Average"),
            F.median("age").alias("Median"),
            F.stddev("age").alias("Standard Deviation"),
        )
        .show()
    )


if __name__ == "__main__":
    age_statistics()
