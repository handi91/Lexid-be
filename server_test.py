from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
sparql.setReturnFormat(JSON)

# gets the first 3 geological ages
# from a Geological Timescale database,
# via a SPARQL endpoint
sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix dbo: <http://dbpedia.org/ontology/> 
    prefix dct: <http://purl.org/dc/terms/> 
    prefix owl: <http://www.w3.org/2002/07/owl#> 
    prefix wd: <https://www.wikidata.org/wiki/> 
    prefix lexid-s: <https://w3id.org/lex-id/schema/> 
    prefix lexid: <https://w3id.org/lex-id/data/>

    SELECT distinct (coalesce(?label, ?ans) as ?answer)
    WHERE {
        ?LegalDocument a lexid-s:LegalDocument ;
            lexid-s:hasEnactionOfficial ?ans ;
            rdfs:label "Peraturan Daerah Provinsi Jambi Nomor 11 Tahun 2009"^^xsd:string .
        OPTIONAL { ?ans rdfs:label ?label .}
    }
    """
)

try:
    ret = sparql.queryAndConvert()
    print(ret)
    # for r in ret["results"]["bindings"]:
    #     print(r)
except Exception as e:
    print(e)