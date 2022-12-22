from django.shortcuts import render

from spotify.queries.query import get_songs_and_artists, search_song_or_artist


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
        'artist': request.GET['artist'],
        'song': request.GET['song'],
    }
    print(request.GET)
    return render(request, 'detail.html', context)
