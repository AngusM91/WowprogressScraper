import aiohttp
from bs4 import BeautifulSoup
#import pandas as pd
import requests
import asyncio

#MODIFY YOUR INFO/REQUIREMENTS#####
   
ourServer = "twisting-nether"
ourRaidsPerWeek = "2"
updateThresholdDays = 10
pagesToCheck = 10

###################################
#KEYS##############################
urlBase = "https://www.wowprogress.com"
key = "/character/eu/"
nextkey = "/gearscore/char_rating/next/"
transferKey = "Yes, ready to transfer"
timeKey = "day ago"
timeKey2 = "days ago"
###################################

print("\n\n Class & spec combinations available: \n ~~~~~~~~~~~~~~~~~~\n deathknight - dd, tank \n demon hunter - dd, tank \n druid - balance, restoration, feral dd, feral tank \n hunter - beastmastery, marksmanship, survival \n mage - arcane, fire, frost \n monk - healer, dd, tank \n paladin - holy, protection, retribution \n priest - healer, dd \n rogue - assassination, outlaw, subtlety \n shaman - elemental, enhancement, restoration \n warlock - affliction, demonology, destruction \n warrior - dd, protection \n ~~~~~~~~~~~~~~~~~~\n")

ourClass = input("Class: ")
ourSpecs = input("Specs: ")
minGearscore = input("Min Gearscore: ")
minKills = input("Min mythic kills this tier: ")


async def fetch(session, url):
        try:
            async with session.get(url) as response:
                text = await response.text()
                return text, url
        except Exception as e:
            print(str(e))

async def main():
   
    url = urlBase + "/gearscore/class." + ourClass + "?lfg=1&raids_week=" + ourRaidsPerWeek + "&lang=en"
    theList = []

    print("Searching for recruits now...")

    ##Check the class summary pages to gather urls for all characters under the search parameters
    for x in range(pagesToCheck):
        msg = "Checking page " + str(x) + "/" + str(pagesToCheck)
        print(msg, end='\r')
        
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data,'html.parser')
        
        for link in soup.find_all('a'):
            target = link.get('href')
            if nextkey in target:
                url = urlBase + target
        
        for tr in soup.find('table').find_all('tr'):
            for link in tr.find_all('a'):
                target = link.get('href')
                if nextkey in target:
                    url = urlBase + target
                if key in target:
                    for spanText in tr.find_all('span'):
                        if timeKey in spanText.get_text() or timeKey2 in spanText.get_text():
                            timeText = spanText.get_text()
                            theTime = timeText[:timeText.find(' ')]
                            if int(theTime) < updateThresholdDays:
                                theList.append(target)
                        else:
                            theList.append(target)
       

    msg = "Found " + str(len(theList)) + " potential recruits."
    print(msg)
    
    
    tasks = []
    finalList = []
    
    headers = {
        "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
    ##Asynchronously get all the raw html data for each url
    async with aiohttp.ClientSession(headers=headers) as session:
        for item in theList:
            url = urlBase + item
            tasks.append(fetch(session, url))

        htmls = await asyncio.gather(*tasks)
        msg = "Successfully retrieved " + str(len(htmls)) + " URLs."
        print(msg)
        print("Processing...")
        index = 0
        for html in htmls:
            if html is not None:
                url = html[1]
                data = html[0]
                soup = BeautifulSoup(data,'html.parser')
                ##traverse html data for relevant match to search criteria (TODO Add more filters)
                needsTransfer = True
                if ourServer in item:
                    needsTransfer = False
                
                for strongText in soup.find_all('strong'):
                    if ourSpecs in strongText.get_text():
                        for gs in soup.find_all(class_='gearscore'):
                            if "Item Level" in gs.get_text():
                                gsText = gs.get_text()
                                gsF = float(gsText[12:])
                                if gsF >= float(minGearscore):
                                    bossKillTable = soup.find(id="tiers_details")
                                    if bossKillTable is not None:
                                        kills = 0
                                        for kill in soup.find_all(class_='progress_heroic'):
                                            if "Mythic" in kill.get_text():
                                                kills+=1
                                        if kills >= int(minKills):
                                            if needsTransfer:
                                                for spanText in soup.find_all('span'):
                                                    if transferKey in spanText.get_text():
                                                       finalList.append(url)
                                            else:
                                               finalList.append(url)
            else:
                continue
            index += 1
            msg = "Progress: " + str(round(len(htmls) / 100 * index, 2)) + "%"
            print(msg, end='\r')
    
    ##Write the relevent urls for hits to file; TODO Directly to google sheet?
    file_name = ourClass + "_" + ourSpecs + ".txt"
    with open(file_name, "w") as f:
      [f.write(f'{final_item}\n') for final_item in finalList]
    print(f"{str(len(finalList))} recruit(s) found and written to file.")
    
if __name__ == "__main__":
    asyncio.run(main())
