from django.shortcuts import render

from spotify.queries.query import *


def index(request):
    return render(request, 'index.html')


def search(request):
    keyword = request.GET['keyword']
    songs_and_artists = get_songs_and_artists()

    if keyword == '':
        data = dict()
        data['songs_and_artists'] = zip(songs_and_artists['songs'], songs_and_artists['artists'])
        data['keyword'] = 'Don\'t Know Where to Start? Try Checking These Songs Out!'
    else:
        result = search_song_or_artist(keyword)
        data = {
            'keyword': keyword,
            'songs_and_artists': zip(result['songs'], result['artists'])
        }

    return render(request, 'search.html', data)


def detail(request):
    context = {
        'data' : get_song_detail(request.GET['song'],request.GET['artist']),
        'attr' : check_local_store(request.GET['song'],request.GET['artist'].replace('_ ', '|'))
    }
    # print(request.GET['artist'].replace('_ ', '|'))
    print(context['data'],context['attr'])
    return render(request, 'detailSong.html', context)


