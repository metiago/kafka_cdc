import json
from confluent_kafka import Consumer, KafkaError

conf = {
    'bootstrap.servers': 'localhost:9092',  
    'group.id': 'my_group',                 
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
topic = 'mysql-.inventory.customers'
consumer.subscribe([topic])

try:
    while True:
        # Timeout of 1 second
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition event')
            else:
                print(f'Error: {msg.error()}')
        else:
            message = json.loads(msg.value().decode("utf-8"))
            payload = message.get("payload")
            _id = payload.get("after").get("id")
            name = payload.get("after").get("first_name")
            print(f"Language id: {_id} and name: {name}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()


def print_languages(message):
    payload = message.get("payload")
    _id = payload.get("after").get("id")
    name = payload.get("after").get("name")
    print(f"Language id: {_id} and name: {name}")