# Twitchcrement - making spam fun for everyone

Twichcrement [(twitchcrement.us)] (http://twitchcrement.us:8000) is a platform for compressing and analyzing spam from the 
twitch.tv chat client.  Similar spam messages are counted on a by-channel basis and a list of unique users per spam event is stored.
Some historical tracking of spam events is also available.

## Ingestion

The top 500 channels are consumed by an adapted version of a known twitch chat bot [Roboraj](https://github.com/aidanrwt/twitch-bot)
and has been adapted to funnel those messages into the python KafkaConsumer class under the "chatmessage" topic.  Messages
are serialized using the msgpack schema.  Messages contain the channel, message, and username of the chatter.
The twitch bot is initiated using the serve.py script.  Joining 500 chat channels takesroughly 50 seconds due to twitch chat 
API limits.  This list of 500 channels updates dynamically once per hour.

## Processing

Messages are streamed through Kafka and processed by Apache Flink into spam topics every 10 seconds.  This input is then used
to further filter spam topics and determine which are still active by sending the spam messages back into Kafka with the 
"spammessage" topic and consuming them again in twitchcrement.  This prevents the need to maintain a list of active spam topics
in memory or in a database sink.

## Consumers

The spam products are consumed by a pair of apps in the django framework in twitchcrement-frontend.  A Cassandra database is 
populated with a time ordered stream of recorded spam events keyed by spam message.  This database can be queried in 
the spamsearcherapp to return a historical list of channels where a given spam message has been observed.

The spamviewer app provides a list of available channels (chosen from the top 500 active twitch channels by periodically
querying the twitch HTTP API).  Upon selection twitchcrement displays the channel selected, as well as a stream of 
observed spam messages from that channel and a stream of unfiltered chat messages for comparison. 
