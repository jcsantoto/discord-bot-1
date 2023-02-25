import discord
from discord import File
import random
import time
import asyncio
import requests
from bs4 import BeautifulSoup

##Retrieves text from billwurtz notepad
billwurtz = requests.get('https://billwurtz.com/notebook.html')
soup = BeautifulSoup(billwurtz.text, 'html.parser')
results = soup.find_all('a', href=True)

client = discord.Client()
global gamestatus
gamestatus = discord.Game('')

fp2 = open('monke.jpg', 'rb')
monke = fp2.read()

async def retrieve_bw(mes):
    h = random.choice(results)['href']
    response = requests.get('https://billwurtz.com/'+h)
    soup2 = BeautifulSoup(response.text, 'html.parser')
    bruh = soup2.find_all(text=True)
    await mes.channel.trigger_typing()
    await asyncio.sleep(2)
            
    x = "".join(bruh)
    n = 2000
    limiter = [x[i:i+n] for i in range(0, len(x), n)]
    for z in limiter:
        await mes.channel.send(z)
        await mes.channel.trigger_typing()
        await asyncio.sleep(2)

##Adding nothing to the event loop
async def null():
    await asyncio.sleep(0.5)

##Timed Roles
async def timed_role(member,mess,role,time,msg1,msg2):
    await member.add_roles(role)
    if(msg1!=""):
        await mess.channel.send(msg1)
    await asyncio.sleep(time)
    if(msg2!=""):
        await mess.channel.send(msg2)
    await member.remove_roles(role)

##Use this to mute user for 30 seconds, asynchronously
async def timed_mute(member,mess,mute,loop,time):
    await member.add_roles(mute)
    await mess.channel.send(str(member) + ' user was muted for '+ str(time) + ' seconds.')
    await asyncio.sleep(time)
    await member.remove_roles(mute)
    await mess.channel.send(str(member) + '\'s mute has expired')

##Using this to vote to mute a member
async def mute_vote(member,mess,mute,loop,time,id,msg1,msg2,msg3,disparity):
    await asyncio.sleep(10)
    re = mess.reactions
    chk = 0
    ex = 0

    for reaction in re:
        if str(reaction) == '✅':
            chk = reaction.count
        elif str(reaction) == '❌':
            ex = reaction.count

    print('checking vote results...')
    print('Yes :' + str(chk))
    print('No :' + str(ex))
    if (chk-ex) >= disparity:
        if id == 0:
            timed_m = loop.create_task(timed_mute(member,mess,mute,loop,time))
        elif id == 1:
            timed_m = loop.create_task(timed_role(member,mess,mute,time,msg1,msg2))
        await timed_m
    else:
        await mess.channel.send(msg3)

###########################################################################

@client.event
async def on_ready():
    global gamestatus
    print('We have logged in as {0.user}'.format(client))
    Guild = client.guilds
    timer = ''

    for g in Guild:
        if g.id == 749977771949948970:
            print('found guild')
            for c in g.channels:
                if c.id == 749977772562186252:
                    print('found channel')
                    m = await c.fetch_message(750747699946586183)
                    timer = m.content
    gamestatus = discord.Game(timer)
    await client.change_presence(status=discord.Status.online, activity=gamestatus)

@client.event
async def on_reaction_add(reaction,user):
    if user.id == 264275152349429760 and str(reaction) == "🤡":
        await reaction.message.channel.send('clown')
    
# Messages admin of a message that was deleted
@client.event
async def on_message_delete(message):
    await message.author.guild.owner.send(str(message.author) + " has deleted message: " + message.content)

# Messages admin of a message that was edited
@client.event
async def on_message_edit(before,after):
    await before.author.guild.owner.send(str(before.author) + " has edited a message. \n" + "Original: " +before.content + "\nNew: "+ after.content)

