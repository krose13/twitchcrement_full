from cassandra.cluster import Cluster
from kafka import KafkaConsumer
import time
import os
consumer = KafkaConsumer('spammessage',
                                 auto_offset_reset='latest',
                                 enable_auto_commit=True,
                                 bootstrap_servers=[str(os.environ['KAFKAPORT'])]
)
x = consumer.poll(100)                                                                                                       
consumer.seek_to_end()                                                                                                       

cluster = Cluster([str(os.environ['CASSANDRA_ADDRESS'])], port=os.environ['CASSANDRA_PORT'])

session = cluster.connect()
session.set_keyspace('spamevents')

while True:
    for message in consumer:
        mw = message.value.split(' ')
        mwlen = len(mw)
        nspammers = (mw[mwlen-1])
        smw = mw[1:(mwlen-3-int(nspammers))]
        spamstr = ' '.join(smw)
        realspammers = (int(nspammers)/2) 
        timestring = str(int(time.time()))
        print mw[0], spamstr, timestring, str(realspammers)
        session.execute(
            """
            INSERT INTO spamwindowed (channel, message, time, spammers)
            VALUES (%s, %s, %s, %s)
            """,
            (mw[0], spamstr, timestring, realspammers)
        )
