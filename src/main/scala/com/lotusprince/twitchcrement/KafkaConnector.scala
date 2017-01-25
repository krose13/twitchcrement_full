package com.lotusprince.twitchcrement

import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer08	
import org.apache.flink.streaming.util.serialization.SimpleStringSchema

import java.util.Properties

object KafkaConnector{
       def main(args: Array[String]) {
       	   val env = StreamExecutionEnvironment.getExecutionEnvironment
	   
	   val p = new Properties

	   p.setProperty("bootstrap.servers", "ec2-34-197-212-254.compute-1.amazonaws.com:9092")
	   p.setProperty("zookeeper.connect", "ec2-34-197-212-254.compute-1.amazonaws.com:2181")
	   p.setProperty("group.id", "twitchcrement")
	   p.setProperty("consumer.id", "flitch")

	   println("Streaming")

	   val stream = env.addSource(new FlinkKafkaConsumer08[String]("chatmessage", new SimpleStringSchema(), p))
	   stream.print
	   env.execute("KafkaConnector")
       }
}
	       
