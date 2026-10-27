from pyspark.sql import functions as F
from pyspark.sql.window import Window
from helpers.helper import start_df, get_labels, clean_tse_df, spark_map


def summarize_correlations(
    df,
    correlation_col,
    top_n=3,
    group_cols=None,
):
    if group_cols is None:
        group_cols = ["office"]

    # Strongest positive correlations within each group.
    positive = (
        df.filter(F.col(correlation_col) > 0)
        .withColumn(
            "_rank",
            F.row_number().over(
                Window.partitionBy(*group_cols).orderBy(F.desc(correlation_col))
            ),
        )
        .filter(F.col("_rank") <= top_n)
        .withColumn("association", F.lit("Positive"))
        .drop("_rank")
    )

    # Strongest negative correlations within each group.
    negative = (
        df.filter(F.col(correlation_col) < 0)
        .withColumn(
            "_rank",
            F.row_number().over(
                Window.partitionBy(*group_cols).orderBy(F.asc(correlation_col))
            ),
        )
        .filter(F.col("_rank") <= top_n)
        .withColumn("association", F.lit("Negative"))
        .drop("_rank")
    )

    return positive.unionByName(negative).orderBy(
        *[F.col(column) for column in group_cols],
        F.desc(correlation_col),
    )


def poverty_political_party(
    ppldf=None,
    col_labels=None,
    poverty_limit=178,
):
    if ppldf is None:
        ppldf = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels") | get_labels("tse_column_labels")


    vtdf = start_df("votacao_partido_munzona_2018_BRASIL.csv", ";")

    vtdf = vtdf.filter(
        (F.col(col_labels["office"]) == "Presidente")
        & (F.col(col_labels["election_round"]) == 1)
    )

    vtdf = clean_tse_df(vtdf, col_labels)

    family_income = (
        ppldf.filter(F.col(col_labels["ibge_municipality_code"]).isNotNull() & F.col(col_labels["family_code"]).isNotNull())
        .groupBy(col_labels["ibge_municipality_code"], col_labels["family_code"])
        .agg(
            F.sum(
                F.coalesce(
                    F.col(col_labels["gross_year_income"]).cast("double"),
                    F.lit(0.0),
                )
            ).alias("family_year_income"),
            F.count(F.lit(1)).alias("family_size"),
        )
    )

    family_income = family_income.withColumn(
        "monthly_income_per_capita",
        F.col("family_year_income") / F.col("family_size") / 12,
    )

    poverty_df = (
        family_income.groupBy(col_labels["ibge_municipality_code"])
        .agg(
            (
                F.avg(
                    F.when(
                        F.col("monthly_income_per_capita") <= poverty_limit,
                        F.lit(1.0),
                    ).otherwise(F.lit(0.0))
                )
                * 100
            ).alias("poverty_percentage")
        )
        .select(
            F.lpad(
                F.col(col_labels["ibge_municipality_code"]).cast("string"),
                7,
                "0",
            ).alias("municipality_code"),
            "poverty_percentage",
        )
    )


    vote_df = vtdf.select(
        F.lpad(
            F.col("CD_MUNICIPIO_IBGE").cast("string"),
            7,
            "0",
        ).alias("municipality_code"),
        F.col(col_labels["party_number"]).alias("party_number"),
        F.col(col_labels["party_name"]).alias("party"),
        F.col(col_labels["office"]).alias("office"),
        F.col("party_votes"),
    )

    municipalities = (
        poverty_df.select("municipality_code")
        .distinct()
        .join(
            vote_df.select("municipality_code").distinct(),
            on="municipality_code",
            how="inner",
        )
    )

    party_offices = vote_df.select(
        "party_number",
        "party",
        "office",
    ).distinct()

    municipal_votes = (
        municipalities.crossJoin(party_offices)
        .join(
            vote_df,
            on=[
                "municipality_code",
                "party_number",
                "party",
                "office",
            ],
            how="left",
        )
        .withColumn(
            "party_votes",
            F.coalesce(F.col("party_votes"), F.lit(0)),
        )
    )

    municipal_votes = municipal_votes.withColumn(
        "total_votes",
        F.sum("party_votes").over(Window.partitionBy("municipality_code", "office")),
    )

    municipal_votes = municipal_votes.withColumn(
        "vote_percentage",
        F.when(
            F.col("total_votes") > 0,
            F.col("party_votes") / F.col("total_votes") * 100,
        ),
    )

    analysis_df = municipal_votes.join(
        poverty_df,
        on="municipality_code",
        how="inner",
    )

    correlation_df = (
        analysis_df.groupBy("office", "party_number", "party")
        .agg(
            F.corr(
                "poverty_percentage",
                "vote_percentage",
            ).alias("poverty_vote_correlation"),
            F.count_distinct("municipality_code").alias("municipalities_analyzed"),
        )
        .filter(F.col("poverty_vote_correlation").isNotNull())
        .withColumn(
            "poverty_vote_correlation",
            F.round(F.col("poverty_vote_correlation"), 3),
        )
        .orderBy(F.desc("poverty_vote_correlation"))
    )

    return summarize_correlations(
        correlation_df,
        correlation_col="poverty_vote_correlation",
        top_n=3,
    )


