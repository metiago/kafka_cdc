## Kafka Change Data Capture (CDC)

Process of capturing changes in data from a database and streaming those changes to Apache Kafka.

### First Things First

To get started with Debezium and Kafka using Docker, follow these steps to launch the necessary containers:

Ensure you have Docker, Docker Compose and Python installed on your machine.

```bash
docker-compose up -d

python -m venv venv

pip install confluent-kafka
```

### Database Config

To set up your MySQL database for Change Data Capture (CDC) using Debezium, you need to ensure that the appropriate user has the necessary privileges. The command you provided is a good start, but let’s break it down and clarify the steps involved:

1. **Log into MySQL**: You start by logging into your MySQL server as the root user (or another user with sufficient privileges).

```bash
mysql -u root -p
```

2. **Create a Debezium User**: It’s a good practice to create a dedicated user for Debezium rather than using the root user. You can create a user with the following command:

```sql
CREATE USER 'mysqluser'@'%' IDENTIFIED BY 'your_password';
```

Replace `'your_password'` with a strong password.

3. **Grant Privileges**: You need to grant the necessary privileges to the user you just created. The command you provided grants the required privileges for CDC:

```sql
GRANT SELECT, RELOAD, SUPER, REPLICATION SLAVE ON *.* TO 'mysqluser'@'%';
```

- `SELECT`: Allows reading data from the database.
- `RELOAD`: Allows the user to execute commands like `FLUSH`.
- `SUPER`: Allows the user to perform administrative operations.
- `REPLICATION SLAVE`: Required for reading the binary log.

4. **Flush Privileges**: After granting privileges, you should flush them to ensure that MySQL recognizes the changes:

```sql
FLUSH PRIVILEGES;
```

5. **Enable Binary Logging**: Ensure that binary logging is enabled in your MySQL configuration (`my.cnf` or `my.ini`). You need to add or uncomment the following lines:

```ini
[mysqld]
log_bin = mysql-bin
binlog_format = row
```

The `binlog_format` should be set to `row` to capture row-level changes, which is necessary for Debezium to work correctly.

6. **Restart MySQL**: After making changes to the configuration file, restart the MySQL server to apply the changes.

7. **Set Up Debezium**: Once your MySQL database is configured, you can set up Debezium to start capturing changes and streaming them to Kafka.

By following these steps, you will have your MySQL database properly configured for CDC with Debezium. Make sure to replace placeholder values with your actual database credentials and settings.

## MySQL Connector Configuration for Kafka Connect

This configuration sets up a Kafka Connect connector using Debezium to capture changes from a MySQL database. The connector streams changes from the specified MySQL table into Kafka topics, enabling real-time data processing and analytics.

### Configuration Overview

The following JSON configuration is used to define the MySQL connector:

```json
{
  "name": "mysql-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "mydb",
    "database.port": "3306",
    "database.user": "mysqluser",
    "database.password": "mysqlpw",
    "database.server.id": "1",
    "database.server.name": "mydb",
    "table.whitelist": "inventory.langs",
    "topic.prefix": "mysql-",
    "database.history.kafka.bootstrap.servers": "kafka:9093",
    "database.history.kafka.topic": "mydb.inventory.history",
    "schema.history.internal.kafka.bootstrap.servers": "kafka:9093",
    "schema.history.internal.kafka.topic": "mydb.schema.history",
    "include.schema.changes": "false"
  }
}
```

### Key Configuration Parameters

