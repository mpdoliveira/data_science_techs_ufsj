from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import json


def age_distribution(df):
    with open("label.json") as config_file:
        config = json.load(config_file)["age_groups"]

    df = df.withColumn("age", )

    df.groupBy("age", "race").agg(
        F.avg("age").alias("Average"),
        F.median("age").alias("Median"),
        F.stddev("age").alias("Standart Deviation"),
    ).show()

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Data analysis CadÚnico").getOrCreate()

    df = spark.read.csv("amostra.csv", encoding="utf-8", header=True, inferSchema=True)

    print(df.columns)
