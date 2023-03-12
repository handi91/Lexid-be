from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process
import pandas as pd
print(rapidfuzz_fuzz.ratio("", "Apakah peraturan"))

df = pd.read_csv('other/Question-Head-And-Tail.csv', keep_default_na=False)

for j in df['tail']:
    if j != '':
        print(True)