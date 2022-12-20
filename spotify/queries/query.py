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
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(
    """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    SELECT distinct ?songLabel ?artistLabel
    WHERE {
        ?song a dbo:Song .
        ?song dbo:artist ?artist .
        ?song rdfs:label ?songLabel .
        ?artist rdfs:label ?artistLabel .
        FILTER (langMatches(lang(?artistLabel), "EN") && langMatches(lang(?artistLabel), "EN"))
    }
    ORDER BY ASC(?song)
    LIMIT 20
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()["results"]["bindings"]

    list_of_songs = []
    list_of_artists = []
    for result in results:
        list_of_songs.append(result['songLabel']['value'])
        list_of_artists.append(result['artistLabel']['value'])
    return {"songs": list_of_songs, "artists": list_of_artists}

def get_song_detail(keyword):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    keyword = f"\"{keyword}\""
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    SELECT distinct ?songLabel ?comment ?artistLabel ?albumLabel ?writersLabel
    WHERE {
        ?song a dbo:Song .
        ?song dbo:artist ?artist .
        ?song rdfs:comment ?comment .
        ?song dbp:album ?album .
        ?song dbp:writer ?writers .
        ?song dbo:producer ?producers .

        ?producers rdfs:label ?producersLabel .
        ?writers rdfs:label ?writersLabel .
        ?album rdfs:label ?albumLabel .
        ?song rdfs:label ?songLabel .
        ?artist rdfs:label ?artistLabel .
        FILTER (langMatches(lang(?artistLabel), "EN") && langMatches(lang(?songLabel), "EN") &&
        langMatches(lang(?albumLabel), "EN") && langMatches(lang(?writersLabel), "EN") &&
        langMatches(lang(?producersLabel), "EN") && langMatches(lang(?comment), "EN") && ?songLabel = """ + keyword + "@en)}"
    print(query)
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
        list_of_album_labels.append(result['albumLabel']['value'])
        list_of_writer_labels.append(result['writersLabel']['value'])
    return {"songs": list_of_song_labels, "comments": list_of_song_comments, "artist labels": list_of_artist_labels, "album labels": list_of_album_labels, "writer labels": list_of_writer_labels}

# print(get_songs_and_artists())
# print(get_song_detail("All Dressed Up for School"))

# Problem: Kalo ngasilin 2 entity, bingung milih yang mana secara ini kan milihnya berdasarkan label doang :O