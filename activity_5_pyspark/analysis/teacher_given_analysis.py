from pyspark.sql import functions as F

from helpers.helper import start_df, get_labels


def income_race_sex(df=None, col_labels=None):
    from helpers.helper import spark_map

    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = df.dropna(
        subset=[
            col_labels["sex"],
            col_labels["race_color"],
            col_labels["employment_income"],
        ]
    )

    moddf = moddf.groupBy(col_labels["sex"], col_labels["race_color"]).agg(
        F.round(F.avg(col_labels["employment_income"]), 2).alias("Média"),
        F.round(F.median(col_labels["employment_income"]), 2).alias("Mediana"),
    )

    moddf = moddf.withColumn("Diferença", F.abs(F.col("Média") - F.col("Mediana")))

    moddf = spark_map(moddf, get_labels("sex_labels"), col_labels["sex"], "Sexo")
    moddf = spark_map(
        moddf, get_labels("race_labels"), col_labels["race_color"], "Raça"
    )

    moddf = moddf.orderBy(col_labels["race_color"], col_labels["sex"])

    return moddf.select("Raça", "Sexo", "Diferença")


def education_formal_work(df=None, col_labels=None):
    from helpers.helper import calculate_formal_work, spark_map

    if df is None:
        df = start_df()
    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = calculate_formal_work(df, col_labels)

    moddf = moddf.withColumn(
        "education_simplified",
        F.when(F.col(col_labels["previous_course"]).isin([1, 2, 15]), 0)
        .when(F.col(col_labels["previous_course"]).isin([5, 6, 7, 11]), 1)
        .when(F.col(col_labels["previous_course"]).isin([8, 9, 12]), 2)
        .when(F.col(col_labels["previous_course"]) == 13, 3),
    ).dropna(subset=["education_simplified"])

    moddf = moddf.groupBy("education_simplified").agg(
        F.sum(F.when(F.col("formal_work") == 2, 1).otherwise(0)).alias(
            "Trabalho Informal"
        ),
        F.count("*").alias("Total"),
    )

    moddf = moddf.withColumn(
        "Trabalho Informal (%)",
        F.round(F.col("Trabalho Informal") / F.col("Total") * 100, 2),
    )

    moddf = spark_map(
        moddf,
        get_labels("simple_course_labels"),
        "education_simplified",
        "Escolaridade",
    )

    moddf = moddf.orderBy("education_simplified")

    return moddf.select(
        "Escolaridade",
        "Trabalho Informal (%)",
    )


def disabled_age(df=None, col_labels=None):
    from helpers.helper import calculate_age, spark_bucketizer
    from pyspark.sql.window import Window

    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = df.select(
        col_labels["family_code"],
        col_labels["disability"],
        col_labels["birth_date"],
    ).dropna(
        subset=[
            col_labels["disability"],
            col_labels["birth_date"],
        ]
    )

    moddf = calculate_age(moddf, col_labels)

    moddf = spark_bucketizer(
        moddf, get_labels("simple_age_range_labels"), "age", "Faixa Etária"
    )

    family_income = (
        df.select(
            col_labels["family_code"],
            col_labels["gross_year_income"],
        )
        .dropna(subset=[col_labels["family_code"]])
        .groupBy(col_labels["family_code"])
        .agg(
            F.sum(col_labels["gross_year_income"]).alias("family_year_income"),
            F.count("*").alias("family_members"),
        )
    )

    family_income = family_income.withColumn(
        "per_capita_income",
        F.col("family_year_income") / F.col("family_members") / 12,
    )

    moddf = moddf.filter(F.col(col_labels["disability"]) == 1)

    moddf = moddf.join(
        family_income,
        on=col_labels["family_code"],
        how="left",
    )

    moddf = moddf.groupBy("Faixa Etária", "Faixa Etária_index").agg(
        F.count("*").alias("PCD"),
        F.count("per_capita_income").alias("PCD com renda conhecida"),
        F.sum(F.when(F.col("per_capita_income") <= 89, 1).otherwise(0)).alias(
            "PCD em extrema pobreza"
        ),
    )

    moddf = moddf.withColumn(
        "Distribuição PCD (%)",
        F.round(
            F.col("PCD") / F.sum("PCD").over(Window.partitionBy()) * 100,
            2,
        ),
    )

    moddf = moddf.withColumn(
        "Extrema pobreza (%)",
        F.when(
            F.col("PCD com renda conhecida") > 0,
            F.round(
                F.col("PCD em extrema pobreza")
                / F.col("PCD com renda conhecida")
                * 100,
                2,
            ),
        ),
    )

    moddf = moddf.orderBy("Faixa Etária_index")

    return moddf.select("Faixa Etária", "Distribuição PCD (%)", "Extrema pobreza (%)")


def responsible_child_occupation(df=None, col_labels=None):
    from helpers.helper import calculate_age, spark_map, calculate_formal_work
    from pyspark.sql.window import Window

    if df is None:
        df = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels")

    moddf = df.select(
        col_labels["family_relationship"],
        col_labels["birth_date"],
        col_labels["family_code"],
        col_labels["gross_year_income"],
        col_labels["employment_income"],
        col_labels["sex"]
    )

    moddf = moddf.dropna(
        subset=[
            col_labels["family_relationship"],
            col_labels["family_code"],
        ]
    )

    moddf = moddf.filter(
        ~(
            (F.col(col_labels["family_relationship"]) == 1)
            & (F.col(col_labels["sex"]) == 1)
        )
    )

    moddf = calculate_age(moddf, col_labels)

    moddf = moddf.filter(
        F.when(F.col("age") <= 6, True)
        .when(
            (F.col(col_labels["family_relationship"]) == 1) & (F.col("age") < 50), True
        )
        .otherwise(False)
    )

    moddf = moddf.withColumn(
        "has_kids",
        F.max(F.when(F.col("age").between(0, 6), 1).otherwise(0)).over(
            Window.partitionBy(col_labels["family_code"])
        ),
    )

    moddf = moddf.filter(F.col(col_labels["family_relationship"]) == 1)

    moddf = calculate_formal_work(moddf, col_labels)

    moddf = moddf.groupBy("has_kids", "formal_work").count()

    moddf = moddf.withColumn(
        "Porcentagem",
        F.round(
            F.col("count") / F.sum("count").over(Window.partitionBy("has_kids")) * 100,
            2,
        ),
    )

    moddf = moddf.orderBy(F.desc("has_kids"), "formal_work")

    moddf = spark_map(moddf, get_labels("trad_boolean_labels"), "has_kids", "Tem criança")

    moddf = spark_map(moddf, get_labels("boolean_labels"), "formal_work", "Trabalha")

    return moddf.select("Tem criança", "Trabalha", "Porcentagem")


if __name__ == "__main__":
    df = start_df()
    col_labels = get_labels("column_labels")

    income_race_sex(df, col_labels).show()
    education_formal_work(df, col_labels).show()
    disabled_age(df, col_labels).show()
    responsible_child_occupation(df, col_labels).show()