# Listens to messages in chat for commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('$hello'):
        await message.channel.send('Hello! ' + str(message.author)) 

    # Removes most recent 100 messages sent by the bot
    elif message.content.startswith('$purgebot'):
        
        def is_me(m):
            return m.author == client.user

        deleted = await message.channel.purge(limit=100, check=is_me)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)))

    # Delete messages with blacklisted keywords specified in badwords.txt
    elif message.content.startswith('$purgea'):
        def is_bad(m):
            check = False

            if m.author.id == 264275152349429760:
                andrewbadwords = open("badwords.txt","r")
                for line in andrewbadwords:
                    for word in line.split():
                        if word.lower() in discord.utils.escape_mentions(m.content.lower()):
                            check = True  
            return check

        deleted = await message.channel.purge(limit=500, check=is_bad)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)))

    # Silly feature that lets users be infected with a temporary 'monkey' role
    elif message.author.guild.get_role(753352032227950793) in message.author.roles:
        c = message.content
        if not ('banana' in c or 'monke' in c or len(c) <= 40) :
            await message.delete() 

        m = await client.wait_for('message', check=None)
        r = random.randint(0,1)
        if r == 0 and m.author != message.author and message.author.guild.get_role(753352032227950793) not in m.author.roles:
            await message.channel.send('uh oh ' + str(message.author) + ' has infected ' + str(m.author))
            loop = asyncio.get_event_loop()
            role = message.author.guild.get_role(753352032227950793)
            temp = m.author.display_name
            timer = loop.create_task(timed_role(m.author,message,role,120,"",""))
            timer = loop.create_task(m.author.edit(nick='monke'))
            await timer
            await asyncio.sleep(120)
            await m.author.edit(nick = temp)

    elif message.content.startswith('$end'):
        await message.channel.send(client.user.activity.name)

    elif message.content.startswith('$test'):
        await message.channel.send('.')

    # Temporary ban role, where users cannot see or send any messages
    elif message.content.startswith('$banish'):
        loop = asyncio.get_event_loop()
        Guild = message.author.guild
        role = message.author.guild.get_role(752009179769864283)

        mentions = message.mentions
        if message.mention_everyone == True:
            mentions = Guild.members

        await message.add_reaction('✅')
        await message.add_reaction('❌')

        loop = asyncio.get_event_loop()

        for mem in mentions:
            if mem.bot == True:
                await message.channel.send(mem.name + " is temporarily banned.")
                continue
            timer = loop.create_task(mute_vote(mem,message,role,loop,240,1, mem.name + ' has been temporarily banned.' ,"", str(mem)+" was not banned.",2))
            
        timer = loop.create_task(null())
        await timer

    # Silly feature that lets users be given a 'stunned' (as if in a video game) role that prevents them from typing in chat temporarily.
    elif message.content.startswith('$stun'):
        
        if message.mentions == []:
            await message.channel.send('Zeus has struck Joe.')

        else:
            loop = asyncio.get_event_loop()
            for mem in message.mentions:
            
                hit = random.randint(0,9)
                if hit > 4:
                    role = message.author.guild.get_role(752000883666976798)
                    await message.channel.send(mem.name + ' has been stunned.')

                    timer = loop.create_task(timed_role(mem,message,role,30,"",""))
                    
                else:
                    await message.channel.send(mem.name + ' said \"no\".')

                timer = loop.create_task(null())
                await timer

    # Silly feature that lets users be given a "blind" role that prevents them from seeing messages temporarily.
    elif message.content.startswith ('$blind'):
        if message.mentions == []:
            await message.channel.send('Joe has no more eyes.')

        else:
            loop = asyncio.get_event_loop()
            for mem in message.mentions:

                hit = random.randint(0,9)
                if hit > 4:
                    role = message.author.guild.get_role(752001011350110299)
                    await message.channel.send(mem.name + ' needs glasses.')
                    timer = loop.create_task(timed_role(mem,message,role,30,"",""))
                else:
                    await message.channel.send(mem.name + ' eated carrot. Now can see forever.')

                timer = loop.create_task(null())
                await timer

    ## Used to debug escaped mentions
    elif message.content.startswith('$$e'):
        await message.channel.send(discord.utils.escape_mentions(message.content))
        await message.channel.send("```" + message.content + "```")
    
    ## Used to mute users temporarily
    elif message.content.startswith('$mute'):

        args = message.content.split(' ',1)[0].replace('$mute','')
        try:
            time = int(args)
            if time > 120:
                time = 120
        except ValueError:
            time = 30

        Guild = message.author.guild
        mute = Guild.get_role(750932003410542602)
        mentions = message.mentions

        await message.add_reaction('✅')
        await message.add_reaction('❌')

        loop = asyncio.get_event_loop()

        if message.mention_everyone == True:
            mentions = Guild.members


        for mem in mentions:
            if mem.bot == True:
                await message.channel.send(mem.name + " will not be muted.")
                continue
            wait_vote = loop.create_task(mute_vote(mem,message,mute,loop,time,0,"","",str(mem)+ " was not muted.",1))

        wait_vote = loop.create_task(null())
        await wait_vote
        

            
    ##What is the answer
    elif ( "what" in message.content.lower() or "get" in message.content.lower() or "give" in message.content.lower() or "need" in message.content.lower() or "please" in message.content.lower() or "tell" in message.content.lower() ) and "answer" in message.content.lower():
        z = random.randint(0,12)
        answer = open("answers.txt","r")


        for line in answer:
            z = z - 1
            if z == -1:
                if line == '':
                    await message.channel.trigger_typing()
                else: 
                    await message.channel.send(line)
                    
                break

    ## Silly feature that sends random messages about monkeys with "monkey" is mentioned in the message
    elif "monke" in message.content.lower():
        global gamestatus
        z = random.randint(0,7)
        if z == 0:
            await message.channel.send('All hail the monke king <@201169339154432000>')
        elif z == 1:
            await message.channel.send('I like monkeys.')
            await asyncio.sleep(1.75) 
            p = random.randint(0,3)
            if p == 0:
                await message.channel.send('The pet store was selling monkeys for five cents a piece. I thought that odd since they were normally a couple thousand. I decided not to look a gift horse in the mouth. I bought 200.')
            elif p == 1:
                await message.channel.send('Two hours later I found out why all the monkeys were so inexpensive: they all died. No apparent reason. They all just sorta\' dropped dead. Kinda\' like when you buy a goldfish and it dies five hours later. Damn cheap monkeys.')
            elif p == 2:
                await message.channel.send('I finally arrived at a solution. I gave the monkeys out as Christmas gifts. My friends didn\'t know quite what to say. They pretended that they like them, but I could tell they were lying.')
        elif z == 2:
            await message.channel.send('OOH OOH AHH AAHHH OOOGA BOOGA')
        elif z == 3:
            if message.author.activity.name != None:
                await message.channel.send('monkey see monkey do')

                if message.author.activity.type == discord.ActivityType.custom: 
                    game2 = discord.Game(message.author.activity.name)
                    await client.change_presence(status=discord.Status.online, activity=game2)
                else: 
                    await client.change_presence(status=discord.Status.online, activity=message.author.activity)

                await asyncio.sleep(15)
                await client.change_presence(status=discord.Status.online, activity=gamestatus)
            else:    
                await message.channel.send('https://tenor.com/view/monkey-gif-6648569')
        elif z == 4:
            await message.channel.send('want banan get banan')
            await message.add_reaction('🍌')
        elif z == 5:
            await message.channel.send('uh oh monke virus')
            loop = asyncio.get_event_loop()
            role = message.author.guild.get_role(753352032227950793)
            temp = message.author.display_name
            timer = loop.create_task(timed_role(message.author,message,role,120,"",""))
            timer = loop.create_task(message.author.edit(nick='monke'))
            await timer
            await asyncio.sleep(120)
            await message.author.edit(nick = temp)

    # Retrieves random message from bill wurtz website
    elif message.content.startswith('$bw'):
       await retrieve_bw(message)

    # Retrieves and posts the user's profile picture or of the users mentioned in the message
    elif message.content.startswith('$au'):
        if message.mentions != []:
            for mem in message.mentions:
                await message.channel.send(str(mem.avatar_url))
        else:
            await message.channel.send(str(message.author.avatar_url))

    # Random chance responses
    else:
        r = random.randint(0,40)

        if r < 5 and ('is' in message.content or 'can' in message.content or 'have'in message.content):
            await message.channel.send('wrong')
            msg = await client.wait_for('message', check = None)
            if 'wrong' in msg.content or 'incorrect' in msg.content:
                await message.channel.send('the real answer is ')
            elif 'right' in msg.content or 'correct' in msg.content:
                await message.channel.send('wrong')
                
        elif r == 12:
            await retrieve_bw(message)
            

client.run('input key here')

