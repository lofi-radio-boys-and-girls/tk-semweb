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

        if len(result['songs']) == 0:
            data['message'] = "Your favorite song or artist still got a long way to reach the top, try other ones!"

    return render(request, 'search.html', data)


def detail(request):
    local_store = check_local_store(request.GET['song'],request.GET['artist'].replace('_ ', '|'))
    # print(local_store['chord_labels'][0].replace('_',','))
    context = {
            # 'data' : get_song_detail(request.GET['song'],request.GET['artist']),
            'artist': request.GET['artist'].replace('_ ', ', '),
            'attr' : local_store,
        }
    if len(local_store['chord_labels']) != 0:
        context['chord'] = local_store['chord_labels'][0].replace('_',',')
    if len(local_store['comments']) != 0:
        context['comment'] = local_store['comments'][0]
    if len(local_store['album_labels']) != 0:
        context['album_labels'] = local_store['album_labels'][0].replace('_',',')
    if len(local_store['writer_labels']) != 0:
        context['writer_labels'] = local_store['writer_labels'][0].replace('_',',')
    if len(local_store['producer_labels']) != 0:
        context['producer_labels'] = local_store['producer_labels'][0].replace('_',',')
    # print(request.GET['artist'].replace('_ ', '|'))
    print(context['attr'])
    return render(request, 'detailSong.html', context)


