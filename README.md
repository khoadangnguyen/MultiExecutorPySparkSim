# MultiExecutorPySparkSim
Simulating the behavior and performance of multiple executors for a PySpark application

### Description
This project is an extended version of my previous project [Pizza Order Analysis With PySpark](https://github.com/khoadangnguyen/PizzaOrderAnalysisWithPySpark)
where the PySpark application runs on multiple-executor environment instead of one single executor.

### Setup
- One spark master container, 4 spark executor containers, and the network are created by utilizing bitnami/spark image and docker compose file.
- Each container is configured to share the resource of the local machine. 
- Application folder containing data, PySpark application, log4j.properties file, and spark configuration file is mapped 
from local machine to the container where the spark master will
execute the PySpark application and the spark executors will read data to handle the tasks.
  - Executors might not need to share the same folder having PySpark application, but data needs to be shared and accessible
  by all executors (simulating data in a distributed executing environment).
- The application uses it own spark configuration file and this file is specified with --properties-file when executing
spark-submit command.
```bash
docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --properties-file /opt/bitnami/spark/MultiExecutorPySparkSim/spark.conf \
  --files ./MultiExecutorPySparkSim/app/log4j.properties \
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:./MultiExecutorPySparkSim/app/log4j.properties" \
  --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:./MultiExecutorPySparkSim/app/log4j.properties" \
./MultiExecutorPySparkSim/app/pizza_order.py
```
- Similar to previous project, spark application event logs are configured to store to the project directory under spark-event-log.
- Spark history server is configured (either in config file or environment variable) to load data from the same spark-event-log project directory.
```bash
spark-default.conf
spark.history.fs.logDirectory=./spark-event-log
```
or
```bash
export SPARK_HISTORY_OPTS=-Dspark.history.fs.logDirectory=./spark-event-log
```

Commands used to create and remove docker containers
```bash
docker-compose up
docker-compose down
```

Commands used to start and stop spark history server
```bash
start-history-server.sh
stop-history-server.sh
```

### Future improvement
- Utilize different approach for data storage in order for executors to access