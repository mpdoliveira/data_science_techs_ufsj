from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import Bucketizer
from pyspark.sql.window import Window

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


# Activity Tasts
# Part 1 - Demographic analysis and labor market


# Part 1, task 1 - 1.1
# Age distribution by sex and race/color combination
def age_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = calculate_age(df)

    moddf = moddf.dropna(subset=col_labels["race_color"])

    moddf = moddf.groupBy(col_labels["sex"], col_labels["race_color"]).agg(
        F.round(F.avg("age"), 2).alias("Média"),
        F.round(F.median("age"), 2).alias("Mediana"),
        F.round(F.stddev("age"), 2).alias("Desvio Padrão"),
    )

    moddf = spark_map(moddf, get_labels("sex_labels"), col_labels["sex"], "Sexo")
    moddf = spark_map(
        moddf, get_labels("race_labels"), col_labels["race_color"], "Cor/Raça"
    )

    moddf = moddf.orderBy(col_labels["race_color"], col_labels["sex"])

    return moddf.select("Cor/Raça", "Sexo", "Média", "Mediana", "Desvio Padrão")


# Part 1, task 2 - 1.2
# Percentage of formal labor vs informal (any income source that is not employment)
def work_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = df.dropna(
        subset=[col_labels["gross_year_income"], col_labels["employment_income"]]
    )

    moddf = calculate_age(moddf, col_labels)

    moddf = moddf.filter(F.col("age").between(18, 65))

    moddf = moddf.withColumn(
        "formal_working",
        F.when(
            (F.col(col_labels["gross_year_income"]) != 0)
            & (F.col(col_labels["employment_income"]) == 0),
            2,
        ).otherwise(1),
    )

    moddf = moddf.groupBy("formal_working").count()

    moddf = moddf.withColumn(
        "Porcentagem",
        F.round(F.col("count") / F.sum("count").over(Window.partitionBy()) * 100, 2),
    )

    moddf = spark_map(
        moddf, get_labels("boolean_labels"), "formal_working", "Trabalha formal"
    )

    return moddf.select("Trabalha formal", "Porcentagem")


# Part 1, task 3 - 1.3
# Average individual gross income by education level
def income_education_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

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

    moddf = spark_map(
        moddf,
        get_labels("course_labels"),
        col_labels["previous_course"],
        "Escolaridade",
    )

    moddf = spark_map(
        moddf,
        get_labels("boolean_labels"),
        col_labels["completed_previous_course"],
        "Concluiu",
    )

    moddf = moddf.orderBy(
        col_labels["previous_course"], col_labels["completed_previous_course"]
    )

    return moddf.select("Escolaridade", "Concluiu", "Média", "Mediana", "Desvio Padrão")


# Part 2 - Working and education profile analysis


# Part 2, task 1 - 2.1
# Employed individuals by age group
def working_age_statistics(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = df.dropna(subset=col_labels["employment_income"])

    moddf = calculate_age(moddf)

    moddf = spark_bucketizer(moddf, get_labels("age_range_labels"), "age", "age_group")

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

    moddf = spark_map(moddf, get_labels("boolean_labels"), "working", "Trabalha")

    moddf = moddf.orderBy("age_group_index", "working")

    return moddf.select(
        F.col("age_group").alias("Faixa Etária"), "Trabalha", "Porcentagem"
    )


# Part 2, task 2 - 2.2
# Percentage of disabled members in each family range
def disabled_family_income(df=None, col_labels=None):
    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

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

    income_labels = get_labels("income_labels")
    moddf = spark_bucketizer(moddf, income_labels, "per_capta_income", "income_group")

    moddf = moddf.groupBy("income_group", "income_group_index").agg(
        F.sum("disabled_members").alias("disabled"),
        F.sum("family_members").alias("total"),
    )

    moddf = moddf.withColumn(
        "Porcentagem PCD", F.round(F.col("disabled") / F.col("total") * 100, 2)
    )

    moddf = moddf.orderBy("income_group_index")

    return moddf.select(
        F.col("income_group").alias("Faixa de Renda"), "Porcentagem PCD"
    )


# Run each analysis
if __name__ == "__main__":
    df = start_df()
    col_labels = get_labels("column_labels")
    age_statistics(df, col_labels).show()
    work_statistics(df, col_labels).show()
    income_education_statistics(df, col_labels).show(30)
    working_age_statistics(df, col_labels).show()
    disabled_family_income(df, col_labels).show()
