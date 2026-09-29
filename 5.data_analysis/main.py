from pyspark.sql import SparkSession


if __name__ == "__main__":
    spark = SparkSession.builder.appName("Data analysis CadÚnico").getOrCreate()

    df = spark.read.csv("amostra.csv", encoding="utf-8", header=True, inferSchema=True)

    print(df.columns)
