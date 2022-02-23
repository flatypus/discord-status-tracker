import discord
import pickle
import asyncio

intents = discord.Intents().all()
intents.members = True

client = discord.Client(intents=intents,status='HI')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel = await client.fetch_channel("CHANNEL NAME") #only include these two lines
    await track(channel,"ID OF PERSON TO TRACK")         #if you want to auto track a person when starting; useful if heroku restarts dynos

async def checkonline(channel,person,online):
    while True:
        member=''
        for i in client.guilds: #finds the member in all servers that the bot is in. If the person is not in a server the bot is in, the command will fail.
            try:
                member = i.get_member(person)
                break
            except:
                pass
        if member == '':
            channel.send(f"'{person}' is not in a server that is shared by this bot")
            return
        try:
            dict=pickle.load(open(r'status','rb')) #stores current status in pickled dictionary
        except:
            dict={1:''}
        if str(member.status) == 'offline' and online: #checks if person is offline, but last logged as online
            online=False
            await channel.send(f"{member.name} is now offline")
            dict[person]=''
        elif str(member.status) != 'offline' and not online: #checks if person is online, but last logged as offline
            online=True
            try:
                if 'playing' not in member.activities[0].type: # to ensure that the bot is not detecting a person playing a game instead
                    status = str(member.activities[0].name)
                    await channel.send(f"{member.name} is back online. Their status is '{status}'")      
            except:
                status=''
                await channel.send(f'{member.name} is back online, but does not have a status')
            dict[person]=status
        else:
            try:
                status = str(member.activities[0].name)
                if dict[person] != status and 'playing' not in member.activities[0].type:
                    await channel.send(f"{member.name} updated their status to '{status}'")
                dict[person]=status
            except:
                try:
                    if dict[person] != '':
                        await channel.send(f"{member.name} is online but does not have a status")
                        dict[person]=''
                except:
                    dict[person]=''
        pickle.dump(dict,open(r'status','wb'))  
        await asyncio.sleep(0)

async def track(channel,person): #this whole block of code is just to do a first status check to set variables in the right place before running the loop
    member = client.guilds[0].get_member(person)
    await channel.send(f"Tracking {member.name}")
    try:
        dict = pickle.load(open(r'status','rb'))
    except:
        dict={1:''}
    pickle.dump(dict,open(r'status','wb'))
    online=str(member.status)!= 'offline'
    try:
        status = str(member.activities[0].name)
        if dict[person] != status and 'playing' not in member.activities[0].type:
            await channel.send(f"{member.name}'s status is '{status}'")
        dict[person]=status
    except:
        if online:
            await channel.send(f"{member.name} does not have a status")
        else:
            await channel.send(f"{member.name} is offline")
        dict[person]=""
    client.loop.create_task(checkonline(channel,person,online))

@client.event
async def on_message(message):
    if '!track' in message.content:
        await track(message.channel,int(message.content[7:]))

client.run('CLIENT TOKEN') #replace token with token from discord dev website