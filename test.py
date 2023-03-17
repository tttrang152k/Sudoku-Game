
#minDomainList = ['CA', 'UT', 'AZ', 'NV', 'NY']
minDomainList = [1, 4, 5, 6, 3, 2, 9]
tempDict = dict.fromkeys(minDomainList, 0)

mrvList = [k for k, v in tempDict.items() if v == 0]

#max_tuple = max(tempDict.items(), key = lambda x:x[1])
#mrvList = [k[0] for k in tempDict.items() if k[1]==max_tuple[1]]


print(tempDict)
print(mrvList)