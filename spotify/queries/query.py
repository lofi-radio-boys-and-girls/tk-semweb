import rdflib
import rdfextras
from SPARQLWrapper import SPARQLWrapper, JSON

prefix_dict = {
    "ex": "http://example.org/data/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dbr": "http://dbpedia.org/resource/",
    "dbp": "http://dbpedia.org/property/",
    "dbo": "http://dbpedia.org/ontology/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dct": "http://purl.org/dc/terms/",
    "dbc": "http://dbpedia.org/page/Category:",
}

def search_song_or_artist(keyword):
    filename = "static/spotify_dataset.ttl"
    rdfextras.registerplugins()

    local_graph = rdflib.Graph()
    local_graph.parse(filename, format='n3')

    # TODO: Handle regex query
    results = local_graph.query("""
        prefix : <http://lofiradioboysandgirls.up.railway.app/data/>
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix xml: <http://www.w3.org/XML/1998/namespace>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix vcard: <http://www.w3.org/2006/vcard/ns#>
        base <http://www.w3.org/2002/07/owl#>

        SELECT distinct ?songLabel (GROUP_CONCAT(DISTINCT ?artistLabel ; separator="_ ") AS ?artistLabel)
        WHERE {
            ?song :artist ?artist .
            ?song :songName ?songLabel .
            ?artist rdfs:label ?artistLabel .

            FILTER(CONTAINS(LCASE(?songLabel), "%s") || REGEX(?songLabel, "(?i).*%s.*") || CONTAINS(LCASE(?artistLabel), "%s") || REGEX(?artistLabel, "(?i).*%s.*"))
            }
        GROUP BY ?songLabel
        ORDER BY ASC (?songLabel)
        """ % (keyword, keyword, keyword, keyword)
    )
    list_of_songs = []
    list_of_artists = []
    for result in results:
        list_of_songs.append(result['songLabel'].toPython())
        list_of_artists.append(result['artistLabel'].toPython())
    return {"songs": list_of_songs, "artists": list_of_artists}

def get_songs_and_artists():
    filename = "static/spotify_dataset.ttl"
    rdfextras.registerplugins()

    local_graph = rdflib.Graph()
    local_graph.parse(filename, format='n3')

    # TODO: Handle regex query
    results = local_graph.query("""
        prefix : <http://lofiradioboysandgirls.up.railway.app/data/>
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix xml: <http://www.w3.org/XML/1998/namespace>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix vcard: <http://www.w3.org/2006/vcard/ns#>
        base <http://www.w3.org/2002/07/owl#>
         SELECT distinct ?songLabel (GROUP_CONCAT(DISTINCT ?artistLabel ; separator="_ ") AS ?artistLabel)
        WHERE {
            ?song :artist ?artist .
            ?song :songName ?songLabel .
            ?artist rdfs:label ?artistLabel .
        }
        GROUP BY ?songLabel
        ORDER BY ASC (?songLabel)
        LIMIT 50
        """
    )
    list_of_songs = []
    list_of_artists = []
    for result in results:
        list_of_songs.append(result['songLabel'].toPython())
        list_of_artists.append(result['artistLabel'].toPython())
    return {"songs": list_of_songs, "artists": list_of_artists}
    
