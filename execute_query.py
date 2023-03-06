from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

def generate_get_query_result():
  sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
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

# get_result = generate_get_query_result
# df = pd.read_csv("SampleQ1-Q5.csv")
# with open('q-a.txt', "w") as f:
#   for j in df['Q']:
#       f.write(j+"\n")
#       f.write(get_result(j)+"\n")
# print(get_result("Kapan Peraturan Menteri Kesehatan Republik Indonesia Nomor 49 Tahun 2019 ditetapkan?"))
