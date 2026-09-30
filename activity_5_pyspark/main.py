from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import Bucketizer
from pyspark.sql.window import Window

REFERENCE_YEAR = 2018


def get_column_labels():
    import json

    with open("labels.json", encoding="utf-8") as file:
        return json.load(file)["column_labels"]


def get_age_labels():
    import json

    with open("labels.json", encoding="utf-8") as file:
        return json.load(file)["age_range_labels"]


def get_course_labels():
    import json

    with open("labels.json", encoding="utf-8") as file:
        return json.load(file)["course_labels"]


def start_session():
    return (
        SparkSession.builder.appName("Análise Cadastro Único")
        .master("local[*]")
        .config("spark.log.level", "ERROR")
        .getOrCreate()
    )


def calculate_age(df, col_labels=get_column_labels()):
    return (
        df.dropna(subset=col_labels["birth_date"])
        .withColumn(col_labels["birth_date"], F.to_date(col_labels["birth_date"]))
        .withColumn(
            "age", F.lit(REFERENCE_YEAR) - F.year(F.col(col_labels["birth_date"]))
        )
    )


def start_df():
    spark = start_session()
    return spark.read.csv(
        "amostra.csv/*.csv",
        header=True,
        inferSchema=True,
        encoding="utf-8",
    )

def spark_map(dict):
    return F.create_map(
        *[
            item
            for key, value in dict.items()
            for item in (F.lit(key), F.lit(value))
        ]
    )


def age_statistics(df, col_labels=get_column_labels()):
    if not df:
        df = start_df()

    moddf = calculate_age(df)

    moddf = moddf.dropna(subset=col_labels["race_color"])

    moddf.groupBy(col_labels["sex"], col_labels["race_color"]).agg(
        F.round(F.avg("age"), 2).alias("Média"),
        F.round(F.median("age"), 2).alias("Mediana"),
        F.round(F.stddev("age"), 2).alias("Desvio Padrão"),
    ).show()


def income_education_statistics(
    df, col_labels=get_column_labels()
):
    if not df:
        df = start_df()

    moddf = df.dropna(
        subset=[
            col_labels["previous_course"],
            col_labels["gross_year_income"],
            col_labels["completed_previous_course"],
        ]
    )

    moddf = moddf.groupBy(
        col_labels["completed_previous_course"], col_labels["previous_course"]
    ).agg(
        F.round(F.avg(col_labels["gross_year_income"]), 2).alias("Média"),
        F.round(F.median(col_labels["gross_year_income"]), 2).alias("Mediana"),
        F.round(F.stddev(col_labels["gross_year_income"]), 2).alias("Desvio Padrão"),
    )

    course_map = spark_map(get_course_labels())

    moddf.withColumn(
        "course_label", course_map[F.col(col_labels["previous_course"])]
    ).show()


def working_age_statistics(df=None, col_labels=get_column_labels()):
    if not df:
        df = start_df()

    age_groups = get_age_labels()

    moddf = df.dropna(subset=col_labels["employment_income"])

    moddf = calculate_age(moddf)

    bucketizer = Bucketizer(
        splits=age_groups["delimiters"], inputCol="age", outputCol="age_group"
    )

    moddf = bucketizer.transform(moddf)

    moddf = moddf.withColumn(
        "working",
        F.when(F.col(col_labels["employment_income"]) == 0, "0").otherwise("1"),
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
