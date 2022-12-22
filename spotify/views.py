from django.shortcuts import render

from spotify.queries.query import get_songs_and_artists, get_song_detail, check_local_store


def index(request):
    return render(request, 'index.html')


def search(request):
    context = {
        'keyword': request.GET['keyword'],
    }
    return render(request, 'search.html', context)


def detail(request):
    context = {
        'data' : get_song_detail(request.GET['song'],request.GET['artist']),
        'attr' : check_local_store(request.GET['song'],request.GET['artist'])
    }
    # print(context['data'],context['attr'])
    return render(request, 'detailSong.html', context)

    
