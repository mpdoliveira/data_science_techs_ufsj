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


def calculate_age(df, labels=get_labels()):
    return df.withColumn(
        "age", F.lit(REFERENCE_YEAR) - F.year(F.col(labels["birth_date"]))
    )


def read_csv():
    spark = start_session()
    return spark.read.csv(
        "amostra.csv/*.csv",
        header=True,
        inferSchema=True,
        encoding="utf-8",
    )


def age_statistics(df: DataFrame | None = None, labels=get_labels()):
    if not df:
        df = read_csv()

    df = df.withColumn(labels["birth_date"], F.to_date(labels["birth_date"]))

    df = calculate_age(df)

    df = df.dropna(subset=labels["race_color_code"])

    df = (
        df.groupBy(labels["sex_code"], labels["race_color_code"])
        .agg(
            F.avg("age").alias("Average"),
            F.median("age").alias("Median"),
            F.stddev("age").alias("Standard Deviation"),
        )
        .show()
    )


def income_education_statistics(df: DataFrame | None = None, labels=get_labels()):
    if not df:
        df = read_csv()

    df = df.dropna(
        subset=[
            labels["current_course_code"],
            labels["gross_income_last_12_months"],
            labels["completed_course_indicator"],
        ]
    )

    df = (
        df.groupBy(labels["completed_course_indicator"], labels["previous_course_code"])
        .agg(
            F.avg(labels["gross_income_last_12_months"]).alias("Average"),
            F.median(labels["gross_income_last_12_months"]).alias("Median"),
            F.stddev(labels["gross_income_last_12_months"]).alias("Standard Deviation"),
        )
        .show()
    )


if __name__ == "__main__":
    income_education_statistics()
