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
            col_labels["race"],
            col_labels["employment_income"]
        ]
    )

    moddf = moddf.groupBy(col_labels["sex"], col_labels["race"]).agg(
        F.round(F.avg(col_labels["employment_income"]), 2).alias("Média"),
        F.round(F.median(col_labels["employment_income"]), 2).alias("Mediana")
    )

    moddf = moddf.withColumn(
        "Diferença",
        F.abs(F.col("Média") - F.col("Mediana"))
    )

    moddf = spark_map(moddf, get_labels("sex_labels"), col_labels["sex"], "Sexo")
    moddf = spark_map(moddf, get_labels("race_labels"), col_labels["race"], "Raça")

    moddf = moddf.orderBy(col_labels["race"], col_labels["sex"])

    return moddf.select("Sexo", "Raça", "Diferença")


