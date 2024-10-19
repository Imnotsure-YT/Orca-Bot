import discord
from discord.ext import commands
from discord.commands import option
import asyncio
import openai
import random
import os
import re

openai_api = os.environ.get('openai_api')
discord_api = os.environ.get('discord_api')

openai.api_key = openai_api
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

bot = commands.Bot(intents=intents)

# global variables
server_cache = {}
pruned = []
sglistening = {}
rinbotban = {}
word = {}
hasRound = False
forceStop = False

# sg group
@bot.slash_command(name="cancelg", description="cancel the current session")
async def cancelg(ctx: discord.ApplicationContext):
    global forceStop
    global sglistening
    forceStop = True
    sglistening[ctx.guild.id] = False
    await ctx.respond("Session stopped. Wait for the current round to conclude.")

@bot.slash_command(name="sg", description="guessing game for vocab & other things.")
@option(
    "genre",
    description="vocab is the only option rn",
    required=False,
    default="vocab"
)
@option(
    "dataset",
    description="choose the dataset from which to test, default is pruned",
    required=False,
    default="pruned"
)
@option(
    "rounds",
    description="enter the number of rounds, default is 1",
    required=False,
    default=1
)
@option(
    "time",
    descrption="total time, default is 30s",
    required=False,
    default=30
)
@option(
    "hints",
    description="number of hints in the given timeframe, default is 2",
    required=False,
    default=2
)

async def sg(ctx: discord.ApplicationContext, genre: str, dataset: str, rounds: int, time: int, hints: int):
    global sglistening
    if ctx.guild.id not in sglistening:
        sglistening[ctx.guild.id] = False
    if sglistening[ctx.guild.id]:
        await ctx.respond("There is currently an active round, please wait or cancel the current round.")
        return
    if genre == "vocab":
        await sgvocab(ctx, dataset, rounds, time, hints)
        
async def processText(fileName):
    # processText assumes that the file fileName is already processed. 
    with open(fileName) as cin:
        output = [line.split("&") for line in cin.readlines()]
    return output

async def sgvocab(ctx:discord.ApplicationContext, dataset: str, rounds: int, time: int, hints: int):
    global sglistening
    global word
    global hasRound
    global forceStop
    
    # load the dataset first
    vocab = []

    async def generateHint(answer, curHint):
        n = len(answer)
        for i in range(n):
            if curHint[i] == "_" and curHint[i] != " ":
                if random.randint(1, 10) <= 2:
                    curHint = curHint[:i] + answer[i] + curHint[i + 1:]
        return curHint

    async def sendHint(answer, hintCnt):
        hint = re.sub(r'\S', '_', answer)
        mnemonic = word[ctx.guild.id][2]
        for i in range(hintCnt):
            await asyncio.sleep(10)
            hintEmbed = discord.Embed(
                title="**Hint**",
                description=f"`{hint}`"
            )
            if i % 2 == 0:
                hint = await generateHint(answer, hint)
                hintEmbed.description=f"`{hint}`"
            else:
                hintEmbed.description=f"`{mnemonic}`"
            if word[ctx.guild.id][1] != answer: break
            await ctx.send(embed=hintEmbed)
    
    async def monitor_sglistening():
        global sglistening
        while sglistening[ctx.guild.id]:
            await asyncio.sleep(0.1)
    
    async def sglisten(message):
        global sglistening
        if message.channel == ctx.channel and sglistening[ctx.guild.id]:
            if message.content.lower() in definition.lower() and len(message.content.lower()) > 2:
                correctEmbed = discord.Embed(
                    title="Correct!",
                    description=f"{message.author.mention} got it right!",
                )
                correctEmbed.add_field(name=f"Guess: `{message.content}`", value="", inline=True)
                correctEmbed.add_field(name=f"**{term}**", value=f"{definition}", inline=True)
                await ctx.send(embed=correctEmbed)
                hint.cancel()  # Cancel the hint task if the correct answer is found
                sglistening[ctx.guild.id] = False

    bot.add_listener(sglisten, "on_message")
    
    if dataset == "pruned":
        global pruned
        if len(pruned) == 0:
            # load the vocab array through the algorithm
            pruned = await processText("pruned.txt")
        vocab = pruned
    
    for i in range(rounds):
        global sglistening

        if forceStop: 
            print("force stopped")
            sglistening[ctx.guild.id] = False
            forceStop = False
            stopEmbed = discord.Embed(
                title="Session terminated.",
                description=f"L"
            )
            await ctx.send(embed=stopEmbed)
            return

        word[ctx.guild.id] = random.choice(vocab)
        term = word[ctx.guild.id][0]
        definition = word[ctx.guild.id][1]

        print(f"{term}: {definition}\n")

        hint = asyncio.create_task(sendHint(definition, hints))

        startEmbed = discord.Embed(
            title="Starting Round!",
            description=f"Round {i + 1} out of {rounds}",
        )

        await ctx.respond(embed=startEmbed)

        await asyncio.sleep(3)

        promptEmbed = discord.Embed(
            title=f"{term}",
            description="Guess the definition of the word!"
        )

        await ctx.send(embed=promptEmbed)
        sglistening[ctx.guild.id] = True
        print(f"waiting for {time}")

        try: 
            await asyncio.wait_for(monitor_sglistening(), timeout=time)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="Round Over",
                description="No one got the word correct."
            )
            timeout_embed.add_field(name=f"**{term}**", value=f"**{definition}**", inline=False)
            await ctx.send(embed=timeout_embed)
    
    bot.remove_listener(sglisten, "on_message")
    hasRound = False

