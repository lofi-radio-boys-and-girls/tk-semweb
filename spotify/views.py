from django.shortcuts import render

from spotify.queries.query import get_songs_and_artists


def index(request):
    return render(request, 'index.html')


def search(request):
    context = {
        'keyword': request.GET['keyword'],
    }
    return render(request, 'search.html', context)


def detail(request, song_by_artis):
    context = {
        'keyword': song_by_artis,
    }
    return render(request, 'detail.html', context)
