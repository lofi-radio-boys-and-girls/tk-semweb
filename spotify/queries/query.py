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
         SELECT distinct ?songLabel (GROUP_CONCAT(DISTINCT ?artistLabel ; separator="; ") AS ?artistLabel)
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
    songLabel = f"\"{songLabel}\""
    artistLabel = f"\"{artistLabel}\""
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    SELECT distinct ?songLabel ?comment (GROUP_CONCAT(DISTINCT ?artistLabel ; separator="; ") AS ?artistLabel) (GROUP_CONCAT(DISTINCT ?albumsLabel ; separator="; ") AS ?albumsLabel) (GROUP_CONCAT(DISTINCT ?writersLabel ; separator="; ") AS ?writersLabel)
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
        langMatches(lang(?producersLabel), "EN") && langMatches(lang(?comment), "EN") && ?songLabel = """ + songLabel + "@en" + "&& ?artistLabel = " + artistLabel + "@en)} GROUP BY ?songLabel ?comment"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()["results"]["bindings"]

    list_of_song_labels = []
    list_of_song_comments = []
    list_of_artist_labels = []
    list_of_album_labels = []
    list_of_writer_labels = []

    for result in results:
        list_of_song_labels.append(result['songLabel']['value'])
        list_of_song_comments.append(result['comment']['value'])
        list_of_artist_labels.append(result['artistLabel']['value'])
        list_of_album_labels.append(result['albumsLabel']['value'])
        list_of_writer_labels.append(result['writersLabel']['value'])
    return {"songs": list_of_song_labels, "comments": list_of_song_comments, "artist_labels": list_of_artist_labels, "album_labels": list_of_album_labels, "writer_labels": list_of_writer_labels}
# print(get_song_detail("What About Now (Daughtry song)", "Daughtry (band)"))

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
        SELECT distinct ?songLabel ?artistLabel ?highestChartingPosition ?popularity ?streams ?energy ?loudness ?tempo (GROUP_CONCAT(DISTINCT ?chordLabel ; separator="; ") AS ?chordLabel) ?speechiness ?releaseDate
        WHERE {
            ?song :highestChartingPosition ?highestChartingPosition .
            ?song :popularity ?popularity .
            ?song :streams ?streams .
            ?song :hasAttribute ?musicAttributes .
            ?song :chord ?chord .
            ?song :releaseDate ?releaseDate .
            ?song :artist ?artist .
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
        GROUP BY ?highestChartingPosition ?popularity ?streams ?energy ?loudness ?tempo ?speechiness ?releaseDate
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
    
    return {"charting_positions": list_of_highest_charting_positions, "popularities": list_of_popularities, "streams": list_of_streams, "energies": list_of_energies, "loudness": list_of_loudness, "tempos": list_of_tempos, "chord_labels": list_of_chord_labels, "speechiness": list_of_speechiness, "release_dates": list_of_release_dates, "song_label":list_of_song_labels, "artist_label":list_of_artist_labels}

res = check_local_store("Hasta Que Dios Diga", "anuel AA")
print(res)
# print(get_songs_and_artists())
