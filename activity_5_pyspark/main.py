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


def get_income_labels():
    import json

    with open("labels.json", encoding="utf-8") as file:
        return json.load(file)["income_labels"]


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


def spark_bucketizer(df, dict, inputCol, outputCol="grouped"):
    return Bucketizer(
        splits=dict["delimiters"], inputCol=inputCol, outputCol=outputCol
    ).transform(df)


def spark_map(dict):
    return F.create_map(
        *[item for key, value in dict.items() for item in (F.lit(key), F.lit(value))]
    )


def age_statistics(df=start_df(), col_labels=get_column_labels()):
    moddf = calculate_age(df)

    moddf = moddf.dropna(subset=col_labels["race_color"])

    moddf.groupBy(col_labels["sex"], col_labels["race_color"]).agg(
        F.round(F.avg("age"), 2).alias("Média"),
        F.round(F.median("age"), 2).alias("Mediana"),
        F.round(F.stddev("age"), 2).alias("Desvio Padrão"),
    ).show()


def income_education_statistics(df, col_labels=get_column_labels()):
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


def working_age_statistics(df=start_df(), col_labels=get_column_labels()):

    moddf = df.dropna(subset=col_labels["employment_income"])

    moddf = calculate_age(moddf)

    moddf = spark_bucketizer(moddf, get_age_labels(), "age", "age_group")

    moddf = moddf.withColumn(
        "working",
        F.when(F.col(col_labels["employment_income"]) == 0, "0").otherwise("1"),
    )

    moddf = moddf.groupBy("working").count()

    moddf = moddf.withColumn(
        "Porcentagem",
        F.round(F.col("count") / F.sum("count").over(Window.partitionBy()) * 100, 2),
    )

    moddf.select("Porcentagem").show()


def disabled_family_income(df=start_df(), col_labels=get_column_labels()):

    moddf = df.dropna(
        subset=[col_labels["gross_year_income"], col_labels["disability"]]
    )

    moddf = moddf.groupBy(col_labels["family_code"]).agg(
        F.sum(col_labels["gross_year_income"]).alias("family_year_income"),
        F.count("*").alias("family_members"),
        F.sum(F.when(F.col(col_labels["disability"]) == 1, 1).otherwise(0)).alias(
            "disabled_members"
        ),
    )

    moddf = moddf.withColumn(
        "per_capta_income", F.col("family_year_income") / F.col("family_members") / 12
    )

    income_labels = get_income_labels()
    moddf = spark_bucketizer(
        moddf, income_labels, "per_capta_income", "income_group"
    )

    moddf = moddf.groupBy("income_group").agg(
        F.sum("disabled_members").alias("disabled"),
        F.sum("family_members").alias("total")
    )

    moddf = moddf.withColumn(
        "Porcentagem",
        F.round(F.col("disabled") / F.col("total") * 100, 2)
    )

    income_map = spark_map(dict(enumerate(income_labels["labels"])))
    moddf = moddf.withColumn(
        "Faixa de Renda", income_map[F.col("income_group")] 
    )

    moddf.select("Faixa de Renda", "Porcentagem").show()


if __name__ == "__main__":
    df = start_df()
    col_labels = get_column_labels()
    age_statistics(df, col_labels)
    income_education_statistics(df, col_labels)
    working_age_statistics(df, col_labels)
    disabled_family_income(df, col_labels)
