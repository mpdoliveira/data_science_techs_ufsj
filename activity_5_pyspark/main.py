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
        .filter((F.col("age") >= 0) & (F.col("age") <= 130))
    )


def start_df():
    spark = start_session()
    return spark.read.csv(
        "amostra.csv/*.csv",
        header=True,
        inferSchema=True,
        encoding="utf-8",
    )


def spark_map(labels):
    return F.create_map(
        *[item for key, value in labels.items() for item in (F.lit(key), F.lit(value))]
    )


def bool_map(
    df,
    input_col,
    output_col="bool_map",
    true=1,
    false=2,
):
    return df.withColumn(
        output_col,
        F.when(F.col(input_col) == true, "Sim").when(F.col(input_col) == false, "Não"),
    )


def spark_bucketizer(df, config, inputCol, output_col="grouped"):

    output_index_col = f"{output_col}_index"
    moddf = Bucketizer(
        splits=config["delimiters"], inputCol=inputCol, outputCol=output_index_col
    ).transform(df)

    label_map = spark_map(dict(enumerate(config["labels"])))

    return moddf.withColumn(output_col, label_map[F.col(output_index_col).cast("int")])


def age_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_column_labels()

    moddf = calculate_age(df)

    moddf = moddf.dropna(subset=col_labels["race_color"])

    moddf = moddf.groupBy(col_labels["sex"], col_labels["race_color"]).agg(
        F.round(F.avg("age"), 2).alias("Média"),
        F.round(F.median("age"), 2).alias("Mediana"),
        F.round(F.stddev("age"), 2).alias("Desvio Padrão"),
    )

    moddf.show()


def income_education_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_column_labels()

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

    moddf = moddf.withColumn(
        "Escolaridade", course_map[F.col(col_labels["previous_course"])]
    )

    moddf = bool_map(moddf, col_labels["completed_previous_course"], "Concluiu")

    moddf = moddf.orderBy(
        col_labels["previous_course"], col_labels["completed_previous_course"]
    )

    moddf.select("Escolaridade", "Concluiu", "Média", "Mediana", "Desvio Padrão").show()


def working_age_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_column_labels()

    moddf = df.dropna(subset=col_labels["employment_income"])

    moddf = calculate_age(moddf)

    moddf = spark_bucketizer(moddf, get_age_labels(), "age", "age_group")

    moddf = moddf.withColumn(
        "working",
        F.when(F.col(col_labels["employment_income"]) == 0, 2).otherwise(1),
    )

    moddf = moddf.groupBy("working", "age_group", "age_group_index").count()

    moddf = moddf.withColumn(
        "Porcentagem",
        F.round(
            F.col("count") / F.sum("count").over(Window.partitionBy("age_group")) * 100,
            2,
        ),
    )

    moddf = bool_map(moddf, "working", "Trabalha")

    moddf = moddf.orderBy(
        "age_group_index",
        "working"
    )

    moddf.select(
        F.col("age_group").alias("Faixa Etária"),
        "Trabalha",
        "Porcentagem"
        ).show()


def disabled_family_income(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_column_labels()

    moddf = df.dropna(subset=[col_labels["disability"]])

    moddf = moddf.groupBy(col_labels["family_code"]).agg(
        F.sum(col_labels["gross_year_income"]).alias("family_year_income"),
        F.count("*").alias("family_members"),
        F.sum(F.when(F.col(col_labels["disability"]) == 1, 1).otherwise(0)).alias(
            "disabled_members"
        ),
    )

    moddf = moddf.dropna(subset="family_year_income")

    moddf = moddf.withColumn(
        "per_capta_income", F.col("family_year_income") / F.col("family_members") / 12
    )

    income_labels = get_income_labels()
    moddf = spark_bucketizer(moddf, income_labels, "per_capta_income", "income_group")

    moddf = moddf.groupBy("income_group").agg(
        F.sum("disabled_members").alias("disabled"),
        F.sum("family_members").alias("total"),
    )

    moddf = moddf.withColumn(
        "Porcentagem", F.round(F.col("disabled") / F.col("total") * 100, 2)
    )

    moddf.select(F.col("income_group").alias("Faixa de Renda"), "Porcentagem").show()


if __name__ == "__main__":
    df = start_df()
    col_labels = get_column_labels()
    age_statistics(df, col_labels)
    income_education_statistics(df, col_labels)
    working_age_statistics(df, col_labels)
    disabled_family_income(df, col_labels)
