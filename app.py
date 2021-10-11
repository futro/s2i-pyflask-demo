
import logging
import logstash
import sys
from flask import Flask
from confluent_kafka import Producer
import socket


app = Flask(__name__)
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
host = 'logstash-client.ex.svc.cluster.local'
port_number = 5000
 
 
conf = {'bootstrap.servers': "host1:9092,host2:9092",
        'client.id': socket.gethostname()}


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
    if err is not None:
        return ("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        return ("Message produced: %s" % (str(msg)))

   

@app.route('/producer')
def get_producer():
 

    producer = Producer(conf)
    message_ack = producer.produce("futro-test-topic", key="key", value="value", callback=acked)

    return '<h1>'+message_ack+'</h1>'


@app.route('/consumer')
def get_consumer():
    
    return '<h1>Producer message</h1>'



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
   
