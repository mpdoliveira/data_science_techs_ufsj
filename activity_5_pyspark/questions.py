from pyspark.sql import functions as F

from helper import start_df, get_labels


def income_race_sex(df=None, col_labels=None):
    from helper import spark_map

    if df is None:
        df=start_df()

    if col_labels is None:
        col_labels=get_labels("column_labels")

    moddf = df.dropna(
        subset=[
            col_labels["sex"],
            col_labels["race_color"],
            col_labels["employment_income"]
        ]
    )

    moddf = moddf.groupBy(col_labels["sex"], col_labels["race_color"]).agg(
        F.round(F.avg(col_labels["employment_income"]), 2).alias("Média"),
        F.round(F.median(col_labels["employment_income"]), 2).alias("Mediana")
    )

    moddf = moddf.withColumn(
        "Diferença",
        F.abs(F.col("Média") - F.col("Mediana"))
    )

    moddf = spark_map(moddf, get_labels("sex_labels"), col_labels["sex"], "Sexo")
    moddf = spark_map(moddf, get_labels("race_labels"), col_labels["race_color"], "Raça")

    moddf = moddf.orderBy(col_labels["race_color"], col_labels["sex"])

    return moddf.select("Sexo", "Raça", "Diferença")

def education_formal_work(df=None, col_labels=None):
    from helper import calculate_formal_working

    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = calculate_formal_working(df, col_labels)

    moddf = moddf.filter(
        F.col(col_labels["employment_income"]) > 0
    )

    moddf = moddf.withColumn(
        "education_simplified",
        F.when(F.col(col_labels["previous_course"]).isin([1, 2, 15]), 0)
        .when(F.col(col_labels["previous_course"]).isin([5, 6, 7, 11]), 1)
        .when(F.col(col_labels["previous_course"]).isin([8, 9, 12]), 2)
        .when(F.col(col_labels["previous_course"]) == 13, 3)
        .otherwise(None),
    ).dropna(subset=["education_simplified", "formal_working"])

    moddf = moddf.groupBy("education_simplified").agg(
        F.round(
            F.avg(
                F.when(F.col("formal_working") == 0, 1).otherwise(0)
            ) * 100,
            2,
        ).alias("Trabalho Informal (%)")
    )

    moddf = moddf.withColumn(
        "Escolaridade",
        F.when(F.col("education_simplified") == 0, "Sem instrução")
        .when(F.col("education_simplified") == 1, "Fundamental")
        .when(F.col("education_simplified") == 2, "Médio")
        .when(F.col("education_simplified") == 3, "Superior"),
    )

    moddf = moddf.orderBy("education_simplified")

    return moddf.select("Escolaridade", "Trabalho Informal (%)")

