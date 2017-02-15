from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse

from kafka.structs import TopicPartition

from django.template import loader, Context

import time

import msgpack

import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

# Create your views here.

def spamviewer_index(request): 
        startup_channels = []
        f = open('/home/ubuntu/top500.txt')
	startup_channels.append("twitchplayspokemon")
        for line in f:
                startup_channels.append(line.rstrip())

	return render(request, 'spamviewer/spamviewer_index.html', {'startup_channels' : startup_channels})



from kafka import KafkaConsumer
user_template = loader.get_template("spamviewer/spamviewer_user.html")
buffer = ' ' * 1024

def twitch_user_page(request, username=""):
        user_context = Context({"username" : username})
#        response = StreamingHttpResponse(spam_rendered(username))
        return HttpResponse(user_template.render(user_context))


def spam_rendered(username=""):
        consumer = KafkaConsumer('spammessage',
                                 auto_offset_reset='latest',
                                 enable_auto_commit=True,
                                 bootstrap_servers=[os.environ['KAFKAPORT']]
                         )
        
        while True:
                spamlist = []
                spamstr = ""
                channelname = '#%s' % username
                spammers = {}
                mydiv = 0
                for message in consumer:
                        mw = message.value.split(' ')
                        if mw[0] == channelname:
                                mwlen = len(mw)
                                nspammers = (mw[mwlen-1])
                                smw = mw[1:(mwlen-3-int(nspammers))]
                                spamstr = ' '.join(smw) + ', ' + mw[mwlen-2 -int(nspammers)]
                                realspammers = (int(nspammers)/2)+1
                                spammers = {}
                                spamdiv = "%s_%i" % (username, mydiv)
                                mydiv = mydiv + 1
                                for n in range(1,realspammers):
                                        spamname = mw[mwlen-1-(n*2)]
                                        spamcount = mw[mwlen-(n*2)]
                                        spammers[spamname] = spamcount
                                spamlist.append(spamstr)
                                httpstring = """ <input type="button" onclick="return toggleMe('%s')" value="%s"><br> """ % (spamdiv, spamstr)
                                httpstring += """ <div id="%s" style="display:none"> """ % spamdiv
                                for spamname in spammers:
                                        httpstring += """%s, %s </br>""" %(spamname, spammers[spamname])
                                httpstring += '</div><br>'
                                yield httpstring

def chat_rendered(username=""):
        consumer = KafkaConsumer('chatmessage',
                                 auto_offset_reset='latest',
                                 enable_auto_commit=True,
                                 bootstrap_servers=[os.environ['KAFKAPORT']],
                                 value_deserializer=msgpack.unpackb
                         )
        while True:
                for message in consumer:
                        channelname = '#%s' % username
                        if message.value[' channel '] == channelname:
                                httpstring = """<p> <i>%s</i> : %s </p>""" % (message.value[' username '], message.value[' message '])
                                yield httpstring



def twitch_user_spam(request, username=""):
        response = StreamingHttpResponse(spam_rendered(username))  
        return response


                                 
def twitch_user_chat(request, username=""):
        response = StreamingHttpResponse(chat_rendered(username))
        return response
