
import logging
import logstash
import sys
from flask import Flask
from confluent_kafka import Producer, Consumer
import socket
import confluent_kafka.admin, pprint

app = Flask(__name__)
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
host = 'logstash-client.ex.svc.cluster.local'
port_number = 5000
 
kafka_host =  "a1-kafka-0.a1-kafka-headless.ex.svc.cluster.local:9092, a1-kafka-1.a1-kafka-headless.ex.svc.cluster.local:9092, a1-kafka-3.a1-kafka-headless.ex.svc.cluster.local:9092"
 
topic = "futro.test.topic"
@app.route('/')
def hello_world():
    return '<h1>Hello, World ! - Pyflask Demo</h1>'

@app.route('/version')
def get_version():
    return '<h1>App version : <b>1.0</b></h1>'

@app.route('/test')
def get_test():
    return '<h1>You are accessing /test endpoint</h1>'

@app.route('/message')
def get_message():
    #test_logger.addHandler(logstash.LogstashHandler(host, 5959, version=1))
    test_logger.addHandler(logstash.TCPLogstashHandler(host, port_number, version=1))

    test_logger.error('futro-python-logstash: test logstash error message.')
    test_logger.info('futro-python-logstash: test logstash info message.')
    test_logger.warning('futro-python-logstash: test logstash warning message.')

# add extra field to logstash message
    extra = {
       'test_string': 'python version: ' + repr(sys.version_info),
       'test_boolean': True,
       'test_dict': {'a': 1, 'b': 'c'},
       'test_float': 1.23,
       'test_integer': 123,
       'test_list': [1, 2, '3'],
    }
    test_logger.info('futro-python-logstash: test extra fields', extra=extra)
    
    return '<h1>Log message</h1>'


@app.route('/topic')
def get_topic():
    conf        = {'bootstrap.servers': kafka_host}
    kafka_admin = confluent_kafka.admin.AdminClient(conf)
    new_topic   = confluent_kafka.admin.NewTopic(topic, 1, 3)
                  # Number-of-partitions  = 1
                  # Number-of-replicas    = 1
    kafka_admin.create_topics([new_topic,]) # CREATE (a list(), so you can create multiple).
    
    return "<h1> Topic Created" +' '.join(kafka_admin.list_topics().topics)+"</h1>"
   
def acked(err, msg):
    test_logger.addHandler(logstash.TCPLogstashHandler(host, port_number, version=1))
    if err is not None:
        test_logger.info("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        test_logger.info("Message produced: %s" % (str(msg)))

@app.route('/producer')
def get_producer():
    conf = {'bootstrap.servers': kafka_host,
       'client.id': 'futro-test'} #socket.gethostname()}

    producer = Producer(conf)
    producer.produce(topic, key="key", value="value", callback=acked)
    producer.flush()
    
    return '<h1>Producer</h1>'


@app.route('/consumer')
def get_consumer():
 
    conf = {'bootstrap.servers': kafka_host, 'session.timeout.ms': 6000,
       'group.id': 'KMOffsetCache-kafka-manager-5c678c8b7d-8x68h'} #socket.gethostname()}
    test_logger.addHandler(logstash.TCPLogstashHandler(host, port_number, version=1))
    consumer = Consumer(conf,  logger=test_logger)
    consumer.subscribe([topic])
    
    for i in range(10):
        msg = consumer.poll(1.0)
        if msg is None:
            test_logger.info('No message')
        else:
            if msg.error():
                test_logger.error(msg.error())
            else:
                # Proper message
                test_logger.info('%% %s [%d] at offset %d with key %s:\n' %
                                     (msg.topic(), msg.partition(), msg.offset(),
                                      str(msg.key())))
                test_logger.info(msg.value())  
    consumer.close()

    return '<h1>Consumer</h1>'



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
   
