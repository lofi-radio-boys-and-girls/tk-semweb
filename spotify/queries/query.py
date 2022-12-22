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
         SELECT distinct ?songLabel ?artistLabel
        WHERE {
            ?song :artist ?artist .
            ?song :songName ?songLabel .
            ?artist rdfs:label ?artistLabel .
        }
        LIMIT 20
        """
    )
    list_of_songs = []
    list_of_artists = []
    for result in results:
        list_of_songs.append(result[0].toPython())
        list_of_artists.append(result[1].toPython())
    return {"songs": list_of_songs, "artists": list_of_artists}
    

def get_song_detail(songLabel, artistLabel):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    songLabel = f"\"{songLabel}\""
    artistLabel = f"\"{artistLabel}\""
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    SELECT distinct ?songLabel ?comment (GROUP_CONCAT(?artistLabel ; separator="; ") AS ?artistLabel) (GROUP_CONCAT(?albumsLabel ; separator="; ") AS ?albumsLabel) (GROUP_CONCAT(?writersLabel ; separator="; ") AS ?writersLabel)
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
        langMatches(lang(?producersLabel), "EN") && langMatches(lang(?comment), "EN") && ?songLabel = """ + songLabel + "@en" + "&& ?artistLabel = " + artistLabel + "@en)}" 
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
    return {"songs": list_of_song_labels, "comments": list_of_song_comments, "artist labels": list_of_artist_labels, "album labels": list_of_album_labels, "writer labels": list_of_writer_labels}
# print(get_song_detail("What About Now (Daughtry song)", "Daughtry (band)"))

def check_local_store(keyword):
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

        SELECT ?p ?o
        WHERE {
            ?song :songName "%s" .
            ?song ?p ?o .
        }
        """ % keyword)

    return results
res = check_local_store("Freaks")
