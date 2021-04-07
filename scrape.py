from bs4 import BeautifulSoup
import requests
import asyncio

#MODIFY YOUR INFO/REQUIREMENTS#####
   
ourServer = "twisting-nether"
ourRaidsPerWeek = "2"
updateThresholdDays = 10
pagesToCheck = 10

###################################
#KEYS##############################
base = "https://www.wowprogress.com"
key = "/character/eu/"
nextkey = "/gearscore/char_rating/next/"
transferKey = "Yes, ready to transfer"
timeKey = "day ago"
timeKey2 = "days ago"
###################################

print("\n\n Class & spec combinations available: \n ~~~~~~~~~~~~~~~~~~\n deathknight - dd, tank \n demon hunter - dd, tank \n druid - balance, restoration, feral dd, feral tank \n hunter - beastmastery, marksmanship, survival \n mage - arcane, fire, frost \n monk - healer, dd, tank \n paladin - holy, protection, retribution \n priest - healer, dd \n rogue - assassination, outlaw, subtlety \n shaman - elemental, enhancement, restoration \n warlock - affliction, demonology, destruction \n warrior - dd, protection \n ~~~~~~~~~~~~~~~~~~\n")

ourClass = input("Class: ")
ourSpecs = input("Specs: ")

    
async def task(name, finalList, work_queue):
    #msg = "Getting info for recruit " + str(index) + "/" + str(len(list))
    #print(msg, end='\r')
    #index+=1;
    while not work_queue.empty():
        item = await work_queue.get()
        print(f"Task {name} running")
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
        await asyncio.sleep(1)

async def main():
   
    url = "https://www.wowprogress.com/gearscore/class." + ourClass + "?lfg=1&raids_week=" + ourRaidsPerWeek + "&lang=en"

    fileName = ourClass + "_" + ourSpecs + ".txt"
    f = open(fileName, "w")

   
    theList = []

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
                                theList.append(target)
                        else:
                            theList.append(target)
       

    msg = "Found " + str(len(theList)) + " potential recruits."
    print(msg)

    finalList = []
    work_queues = []
    for x in range(4):
        work_queues.append(asyncio.Queue())
    queueSize = round(len(theList) / 4)+1;
    index = 0
    queueIndex = 0
    for work in theList:
        await work_queues[queueIndex].put(work)
        index+=1
        if index > queueSize :
            index = 0
            queueIndex += 1
        
    await asyncio.gather(
        asyncio.create_task(task("One", finalList, work_queues[0])),
        asyncio.create_task(task("Two", finalList, work_queues[1])),
        asyncio.create_task(task("Three", finalList, work_queues[2])),
        asyncio.create_task(task("Four", finalList, work_queues[3])),
    )
                
    for finalItem in finalList:
        f.write(finalItem)
        f.write('\n')
    msg = str(len(finalList)) + " recruit(s) found and written to file."
    print(msg)
        
    f.close()
    
if __name__ == "__main__":
    asyncio.run(main())
