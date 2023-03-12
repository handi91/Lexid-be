import pandas as pd
import ast
import tracemalloc
import random

# title_df = pd.read_csv('valid-document-title.csv')

# titles = []
# jenis_peraturan = []
# nomor_tahun_peraturan = []
# for title in title_df['Peraturan']:
#     title_words = title.split()
#     nomor_tahun = ""
#     jenis = ""
#     if title_words[-1].isnumeric() and title_words[-3].isnumeric():
#         nomor_tahun = " ".join(title_words[-4:])
#         jenis = " ".join(title_words[:-4])
#         titles.append(title)
#         jenis_peraturan.append(jenis)
#         nomor_tahun_peraturan.append(nomor_tahun)
#     elif title_words[-1].isnumeric():
#         nomor_tahun = " ".join(title_words[-2:])
#         jenis = " ".join(title_words[:-2])
#         titles.append(title)
#         jenis_peraturan.append(jenis)
#         nomor_tahun_peraturan.append(nomor_tahun)
#     else:
#         print(title)

# data_parse = pd.DataFrame({
#     "judul": titles,
#     "jenis": jenis_peraturan,
#     "nomor_tahun": nomor_tahun_peraturan
# })

# data_parse.to_csv("peraturan-parsing.csv", index=False)

# legal_parse_df = pd.read_csv("peraturan-parsing.csv")
# legal_type = legal_parse_df['jenis'].unique()
# nomor_tahun_variaton = []
# for type in legal_type:
#     nomor_tahun = legal_parse_df[legal_parse_df['jenis'] == type]['nomor_tahun']
#     nomor_tahun_list = list(nomor_tahun)
#     random.shuffle(nomor_tahun_list)
#     nomor_tahun_variaton.append(nomor_tahun_list)
# legal_type_list = list(legal_type)
# peraturan_grouping = pd.DataFrame({"tipe": legal_type_list, "nomor_tahun": nomor_tahun_variaton})

# peraturan_grouping.to_csv('peraturan-grouping.csv', index=False)

# tracemalloc.start()
# test = pd.read_csv('peraturan-grouping.csv')
# test2 = test.set_index('tipe')
# print(test)
# print(test2['nomor_tahun']['Undang-Undang Republik Indonesia'])
# tmp = {}
# for j in test['tipe']:
#     for i in test[test['tipe']==j]['nomor_tahun']:
#         tmp[j] = ast.literal_eval(i)
    # break

# print(tmp)
