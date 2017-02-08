package com.lotusprince.twitchcrement

import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer09	
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer09
import org.apache.flink.streaming.util.serialization.SimpleStringSchema
import org.apache.flink.streaming.util.serialization.TypeInformationSerializationSchema
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.contrib.streaming.DataStreamUtils
import scala.collection.JavaConverters._

import scala.collection.mutable.Map

import java.util.Properties

object KafkaConnector{

       def InterpretSpamMessage(m1:String): Tuple5[String, Int, Int, String, Int] = {
       	   var mTup: Tuple5[String, Int, Int, String, Int] = ("", 0, 0, "", 0)
	   
	   var arrayofmessage = m1.split(" ")

	   val term5 = arrayofmessage.last.toInt
	   val term4 = arrayofmessage.dropRight(1).takeRight(term5).mkString(" ")
	   val term3 = arrayofmessage.dropRight(term5+1).last.toInt
	   val term2 = arrayofmessage.dropRight(term5+2).last.toInt
	   val term1 = arrayofmessage.dropRight(term5+3).mkString(" ")
	   
	   mTup = (term1, term2, term3, term4, term5)
	   
	   return mTup
	   }


       def CombineTuples(t1:Tuple5[String, Int, Int, String, Int], t2:Tuple5[String, Int, Int, String, Int]): Tuple5[String, Int, Int, String, Int] = {
       	   var rTup:Tuple5[String, Int, Int, String, Int] = ("",0,0,"", 0)
	   var suser1 = t1._4.split(" ")
	   var suser2 = t2._4.split(" ")
	   if (t1._3 == t2._3 && t1._2 == 0 && t2._2 == 0){
	        rTup = (t1._1, 0, 1, t1._4, suser1.length)
	   }
	   else if((t1._2+t1._3) == (t2._2 + t2._3) && ((t1._2 + t1._3) != 1)){
                rTup = (t1._1, math.min(t1._2, t2._2), math.max(t1._3, t2._3), t2._4, t2._5)
           }
	   else if (t1._5 == 2){
		var suser3 = Array[String]()
                if(suser2.contains(suser1(0))){
			var nspam1 = suser2(suser2.indexOf(suser1(0))+1).toInt
			var nspam2 = suser1(1).toInt
                        var nspam = math.max(nspam1, nspam2)+1
			suser3 = suser2
                        suser3(suser2.indexOf(suser1(0))+1) = nspam.toString
                }
		else{
			suser3 = suser2 ++ suser1
		}
		rTup = (t1._1, t1._2+t2._2, math.max(t1._3, t2._3), suser3.mkString(" "), suser3.length)
	   }
	   else if (t2._5 == 2){
	   	var suser3 = Array[String]()
	   	if(suser1.contains(suser2(0))){
			var nspam1 = suser1(suser1.indexOf(suser2(0))+1).toInt
			var nspam2 = suser2(1).toInt
                        var nspam = math.max(nspam1, nspam2)+1
			suser3 = suser1
                        suser1(suser3.indexOf(suser2(0))+1) = nspam.toString

		}
                else{
                        suser3 = suser1 ++ suser2
                }
		rTup = (t1._1, t1._2+t2._2, math.max(t1._3, t2._3), suser3.mkString(" "), suser3.length)          
	   }
	   else{
		rTup = t2
	   } 
	   println("These tuples")
	   println(t1.productIterator.mkString(" "))
	   println(t2.productIterator.mkString(" "))
	   println(rTup.productIterator.mkString(" "))
	   return rTup
       }

       def main(args: Array[String]) {
       	          
	   
	   
       	   val env = StreamExecutionEnvironment.getExecutionEnvironment
	   
	   val p = new Properties

	   p.setProperty("bootstrap.servers", "ec2-34-197-212-254.compute-1.amazonaws.com:9092")
	   p.setProperty("zookeeper.connect", "ec2-34-197-212-254.compute-1.amazonaws.com:2181")
	   p.setProperty("group.id", "twitchcrement")
	   p.setProperty("consumer.id", "flitch")

	   println("Streaming")

	   val stream = env.addSource(new FlinkKafkaConsumer09[String]("chatmessage", new SimpleStringSchema(), p))
	   val toRemove = "�".toSet

/** All messages */
	   val streamMessages =stream
	       .map { w => w.filterNot(toRemove) }
	       .map { w => ((w.split(" ")(w.indexOf("channel")+1).toString() + " " + w.split(" ").drop(6).mkString(" ")), 1, 0, (w.split(" ")(4).toString() + " 1"), 2)}


/** Acquire list of most recent spam terms */
	   val SpamStream = env.addSource(new FlinkKafkaConsumer09[String]("spammessage", new SimpleStringSchema(), p))

/** Process Spam terms */
	   val processedSpamStream = SpamStream
	       .map{ w => InterpretSpamMessage(w) }
	       
	   val streamWithSpam = streamMessages.union(processedSpamStream)
	       .keyBy(0)
	       .reduce((left, right) => CombineTuples(left, right))

	   val printSpamStream = processedSpamStream
	       .map {w => w.productIterator.mkString(" ") }


/** Filtered messages that occur repeatedly */

           val windowSpamCounts = streamWithSpam
               .keyBy(0)
               .timeWindow(Time.seconds(10))
	       .maxBy(1)
               .filter{ w => w._2 > 1 }  
	       .map { w => ( w._1, 0, w._3+w._2, w._4, w._5) }
               .map { w => w.productIterator.mkString(" ") }

/**	   streamMessages.map{ w => w.productIterator.mkString(" ") }.print.setParallelism(1) */

	   windowSpamCounts.print().setParallelism(1) 

	   windowSpamCounts.addSink(new FlinkKafkaProducer09[String]("ec2-34-197-212-254.compute-1.amazonaws.com:9092", "spammessage", new SimpleStringSchema()))

	   env.execute("KafkaConnector")
       }

}
	       
