from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse

from kafka.structs import TopicPartition

from django.template import loader, Context

import time

import msgpack

import sys
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
chat_template = loader.get_template("spamviewer/spamviewer_user.html")
buffer = ' ' * 1024

def gen_rendered(username=""):
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
                print username
                chat_context  = Context({"username" : username, "spamline" : spamstr, "spammers" : spammers, "buffer" : buffer})

                yield chat_template.render(chat_context)
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
                                print spamdiv, spamstr
                                httpstring = """ <input type="button" onclick="return toggleMe('%s')" value="%s"><br> """ % (spamdiv, spamstr)
                                httpstring += """ <div id="%s" style="display:none"> """ % spamdiv
                                for spamname in spammers:
                                        httpstring += """%s, %s </br>""" %(spamname, spammers[spamname])
                                httpstring += '</div><br>'
                                print spamstr
                                yield httpstring

def twitch_user_page(request, username=""):
        response = StreamingHttpResponse(gen_rendered(username))  
        return response


                                 