# bark command 
@bot.slash_command(name="bark", description="Make the bot bark!")
@option(
    "length",
    description="Enter the number of barks.",
    required=False,
    default=2
)

async def bark(ctx: discord.ApplicationContext, length: int):
    await ctx.respond('ARF '*length)

# admin bypass (thanks antares)
@bot.slash_command(name="ur_muted", description="ur muted")
@option(
    "user", 
    description="who to mute (ping)",
    required=True
)

async def ur_muted(ctx: discord.ApplicationContext, user: discord.User):
    pass

# jokes
@bot.slash_command(name="tips", description="Get a good tip from orca")
async def tips(ctx: discord.ApplicationContext):
    tips = []
    with open("tips.txt") as cin:
        temp = []
        n = int(input())
        for i in range(n):
            temp.append(cin.readline())
        tips.append(temp)
    
    tip = random.choice(tip)
    des = ""
    for i in range(1, len(tip)):
        des += tip[i] + "\n"
    tipEmbed = discord.Embed(
        name=tip[0],
        description=f"`{des}`"
    )
    await ctx.respond(embed=tipEmbed)

#GPT testing
@bot.slash_command(name="askgpt", description="Ask a question to AI!")
@option(
    "Inquiry",
    description="Ask something!",
    required=True,
)

async def askgpt(ctx: discord.ApplicationContext, inquiry: str):
    global word
    banned_ppl = [815017361215979541]
    banned = False
    # toggle the banned filter (banned_ppl currently contains lever)
    checkBan = False
    if checkBan:
        try: 
            banned = True if banned_ppl.index(ctx.author.id) != -1 else False
        except ValueError:
            banned = False

    # banned if current inquiry contains the sgvocab word[ctx.guild.id]
    if len(word[ctx.guild.id][0]) != 0 and word[ctx.guild.id][0].lower() in inquiry.lower() and sglistening[ctx.guild.id]:
        banned = True

    # I'm sorry, but this is a bit too funny to pass up.
    if banned:
        await ctx.respond("dont cheat noob")
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f'Respond to this message as prompted: {inquiry}.'},
                {"role": "user", "content": f'Respond to this message as prompted: {inquiry}.'}
                ])
        await ctx.respond(f'Question: {inquiry}'+'\n'*2 + 'Response: '+response["choices"][0]["message"]["content"])
        # await ctx.respond('Sorry, askgpt is currently under maintenance. Maybe try the ChatGPT Website?')

@bot.slash_command(name="orca", description="Show a random gif of an orca!")
async def flip(ctx: discord.ApplicationContext,):
    # Initialize a list to store the file contents
    orcaGifs = []
    if not orcaGifs:
        with open("orcaCommand.in") as rFile:
            # Read the file and store its contents
            lines = rFile.readlines()
            orcaGifs.extend([line.rstrip() for line in lines])
    await ctx.respond(random.choice(orcaGifs))

print("running")

bot.run(discord_api)
