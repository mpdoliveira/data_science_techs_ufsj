from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import Bucketizer
from pyspark.sql import DataFrame
from pyspark.sql.window import Window

REFERENCE_YEAR = 2018


def get_column_labels():
    import json

    with open("labels.json") as file:
        return json.load(file)["column_labels"]


def get_age_labels():
    import json

    with open("labels.json") as file:
        return json.load(file)["age_range_labels"]


def get_course_labels():
    import json

    with open("labels.json") as file:
        return json.load(file)["course_labels"]


def start_session():
    return (
        SparkSession.builder.appName("Análise Cadastro Único")
        .master("local[*]")
        .config("spark.log.level", "ERROR")
        .getOrCreate()
    )


def calculate_age(df, labels=get_column_labels()):
    return (
        df.dropna(subset=labels["birth_date"])
        .withColumn(labels["birth_date"], F.to_date(labels["birth_date"]))
        .withColumn("age", F.lit(REFERENCE_YEAR) - F.year(F.col(labels["birth_date"])))
    )


def start_df():
    spark = start_session()
    return spark.read.csv(
        "amostra.csv/*.csv",
        header=True,
        inferSchema=True,
        encoding="utf-8",
    )


def age_statistics(df: DataFrame | None = None, labels=get_column_labels()):
    if not df:
        df = start_df()

    moddf = calculate_age(df)

    moddf = moddf.dropna(subset=labels["race_color_code"])

    moddf.groupBy(labels["sex_code"], labels["race_color_code"]).agg(
        F.round(F.avg("age").alias("Média"), 2),
        F.round(F.median("age").alias("Mediana"), 2),
        F.round(F.stddev("age").alias("Desvio Padrão"), 2),
    ).show()


def income_education_statistics(
    df: DataFrame | None = None, labels=get_column_labels()
):
    if not df:
        df = start_df()

    moddf = df.dropna(
        subset=[
            labels["previous_course_code"],
            labels["gross_income_last_12_months"],
            labels["completed_course_indicator"],
        ]
    )

    moddf = moddf.groupBy(
        labels["completed_course_indicator"], labels["previous_course_code"]
    ).agg(
        F.round(F.avg(labels["gross_income_last_12_months"]).alias("Média"), 2),
        F.round(F.median(labels["gross_income_last_12_months"]).alias("Mediana"), 2),
        F.round(
            F.stddev(labels["gross_income_last_12_months"]).alias("Desvio Padrão"), 2
        ),
    )

    moddf.withColumn("course_label", F.col(labels[""]))


def working_age_statistics(df=None, labels=get_column_labels()):
    if not df:
        df = start_df()

    age_groups = get_age_labels()

    moddf = df.dropna(subset=labels["employment_income"])

    moddf = calculate_age(moddf)

    bucketizer = Bucketizer(
        splits=age_groups["delimiters"], inputCol="age", outputCol="age_group"
    )

    moddf = bucketizer.transform(moddf)

    moddf = moddf.withColumn(
        "working", F.when(F.col(labels["employment_income"]) == 0, "0").otherwise("1")
    )

    moddf = (
        moddf.groupBy("working")
        .count()
        .withColumn(
            "Porcentagem",
            F.round(
                F.col("count") / F.sum("count").over(Window.partitionBy()) * 100, 2
            ),
        )
    )

    moddf.select("Porcentagem").show()


if __name__ == "__main__":
    df = start_df()

    labels = get_column_labels()
    income_education_statistics(df, labels)
