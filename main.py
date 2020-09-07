import discord, html2text, os, dateutil.parser, json
from datetime import datetime, timedelta
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException, InvalidAccessToken
import keyLog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv
import embeds

load_dotenv()

TOKEN = os.getenv('TOKEN')
prefix = 'c' 

API_URL = "https://hcpss.instructure.com"

client = discord.Client()

htmlText = html2text.HTML2Text()
htmlText.ignore_links = True


@client.event
async def on_ready():
    print('ready!')

@client.event
async def on_message(message):
    #if message.content[0] == prefix.lower() or message.content[0] == prefix.upper():
        command = message.content[len(prefix):]
        params = command[command.find(" ")+1:]
        splitparams = params.split()

        if command.find(" ") != -1: # commands with params
            command = command[:command.find(" ")].lower()



        if command == "bind":
            '''
            bind a user's discord id to a canvas api key
            '''
            key = splitparams[0]
            keyLog.writeKey(message.author,key)
            try:
                canvas = Canvas(API_URL, keyLog.readKey(message.author))
                courses = stripCourses(canvas.get_courses())
                await message.channel.send(embed=embeds.genericSuccess("bound {} to new canvas key".format(message.author.name)))
            except InvalidAccessToken as ex:
                payload = json.loads(str(ex).strip('][').split(',')[0].replace("'", '"'))
                await message.channel.send(embed=embeds.errorEmbed(payload))
            await message.delete()


        if command == "meetlinks":
            date = datetime.today().strftime('%Y-%m-%d')

            if len(splitparams) != 0 and splitparams[0] != command:
                date = splitparams[0]

            codes = await getUserMeetCodes(message.author, date)
            print(codes)

            await message.channel.send(embed=embeds.onePeriodMeetLinks(codes,date,message.author.name))


        if command == "todo" or command == "events":
            '''
            gets assignments/calendar events due on a certain day, today by default but can be overridden by providing datein yyyy-mm-dd format
            '''
            try:
                canvas = Canvas(API_URL, keyLog.readKey(message.author))
                courses = stripCourses(canvas.get_courses())

                date = datetime.today().strftime('%Y-%m-%d')

                if len(splitparams) != 0 and splitparams[0] != command:
                    date = splitparams[0]
                
                courseIds = ["course_{}".format(course.id) for course in courses]

                events = canvas.get_calendar_events(context_codes=courseIds,type="assignment" if command == "todo" else "event",start_date=date)

                embed = discord.Embed(
                    title="{}'s to-do list for {}".format(message.author.name,date) if command == "todo" else "{}'s events for {}".format(message.author.name,date),
                )

                eventsCount = 0
                for event in events:
                    if event.description is not None:
                        desc = htmlText.handle(event.description)
                    else:
                        desc = "no description or assignment locked"
                    description = "[link]({}) \n**course**: {} \n**description**: {} \n".format(event.html_url,event.context_name,desc)
                    
                    title = "{}/ {}".format(datetime.strptime(event.start_at,'%Y-%m-%dT%H:%M:%SZ').time().strftime("%I:%M%p"), event.title) if command == "events" else event.title

                    embed.add_field(name=title,value=description,inline=False)
                    eventsCount = eventsCount + 1

                if eventsCount == 0:
                    embed.add_field(name="nothing to do today!",value="nice")
                
                await message.channel.send(embed=embed)
            except CanvasException as ex:
                payload = json.loads(str(ex))
                await message.channel.send(embed=embeds.errorEmbed(payload["errors"]))
            except InvalidAccessToken as ex:
                payload = json.loads(str(ex).strip('][').split(',')[0].replace("'", '"'))
                await message.channel.send(embed=embeds.errorEmbed(payload))
                


async def sync():
    '''
    send each person their calendar events for the day
    '''
    for i in keyLog.getKeys():
        user = client.get_user(i["discordId"])
        #embed = discord.Embed(title="good morning!")
        await user.send("test")


async def getUserMeetCodes(user,date=datetime.today().strftime('%Y-%m-%d')):
    '''
    get the meet codes for a given discord user object on a day
    '''
    links = []
    canvas = Canvas(API_URL, keyLog.readKey(user))
    courses = stripCourses(canvas.get_courses())
    for course in courses:
        courseIds = ["course_{}".format(course.id) for course in courses]
        events = canvas.get_calendar_events(context_codes=courseIds,type="event",start_date=date)
        for event in events:
            if event.description is not None:
                event.description = htmlText.handle(event.description) #turn all event descriptions into plaintext
            else:
                event.description = "no description"
        for event in events:
            desc = event.description.lower().splitlines()
            for line in desc:
                try:
                    codeIndexStart = line.find("mrhs-")
                    codeIndexEnd = line.rfind("-pd")+4
                    code = line[codeIndexStart:codeIndexEnd]
                    period = int(code[-1])
                    found = False
                    for link in links:
                        if code in link[1]:
                            found = True
                    if not found:
                        links.append([event.context_name,code])
                except:
                    continue
    return links


async def getMeetCodes(date=datetime.today().strftime('%Y-%m-%d')):
    '''
    go through all saved keys and find google meet codes
    '''
    meetLinks = [[],[],[],[]]
    for key in keyLog.getKeys():
        userLinks = await getUserMeetCodes(client.get_user(key["discordId"]),date)
        for link in userLinks:
            period = int(link[1][-1])
            found = False 
            for i in meetLinks[period-1]:
                if link in i[1]:
                    found = True
            if not found:
                meetLinks[period-1].append(link)
    return meetLinks


def stripCourses(courses):
    '''
    gets rid of the weird phantom courses
    '''
    realCourses = []
    for course in courses:
        if hasattr(course, 'name'):
            realCourses.append(course)
    return realCourses


job_stores = {'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')}
sched = AsyncIOScheduler(jobstores=job_stores)
sched_njs = AsyncIOScheduler()
sched.start()
sched_njs.start()
sched_njs.add_job(sync, "cron", hour=19, minute=58)
sched_njs.add_job(getMeetCodes, "cron", hour=21, minute=43)


client.run(TOKEN)