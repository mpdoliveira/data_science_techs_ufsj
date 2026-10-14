from pyspark.sql import functions as F


REFERENCE_YEAR = 2018

# Helper functions


def get_labels(title=None):
    import json

    with open("labels.json", encoding="utf-8") as file:
        if title is None:
            return json.load(file)
        return json.load(file)[title]


def start_session():
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName("Análise Cadastro Único")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
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
    from pyspark.ml.feature import Bucketizer

    # Categorize in buckets based on a config range and save on output_index_col
    output_index_col = f"{output_col}_index"
    moddf = Bucketizer(
        splits=config["delimiters"], inputCol=input_col, outputCol=output_index_col
    ).transform(df)

    # Return dataframe with index and label columns
    return spark_map(
        moddf, dict(enumerate(config["labels"])), output_index_col, output_col
    )


def calculate_age(df, col_labels=None):
    if col_labels is None:
        col_labels = get_labels("column_labels")

    return (
        df.dropna(subset=col_labels["birth_date"])
        .withColumn(col_labels["birth_date"], F.to_date(col_labels["birth_date"]))
        .withColumn(
            "age", F.lit(REFERENCE_YEAR) - F.year(F.col(col_labels["birth_date"]))
        )
        .filter((F.col("age") >= 0) & (F.col("age") <= 130))
    )

def calculate_formal_work(df, col_labels=None):
    if col_labels is None:
        col_labels=get_labels("column_labels")

    moddf = df.dropna(
            subset=[col_labels["gross_year_income"], col_labels["employment_income"]]
        )

    moddf = moddf.withColumn(
            "formal_work",
            F.when(
                (F.col(col_labels["gross_year_income"]) != 0)
                & (F.col(col_labels["employment_income"]) == 0),
                2,
            ).otherwise(1),
        )

    return moddf
