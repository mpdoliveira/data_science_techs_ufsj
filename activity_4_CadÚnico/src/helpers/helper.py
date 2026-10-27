from pyspark.sql import functions as F

REFERENCE_YEAR = 2018

# Helper functions


def get_labels(title=None):
    import json

    with open("src/helpers/labels.json", encoding="utf-8") as file:
        if title is None:
            return json.load(file)
        return json.load(file)[title]


def start_session():
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName("Análise Cadastro Único")
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.log.level", "ERROR")
        .getOrCreate()
    )


def start_df(path=None, sep=None):
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
    elif path is None:
        path = "amostra.csv/*.csv"

    if len(sys.argv) > 2:
        sep = sys.argv[2]
    elif sep is None:
        sep = ","

    spark = start_session()
    return spark.read.csv(
        path, header=True, inferSchema=True, encoding="utf-8", sep=sep
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
        col_labels = get_labels("column_labels")

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


from pyspark.sql import functions as F


def clean_tse_df(df=None, col_labels=None):
    if df is None:
        df = start_df("votacao_partido_munzona_2018_BRASIL.csv", ";")

    if col_labels is None:
        col_labels = get_labels("tse_column_labels")

    municipality = col_labels["municipality_code"]
    party_number = col_labels["party_number"]
    party_name = col_labels["party_name"]
    office = col_labels["office"]
    list_votes = col_labels["valid_party_list_votes"]
    nominal_votes = col_labels["valid_nominal_votes"]

    # Load the TSE-IBGE municipality code mapping.
    mapping_path = (
        r"C:\Users\marco\OneDrive\Documentos\GitHub"
        r"\data_science_techs_ufsj\activity_5_pyspark"
        r"\municipio_tse_ibge.csv"
    )

    mapping_df = (
        df.sparkSession.read.option("header", True).option("sep", ";").csv(mapping_path)
    )

    mapping_df = mapping_df.select(
        F.lpad(
            F.trim(F.col("CD_MUNICIPIO_TSE").cast("string")),
            5,
            "0",
        ).alias("_tse_code"),
        F.lpad(
            F.trim(F.col("CD_MUNICIPIO_IBGE").cast("string")),
            7,
            "0",
        ).alias("CD_MUNICIPIO_IBGE"),
    )

    mapping_df = mapping_df.filter(
        F.col("CD_MUNICIPIO_IBGE").isNotNull()
    ).dropDuplicates(["_tse_code"])

    # Keep only municipalities with a valid TSE-IBGE match.
    moddf = df.join(
        mapping_df,
        F.lpad(
            F.trim(F.col(municipality).cast("string")),
            5,
            "0",
        )
        == F.col("_tse_code"),
        "inner",
    )

    moddf = moddf.select(
        "CD_MUNICIPIO_IBGE",
        party_number,
        party_name,
        office,
        list_votes,
        nominal_votes,
    )

    moddf = moddf.withColumn(
        "party_votes",
        F.coalesce(F.col(list_votes), F.lit(0))
        + F.coalesce(F.col(nominal_votes), F.lit(0)),
    )

    moddf = moddf.groupBy(
        "CD_MUNICIPIO_IBGE",
        party_number,
        party_name,
        office,
    ).agg(F.sum("party_votes").alias("party_votes"))

    return moddf
