from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv

def generate_get_query_result():
    load_dotenv()
    sparql = SPARQLWrapper(os.environ.get('URL', 'http://localhost:9999/blazegraph/sparql'))
    prefix = '''
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX dbo: <http://dbpedia.org/ontology/> 
    PREFIX dct: <http://purl.org/dc/terms/> 
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX wd: <https://www.wikidata.org/wiki/> 
    PREFIX lexid-s: <https://w3id.org/lex-id/schema/> 
    PREFIX lexid: <https://w3id.org/lex-id/data/> 
    '''
    sparql.setReturnFormat(JSON)

    def get_result(query):
        sparql.setQuery(prefix + query)
        try:
            result = sparql.queryAndConvert()
            answer = ";\n".join(ans['answer']['value'] for ans in result['results']['bindings'])
            if not answer:
                answer = "Jawaban tidak ditemukan"
            return answer
        except:
            return "error"
    return get_result