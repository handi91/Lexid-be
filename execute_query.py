from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv

def generate_get_query_result():
    load_dotenv()
    sparql = SPARQLWrapper(os.environ.get('URL', 'http://localhost:9999/blazegraph/sparql'))
    sparql.setReturnFormat(JSON)

    def get_result(query):
        sparql.setQuery(query)
        try:
            result = sparql.queryAndConvert()
            answer = ";\n".join(ans['answer']['value'] for ans in result['results']['bindings'])
            if not answer:
                answer = "Jawaban tidak ditemukan"
            return answer
        except:
            return "error"
    return get_result