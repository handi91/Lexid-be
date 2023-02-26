from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from mapping import mapping

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
sparql.setReturnFormat(JSON)

def get_result(question):
    query = mapping(question)
    sparql.setQuery(query)
    try:
        result = sparql.queryAndConvert()
        answer = ";\n".join(ans['answer']['value'] for ans in result['results']['bindings'])
        return answer
    except:
        return "error"

df = pd.read_csv("sample-question.csv")
for j in df['Q']:
    print(j)
    print(get_result(j))
# print(get_result("Kapan Peraturan Menteri Kesehatan Republik Indonesia Nomor 49 Tahun 2019 ditetapkan?"))
