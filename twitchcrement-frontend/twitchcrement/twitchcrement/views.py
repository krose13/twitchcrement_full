from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse


def index(request):
#        return render(request, 'spamviewer/spamviewer_index.html', {'startup_channels' : startup_channels})
	return render(request, 'twitchcrement/index.html', {})

