from pyspark.sql import SparkSession
from pyspark.sql.functions import date_format, sum, count, col, round, when


log4j_conf = "log4j.properties"

spark = SparkSession.builder \
    .appName("Average Pizza Order per Day") \
    .getOrCreate()


"""
    Calculate the average number of pizzas ordered per day
"""

orders_df = spark.read.csv(
    "./MultiExecutorPySparkSim/data/orders.csv",
    header=True,
    inferSchema=True
)

print("Orders' schema")
orders_df.printSchema()
print("Example data")
orders_df.show(5)
print(f"Orders' total rows: {orders_df.count()}")
orders_df.describe().show()

orders_df = orders_df.withColumn("day", date_format("date", "EEEE"))
orders_df.show(5)

order_detail_df = spark.read.csv(
    "./MultiExecutorPySparkSim/data/order_details.csv",
    header=True,
    inferSchema=True
)
print("Order details' schema")
order_detail_df.printSchema()
print("Example data")
order_detail_df.show(5)
print(f"Order details' total rows: {order_detail_df.count()}")
order_detail_df.describe().show()

orders_order_details_df = orders_df.join(order_detail_df,
                                         orders_df["order_id"] == order_detail_df["order_id"],
                                         "inner")
orders_order_details_df.show(5)
group_by_date_df = orders_order_details_df\
    .groupby("date")\
    .agg(sum("quantity").alias("quantity"))\
    .orderBy(col("date"))
group_by_date_df = group_by_date_df.withColumn("day", date_format("date", "EEEE"))
total_pizzas_by_day_df = group_by_date_df\
    .groupBy("day")\
    .agg(sum("quantity").alias("total_ordered_pizzas"))
total_pizzas_by_day_df = total_pizzas_by_day_df.withColumnRenamed("day", "day_total_pizzas")
total_pizzas_by_day_df.show()
total_day_df = group_by_date_df.groupBy("day").agg(count("day").alias("count"))
total_day_df = total_day_df.withColumnRenamed("day", "day_total")
total_day_df.show()
avg_pizzas_by_day = total_pizzas_by_day_df.join(total_day_df,
                                                total_pizzas_by_day_df["day_total_pizzas"] == total_day_df["day_total"],
                                                "inner")
avg_pizzas_by_day = avg_pizzas_by_day\
    .withColumn("avg_pizzas", round(col("total_ordered_pizzas")/col("count"), 2))\
    .withColumn("day_number",
                when(col("day_total") == "Monday", 1)
                .when(col("day_total") == "Tuesday", 2)
                .when(col("day_total") == "Wednesday", 3)
                .when(col("day_total") == "Thursday", 4)
                .when(col("day_total") == "Friday", 5)
                .when(col("day_total") == "Saturday", 6)
                .when(col("day_total") == "Sunday", 7))\
    .orderBy("day_number")
avg_pizzas_by_day = avg_pizzas_by_day.select("day_total", "count", "total_ordered_pizzas", "avg_pizzas")
avg_pizzas_by_day = avg_pizzas_by_day\
    .withColumnRenamed("day_total", "day")\
    .withColumnRenamed("count", "count_day")
avg_pizzas_by_day.show()
data = avg_pizzas_by_day.collect()
csv_data = []
header = ",".join(avg_pizzas_by_day.columns)
csv_data.append(header)

spark.stop()
# Add rows
for row in data:
    csv_data.append(','.join(str(value) for value in row))

# Write the CSV data to a file
with open('./MultiExecutorPySparkSim/output/avg_ordered_pizzas_by_day.csv', 'w') as file:
    for line in csv_data:
        file.write(line + '\n')
