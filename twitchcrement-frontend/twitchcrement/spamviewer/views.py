from django.shortcuts import render
from django.http import HttpResponse

from kafka.structs import TopicPartition

from django.shortcuts import render

import time

import msgpack

# Create your views here.

def spamviewer_index(request): 
        startup_channels = []
        f = open('/home/ubuntu/top500.txt')
        for line in f:
                startup_channels.append(line.rstrip())

	return render(request, 'spamviewer/spamviewer_index.html', {'startup_channels' : startup_channels})

from kafka import KafkaConsumer

def twitch_user_page(request, username=""):

#        return HttpResponse("This is the page for %s" % username)
        consumer = KafkaConsumer('spammessage',
                                 auto_offset_reset='latest',
                                 enable_auto_commit=True,
                                 bootstrap_servers=['ec2-34-197-212-254.compute-1.amazonaws.com:9092']
#                                 value_deserializer=msgpack.unpackb
                         )
#        x = consumer.poll(100)
#        consumer.seek_to_end()
        while True:
                spamlist = []
                channelname = '#%s' % username
                for message in consumer:                 
                        mw = message.value.split(' ')
                        if mw[0] == channelname:
                                mwlen = len(mw)
                                nspammers = (mw[mwlen-1])
                                if nspammers != "":
                                        smw = mw[1:(mwlen-3-int(nspammers))]
                                        spamstr = ' '.join(smw) + ', ' + mw[mwlen-2 -int(nspammers)]
                                        realspammers = (int(nspammers)/2)+1
                                        spammers = {}
                                        for n in range(1,realspammers):
                                                spamname = mw[mwlen-1-(n*2)]
                                                spamcount = mw[mwlen-(n*2)]
                                                spammers[spamname] = spamcount
                                        spamlist.append(spamstr)
                                        if len(spamlist) == 1:
                                                httpstring = ""
                                                for spamline in spamlist:
                                                        httpstring += "Spam Message:<br/>"
                                                        httpstring += spamline
                                                        httpstring += "<br/>"
                                                httpstring += "<br/>Spammers:<br/><br/>"
                                                for spammer in spammers:
                                                        httpstring += "%s, %s<br/>" % (spammer, spammers[spammer] )
                                                return render(request, "spamviewer/spamviewer_user.html", {"username" : username, "spamline" : spamline, "spammers" : spammers}) 


                                 
