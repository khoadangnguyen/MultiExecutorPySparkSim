from pyspark.sql import SparkSession

log4j_conf = "log4j.properties"

spark = SparkSession.builder \
    .appName("Top 3 by revenue") \
    .getOrCreate()