- **name**: The name of the connector instance (e.g., `mysql-connector`).
- **connector.class**: Specifies the Debezium MySQL connector class.
- **tasks.max**: The maximum number of tasks to run for this connector (set to `1` for simplicity).
- **database.hostname**: The hostname of the MySQL database (e.g., `mydb`).
- **database.port**: The port on which the MySQL database is running (default is `3306`).
- **database.user**: The username for connecting to the MySQL database (e.g., `mysqluser`).
- **database.password**: The password for the MySQL user (e.g., `mysqlpw`).
- **database.server.id**: A unique identifier for the MySQL server (must be unique across all servers).
- **database.server.name**: A logical name for the MySQL server, used as a prefix for the generated Kafka topics.
- **table.whitelist**: A comma-separated list of tables to capture changes from (e.g., `inventory.langs`).
- **topic.prefix**: The prefix to use for the Kafka topics that will receive the change events (e.g., `mysql-`).
- **database.history.kafka.bootstrap.servers**: The Kafka bootstrap servers for storing database history.
- **database.history.kafka.topic**: The Kafka topic for storing the database history.
- **schema.history.internal.kafka.bootstrap.servers**: The Kafka bootstrap servers for storing schema history.
- **schema.history.internal.kafka.topic**: The Kafka topic for storing schema history.
- **include.schema.changes**: Set to `false` to exclude schema change events from the output.

### How to Use

1. **Prerequisites**: Ensure that you have Kafka and Kafka Connect set up, along with a running MySQL database configured for CDC as described in the previous sections.

2. **Deploy the Connector**: Use the Kafka Connect REST API to deploy the connector with the above configuration. You can do this by sending a POST request to the Kafka Connect endpoint:

```bash
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors -d @connectors/mysql-source.json
```

Replace `http://localhost:8083` with the appropriate address of your Kafka Connect instance.

3. **Monitor the Connector**: After deploying, you can monitor the status of the connector and its tasks through the Kafka Connect REST API.

```bash
curl -X GET http://localhost:8083/connectors/mysql-connector/status
```

4. **Consume Data**: Once the connector is running, you can consume the change events from the specified Kafka topics (e.g., `main.py`) using any Kafka consumer.

## Debezium Events

In the context of Debezium and Kafka, when you capture change events from a database, the events typically include a JSON payload that contains a `payload` key. This payload includes two main attributes: `before` and `after`. Here's what each of these attributes represents:

1. **`before`**: 
   - The `before` attribute contains the state of the record before the change occurred. 
   - This is particularly useful for understanding what the data looked like prior to an update or delete operation.
   - If the event represents an insert operation, the `before` attribute will be `null` because there was no previous state for the newly inserted record.

2. **`after`**: 
   - The `after` attribute contains the state of the record after the change has been applied.
   - This reflects the current state of the record in the database after an insert, update, or delete operation.
   - If the event represents a delete operation, the `after` attribute will be `null` because the record has been removed from the database.

### Example

Here’s an example of what a change event might look like:

```json
{
  "payload": {
    "before": {
      "id": 1,
      "name": "Old Name",
      "value": 100
    },
    "after": {
      "id": 1,
      "name": "New Name",
      "value": 200
    },
    "source": {
      "version": "1.0.0",
      "connector": "mysql",
      "name": "mydb",
      "ts_ms": 1620000000000,
      "snapshot": "false",
      "db": "inventory",
      "table": "langs",
      "server_id": 1,
      "gtid": null,
      "file": "mysql-bin.000001",
      "pos": 12345,
      "row": 0,
      "thread": 1,
      "query": null
    },
    "op": "u",  // Operation type: 'c' for create, 'u' for update, 'd' for delete
    "ts_ms": 1620000000000
  }
}
```

### Explanation of the payload

- **`before`**: Shows the state of the record before the update, with `id` 1 having the name "Old Name" and value 100.
- **`after`**: Shows the updated state of the record after the change, with `id` 1 now having the name "New Name" and value 200.
- **`op`**: Indicates the type of operation that triggered the event. In this case, it is an update (`"u"`).

### Use Cases

- **Data Auditing**: You can track changes over time by comparing the `before` and `after` states.
- **Event Sourcing**: You can reconstruct the history of changes by processing the events in order.
- **Data Synchronization**: You can use the `before` and `after` states to update other systems or caches accordingly.

Understanding the `before` and `after` attributes is crucial for effectively processing change events in your applications.