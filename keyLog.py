import json

def writeKey(user,key,classes):
    with open('keys.json') as json_file: 
        temp = json.load(json_file)

        for i,v in enumerate(temp):
            if v["discordId"] == user.id:
                temp.pop(i)

        payload = {
            "discordId": user.id,
            "canvasKey": key,
            "classPeriods": classes,
        }

        temp.append(payload) 
        
    writeJSON(temp)  


def writeJSON(data, filename='keys.json'):
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 

def readUser(user):
    with open('keys.json') as json_file: 
        temp = json.load(json_file)

        for i in temp:
            if i["discordId"] == user.id:
                return i

def getKeys():
    with open('keys.json') as json_file: 
        temp = json.load(json_file)
        return temp