def average_income_political_party(ppldf=None, vtdf=None, col_labels=None):
    if ppldf is None:
        ppldf = start_df()

    if col_labels is None:
        col_labels = get_labels("column_labels") | get_labels("tse_column_labels")

    municipality = col_labels["ibge_municipality_code"]
    family = col_labels["family_code"]
    income = col_labels["gross_year_income"]
    party_number = col_labels["party_number"]
    party_name = col_labels["party_name"]
    office = col_labels["office"]

    if vtdf is None:
        vtdf = start_df("votacao_partido_munzona_2018_BRASIL.csv", ";")

    vtdf = vtdf.filter(F.trim(F.col(office)) == "Presidente")
    vtdf = clean_tse_df(vtdf, col_labels)

    family_income = (
        ppldf.filter(
            F.col(municipality).isNotNull()
            & F.col(family).isNotNull()
        )
        .groupBy(municipality, family)
        .agg(
            F.sum(
                F.coalesce(F.col(income).cast("double"), F.lit(0.0))
            ).alias("family_year_income"),
            F.count("*").alias("family_size"),
        )
        .withColumn(
            "monthly_income_per_capita",
            F.col("family_year_income") / F.col("family_size") / 12,
        )
    )

    income_df = (
        family_income.groupBy(municipality)
        .agg(
            F.avg("monthly_income_per_capita").alias("average_income")
        )
        .select(
            F.lpad(
                F.col(municipality).cast("string"), 7, "0"
            ).alias("municipality_code"),
            "average_income",
        )
    )

    vote_df = vtdf.select(
        F.lpad(
            F.col("CD_MUNICIPIO_IBGE").cast("string"), 7, "0"
        ).alias("municipality_code"),
        F.col(party_number).alias("party_number"),
        F.col(party_name).alias("party"),
        F.col("party_votes"),
    )

    municipalities = (
        income_df.select("municipality_code").distinct()
        .join(
            vote_df.select("municipality_code").distinct(),
            on="municipality_code",
            how="inner",
        )
    )

    parties = vote_df.select("party_number", "party").distinct()

    municipal_votes = (
        municipalities.crossJoin(parties)
        .join(
            vote_df,
            on=["municipality_code", "party_number", "party"],
            how="left",
        )
        .withColumn(
            "party_votes",
            F.coalesce(F.col("party_votes"), F.lit(0)),
        )
    )

    municipal_votes = municipal_votes.withColumn(
        "total_votes",
        F.sum("party_votes").over(
            Window.partitionBy("municipality_code")
        ),
    )

    municipal_votes = municipal_votes.withColumn(
        "vote_percentage",
        F.when(
            F.col("total_votes") > 0,
            F.col("party_votes") / F.col("total_votes") * 100,
        ),
    )

    analysis_df = municipal_votes.join(
        income_df,
        on="municipality_code",
        how="inner",
    )

    result_df = (
        analysis_df.groupBy("party_number", "party")
        .agg(
            F.corr(
                "average_income",
                "vote_percentage",
            ).alias("income_vote_correlation"),
            F.count_distinct("municipality_code").alias(
                "municipalities_analyzed"
            ),
        )
        .filter(F.col("income_vote_correlation").isNotNull())
        .withColumn(
            "income_vote_correlation",
            F.round(F.col("income_vote_correlation"), 3),
        )
        .withColumn("office", F.lit("Presidente"))
    )

    return summarize_correlations(
        result_df,
        correlation_col="income_vote_correlation",
        top_n=3,
    )


if __name__ == "__main__":
    people_df = start_df()

    poverty_political_party(ppldf=people_df).show()
    average_income_political_party().show(10, truncate=False)
