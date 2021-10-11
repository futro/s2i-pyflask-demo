
import logging
import logstash
import sys
from flask import Flask
from confluent_kafka import Producer, Consumer
import socket


app = Flask(__name__)
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
host = 'logstash-client.ex.svc.cluster.local'
port_number = 5000
 
 
conf = {'bootstrap.servers': "a1-kafka-0.a1-kafka-headless.ex.svc.cluster.local:9092",
        'client.id': socket.gethostname()}
topic = "futro-test-topic"
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

def acked(err, msg):
    test_logger.addHandler(logstash.TCPLogstashHandler(host, port_number, version=1))
    if err is not None:
        test_logger.info("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        test_logger.info("Message produced: %s" % (str(msg)))

   

@app.route('/producer')
def get_producer():
    producer = Producer(conf)
    ack = producer.produce(topic, key="key", value="value", callback=acked)
    producer.flush()
    
    return '<h1>Producer</h1>'


@app.route('/consumer')
def get_consumer():
    consumer = Consumer(conf)
    consumer.subscribe([topic])
    msg = consumer.poll(1.0)
    if msg is not None:
        test_logger.info('futro-python-logstash: test from consumer fields', extra=msg)
      
    consumer.close()

    return '<h1>Consumer</h1>'



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
   