def get_song_detail(songLabel, artistLabel):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>

    SELECT distinct ?songLabel ?comment (GROUP_CONCAT(DISTINCT ?albumsLabel ; separator="_ ") AS ?albumsLabel) (GROUP_CONCAT(DISTINCT ?writersLabel ; separator="_ ") AS ?writersLabel) (GROUP_CONCAT(DISTINCT ?producersLabel ; separator="_ ") AS ?producersLabel)
    WHERE {
        ?song a dbo:Song .
        ?song rdfs:label ?songLabel .

        OPTIONAL {
        ?song dbo:artist ?artist .
        ?artist rdfs:label ?artistLabel .
        }

        OPTIONAL {
            ?song rdfs:comment ?comment .
        }
        
        OPTIONAL {
            ?song dbp:album ?album .
            ?album rdfs:label ?albumsLabel .
        }

        OPTIONAL {
            ?song dbp:writer ?writers .
            ?writers rdfs:label ?writersLabel .
        }
        
        ?song dbo:producer ?producers .
        ?producers rdfs:label ?producersLabel .

        FILTER (langMatches(lang(?artistLabel), "EN") && langMatches(lang(?songLabel), "EN") &&
        langMatches(lang(?albumsLabel), "EN") && langMatches(lang(?writersLabel), "EN") &&
        langMatches(lang(?producersLabel), "EN") && langMatches(lang(?comment), "EN") && 
        (CONTAINS(LCASE(?songLabel), "%s") || REGEX(?songLabel, "(?i).*%s.*")) && (CONTAINS(LCASE(?artistLabel), "%s") || REGEX(?artistLabel, "(?i).*%s.*")))
        }
        GROUP BY ?songLabel ?comment
        """ % (songLabel, songLabel, artistLabel, artistLabel)
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()["results"]["bindings"]

    list_of_song_comments = []
    list_of_album_labels = []
    list_of_writer_labels = []
    list_of_producer_labels = []

    for result in results:
        list_of_song_comments.append(result['comment']['value'])
        list_of_album_labels.append(result['albumsLabel']['value'])
        list_of_writer_labels.append(result['writersLabel']['value'])
        list_of_producer_labels.append(result['producersLabel']['value'])
    return {"comments": list_of_song_comments, "album_labels": list_of_album_labels, "writer_labels": list_of_writer_labels, "producer_labels": list_of_producer_labels}

def check_local_store(songLabel, artistLabel):
    filename = "static/spotify_dataset.ttl"
    rdfextras.registerplugins()

    local_graph = rdflib.Graph()
    local_graph.parse(filename, format='n3')

    # TODO: Handle regex query
    results = local_graph.query("""
        prefix : <http://lofiradioboysandgirls.up.railway.app/data/>
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix xml: <http://www.w3.org/XML/1998/namespace>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix vcard: <http://www.w3.org/2006/vcard/ns#>
        base <http://www.w3.org/2002/07/owl#>
        SELECT distinct (GROUP_CONCAT(DISTINCT ?genreLabel ; separator="; ") AS ?genreLabel) ?songLabel (GROUP_CONCAT(DISTINCT ?artistLabel ; separator="_ ") AS ?artistLabel) ?highestChartingPosition ?popularity ?streams ?energy ?loudness ?tempo (GROUP_CONCAT(DISTINCT ?chordLabel ; separator="_ ") AS ?chordLabel) ?speechiness ?releaseDate
        WHERE {
            ?song :highestChartingPosition ?highestChartingPosition .
            ?song :popularity ?popularity .
            ?song :streams ?streams .
            ?song :hasAttribute ?musicAttributes .
            ?song :chord ?chord .
            ?song :releaseDate ?releaseDate .
            ?song :artist ?artist .
            ?song :genre ?genre .
            ?genre rdfs:label ?genreLabel .
            ?artist rdfs:label ?artistLabel .
            ?chord rdfs:label ?chordLabel
            OPTIONAL {
            ?musicAttributes :energy ?energy .
            }
            OPTIONAL {
            ?musicAttributes :loudness ?loudness .
            }
            OPTIONAL {
            ?musicAttributes :tempo ?tempo .
            }
            OPTIONAL {
                ?musicAttributes :speechiness ?speechiness .
            }
            ?song :songName ?songLabel .
            FILTER (REGEX(?songLabel, "(?i).*%s.*") && REGEX(?artistLabel, "(?i).*%s.*"))
        }
        GROUP BY ?songLabel ?highestChartingPosition ?popularity ?streams ?energy ?loudness ?tempo ?speechiness ?releaseDate
        """ %(songLabel, artistLabel))
    list_of_highest_charting_positions = []
    list_of_popularities = []
    list_of_streams = []
    list_of_energies = []
    list_of_loudness = []
    list_of_tempos = []
    list_of_chord_labels = []
    list_of_speechiness = []
    list_of_release_dates = []
    list_of_song_labels = []
    list_of_artist_labels = []
    list_of_genres = []

    for row in results:
        list_of_highest_charting_positions.append(row["highestChartingPosition"].toPython())
        list_of_popularities.append(row["popularity"].toPython())
        list_of_streams.append(row["streams"].toPython())
        list_of_energies.append(row["energy"].toPython())
        list_of_loudness.append(row["loudness"].toPython())
        list_of_tempos.append(row["tempo"].toPython())
        list_of_chord_labels.append(row["chordLabel"].toPython())
        list_of_speechiness.append(row["speechiness"].toPython())
        list_of_release_dates.append(row["releaseDate"].toPython().strftime("%d %B, %Y"))
        list_of_song_labels.append(row["songLabel"].toPython())
        list_of_artist_labels.append(row["artistLabel"].toPython())
        list_of_genres.append(row["genreLabel"].toPython())
    
    dbpedia_result = get_song_detail(songLabel, artistLabel)
    dict_result = {"charting_positions": list_of_highest_charting_positions, "popularities": list_of_popularities, "streams": list_of_streams, "energies": list_of_energies, "loudness": list_of_loudness,
    "tempos": list_of_tempos, "chord_labels": list_of_chord_labels, "speechiness": list_of_speechiness, "release_dates": list_of_release_dates, "song_labels":list_of_song_labels,
    "artist_labels":list_of_artist_labels, "genres":list_of_genres}
    dict_result.update(dbpedia_result)

    return dict_result
# res = check_local_store("Hasta Que Dios Diga", "Bad Bunny")
# result = get_song_detail("alive and Living", "The Golden Palominos")
# print(result)
# print(res)
# print(get_songs_and_artists())
# result = search_song_or_artist("anue")
# for row in result:
#     print(row)
