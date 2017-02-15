from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse

from cassandra.cluster import Cluster

from django.template import loader, Context

import os

# Create your views here.

def index(request):
        return render(request, 'spamsearcher/index.html', {})

def search(request):
	cluster = Cluster([os.environ['CASSANDRA_ADDRESS']], port=os.environ['CASSANDRA_PORT'])
	session = cluster.connect()
	session.set_keyspace('spamevents')

        query = request.GET['q']

        query_results = session.execute(
                """
                SELECT * FROM spamwindowed WHERE message=%s
                """,
                (query,)
        )

        t = loader.get_template('spamsearcher/results.html')
        c = Context({'query': query, 'query_results': query_results,})

        

        return HttpResponse(t.render(c))

