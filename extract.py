import re
import pandas as pd

# with open('/clean.txt', 'r') as f:
#     counter = 0
#     for line in f:
#         match = re.search(r"^\b\w+\b\s+\b\w+\b$", line)
#         if match:
#             counter += 1
#         if counter == 46652:
#             print(line)
#             break

data = pd.read_csv('questions/SampleQ1-Q4.csv')
data_group =  data.sort_values(['type2', 'reg_id'])
d = data_group.groupby('type2').count()
print(d)
# print(data.tail())
# print(data_group.tail())
# data_group.to_csv('SampleQ1-Q4-group.CSV', index=False)