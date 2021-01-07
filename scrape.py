from bs4 import BeautifulSoup
import requests

#MODIFY YOUR INFO/REQUIREMENTS#####
ourServer = "twisting-nether"
ourClass = "priest"
ourSpecs = "healer"
ourRaidsPerWeek = "2"
updateThresholdDays = 7
pagesToCheck = 10
###################################

url = "https://www.wowprogress.com/gearscore/class." + ourClass + "?lfg=1&raids_week=" + ourRaidsPerWeek + "&lang=en"

fileName = ourClass + "_" + ourSpecs + ".txt"
f = open(fileName, "w")

base = "https://www.wowprogress.com"
key = "/character/eu/"
nextkey = "/gearscore/char_rating/next/"
transferKey = "Yes, ready to transfer"
timeKey = "day ago"
timeKey2 = "days ago"
list = []

print("Searching for recruits now...")

for x in range(pagesToCheck):
    msg = "Checking page " + str(x) + "/" + str(pagesToCheck)
    print(msg, end='\r')
    
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,'html.parser')
    
    for link in soup.find_all('a'):
        target = link.get('href')
        if nextkey in target:
            url = base + target
    
    for tr in soup.find('table').find_all('tr'):
        for link in tr.find_all('a'):
            target = link.get('href')
            if nextkey in target:
                url = base + target
            if key in target:
                for spanText in tr.find_all('span'):
                    if timeKey in spanText.get_text() or timeKey2 in spanText.get_text():
                        timeText = spanText.get_text()
                        theTime = timeText[:timeText.find(' ')]
                        if int(theTime) < updateThresholdDays:
                            list.append(target)
                    else:
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
    if ourServer in item:
        needsTransfer = False
    
    for strongText in soup.find_all('strong'):
        if ourSpecs in strongText.get_text():
            if needsTransfer:
                for spanText in soup.find_all('span'):
                    if transferKey in spanText.get_text():
                       finalList.append(url)
            else:
                finalList.append(url)
                        
for finalItem in finalList:
    f.write(finalItem)
    f.write('\n')
msg = str(len(finalList)) + " recruit(s) found and written to file."
print(msg)
    
f.close()
