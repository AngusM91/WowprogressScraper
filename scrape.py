from bs4 import BeautifulSoup
import requests

url = "https://www.wowprogress.com/gearscore/?lfg=1&raids_week=2&lang=en"
ourServer = "twisting-nether"
ourClass = "deathknight"
ourSpecs = "dd"

fileName = ourClass + "_" + ourSpecs + ".txt"
f = open(fileName, "w")

base = "https://www.wowprogress.com"
key = "/character/eu/"
nextkey = "/gearscore/char_rating/next/"
transferKey = "Yes, ready to transfer"
list = []

print("Searching for recruits now...")

for x in range(35):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,'html.parser')
    
    for link in soup.find_all('a'):
        target = link.get('href')
        if nextkey in target:
            url = base + target
        if key in target:
            list.append(target)

msg = "Found " + str(len(list)) + " potential recruits."
print(msg)

index = 1
finalList = []
for item in list:
    msg = "Getting info for recruit " + str(index) + "/" + str(len(list))
    print(msg, end='\r')
    index+=1;
    
    url = base + item
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,'html.parser')
    
    needsTransfer = True
    if item in ourServer:
        needsTransfer = False
    
    for info in soup.find_all('i'):
        if ourClass in info.get_text():
            for spec in soup.find_all('strong'):
                if ourSpecs in spec.get_text():
                    if needsTransfer:
                        for transferStatus in soup.find_all('span'):
                            if transferKey in transferStatus.get_text():
                               finalList.append(url)
                    else:
                        finalList.append(url)
                        
for finalItem in finalList:
    f.write(finalItem)
    f.write('\n')
msg = str(len(finalList)) + " recruit(s) found and written to file."
print(msg)
    
f.close()
