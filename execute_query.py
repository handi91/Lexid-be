from SPARQLWrapper import SPARQLWrapper, JSON
import os
import locale
from datetime import datetime
from dotenv import load_dotenv

def generate_get_query_result():
    load_dotenv()
    sparql = SPARQLWrapper(os.environ.get('URL', 'http://localhost:9999/blazegraph/sparql'))
    locale.setlocale(locale.LC_ALL, "id_ID.UTF-8")
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

    def get_result(query, question_type):
        sparql.setQuery(prefix + query)
        try:
            result = sparql.queryAndConvert()
            answer = ";\n".join(ans['answer']['value'] for ans in result['results']['bindings'] if ans)
            if not answer:
                return "Jawaban tidak ditemukan"
            return answer if question_type not in [2, 3] else datetime.strptime(answer, "%Y-%m-%d").strftime("%d %B %Y")
        except:
            return "error"
    return get_result
