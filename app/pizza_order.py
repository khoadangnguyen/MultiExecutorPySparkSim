from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, max, desc, hour, count

log4j_conf = "log4j.properties"

spark = SparkSession.builder \
    .appName("Pizza Order") \
    .getOrCreate()

orders_df = spark.read.csv(
    "./MultiExecutorPySparkSim/data/orders.csv",
    header=True,
    inferSchema=True
)

order_details_df = spark.read.csv(
    "./MultiExecutorPySparkSim/data/order_details.csv",
    header=True,
    inferSchema=True
)

pizzas_df = spark.read.csv(
    "./MultiExecutorPySparkSim/data/pizzas.csv",
    header=True,
    inferSchema=True
)

"""
    Total number of orders
"""
total_number_orders = orders_df.select("order_id").distinct().count()
total_number_ordered_items = order_details_df.count()

print()
print(f"Total number of orders: {total_number_orders}")
print(f"Total number items ordered: {total_number_ordered_items}")
print(f"Average number item per order: {round(total_number_ordered_items/total_number_orders, 2)}")


"""
    Total sale
"""
order_details_pizzas_df = order_details_df.join(pizzas_df, on="pizza_id", how="inner")
order_details_pizzas_df = order_details_pizzas_df.withColumn("sales", col("quantity") * col("price"))
total_sale = round(order_details_pizzas_df.agg(sum("sales").alias("total_sale")).collect()[0]["total_sale"], 2)
print(f"Total sale : {total_sale}")

"""
    Find the highest price pizza
"""
pizza_types_df = spark.read.csv(
    "./MultiExecutorPySparkSim/data/pizza_types.csv",
    header=True,
    inferSchema=True
)

highest_price = pizzas_df.agg(max(col('price'))).collect()[0][0]
print()
print(f"The highest pizza price is {highest_price}")
print("Pizza with highest price is:")
pizzas_pizza_types_df = pizzas_df.join(pizza_types_df, on="pizza_type_id", how="inner")
highest_price_pizza_df = pizzas_pizza_types_df.filter(col("price") == highest_price)
highest_price_pizza_df.rdd.foreach(lambda row: print(f"\tPizza name: {row['name']} size: {row['size']}"))

"""
    Find top 5 most ordered pizzas
"""
quantity_by_pizza_type = order_details_df.groupby(col("pizza_id")).agg(sum("quantity").alias("total_ordered_quantity"))
top5_quantity_by_pizza_type = quantity_by_pizza_type.orderBy(desc("total_ordered_quantity")).limit(5)
top5_ordered_quantity = top5_quantity_by_pizza_type.join(pizzas_df, on="pizza_id", how="inner")\
    .select("pizza_type_id", "total_ordered_quantity")\
    .join(pizza_types_df, on="pizza_type_id", how="inner")\
    .select("name", "total_ordered_quantity")
print()
print(f"Top 5 most ordered pizza")
top5_ordered_quantity_rows = top5_ordered_quantity.orderBy(desc("total_ordered_quantity")).collect()
for row in top5_ordered_quantity_rows:
    print(f"\tPizza name = {row['name']}\t\tordered quantity = {row['total_ordered_quantity']}")


"""
    Total ordered quantity of each pizza category
"""
print()
print(f"Total ordered quantity of each pizza category")
order_details_pizza_id_quantity = order_details_df.select("pizza_id", "quantity")
ordered_quantity_by_category =\
    order_details_pizza_id_quantity.join(pizzas_df, on="pizza_id", how="inner")\
    .select("pizza_type_id", "quantity")\
    .join(pizza_types_df, on="pizza_type_id", how="inner")\
    .select("category", "quantity")\
    .groupby("category").agg(sum("quantity").alias("total_ordered_quantity"))

ordered_quantity_by_category.rdd.foreach(lambda row: print(f"\tCategory: {row['category']}, Total ordered quantity = {row['total_ordered_quantity']}"))
print(f"Total ordered quantity = {ordered_quantity_by_category.agg(sum('total_ordered_quantity')).collect()[0][0]}")


"""
    Determine the distribution of orders by hour of the day.
"""
print()
print(f"Distribution of orders by hour of the day")
orders_df\
    .select("order_id", hour("time").alias("order_hour")) \
    .groupby("order_hour") \
    .agg(count("order_id").alias("order_count")) \
    .orderBy("order_hour") \
    .show()


"""
    Find the category-wise distribution of pizzas
    (assumption by total order)
"""
print()
print(f"Find the category-wise distribution of pizzas (by total order)")
pizza_types_df.select("category", "pizza_type_id") \
    .join(
        pizzas_df.select("pizza_id", "pizza_type_id"),
        on="pizza_type_id", how="inner") \
    .join(
        order_details_df.select("order_id", "pizza_id"),
        on="pizza_id", how="inner") \
    .groupby("category") \
    .agg(count("order_id").alias("total_order")) \
    .show()
