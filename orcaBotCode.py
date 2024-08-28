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
client = discord.Client(intents=intents)

bot = commands.Bot(intents=intents)

# global variables
server_cache = {}
pruned = []
sglistening = False
word = []
hasRound = False
forceStop = False

# "hi" command 
# @bot.slash_command(name="hi", description="Let the bot greet you!")
# @option(
#     "name",
#     description="Enter a name",
#     required=False,
#     default=''
# )
# async def hi(
#         ctx: discord.ApplicationContext,
#         name: str
# ):
#     if name == '':
#         await ctx.respond('uwu hi i am an orca! (and a bot, but mostly an orca)')
#     else:
#         await ctx.respond(f'uwu hi {name} i am an orca! (and a bot, but mostly an orca)')

# # antirinbot WIP

# @bot.slash_command(name="antirinbot", description="Set the channel and activity status of antirinbot")
# @option(
#     "channel-id",
#     description="Channel ID of rinbot activity",
#     required=True,
#     default=""
# )

# async def set(ctx: discord.ApplicationContext, interaction: discord.interactions, channel: str):
#     found = False
#     with open ("Code/VSCode/Personal/Orca Bot/server_cache.txt") as rFile:
#         for line in rFile:
#             if int(line.split()[0]) == interaction.guild.id:
#                 found = True
#             server_cache[int(line.split()[0])] = int(line.split()[1])
            
#     if not found:
#         with open("Code/VSCode/Personal/Orca Bot/server_cache.txt", "a") as rFile:
#             rFile.write(f"{interaction.guild.id} {channel}\n")

# # listening to channel

# async def on_message(message):
#     if server_cache[message.guild.id] == message.channel.id:
#         pass


# sg group
@bot.slash_command(name="cancelg", description="cancel the current session")
async def cancelg(ctx: discord.ApplicationContext):
    global hasRound
    hasRound = False
    global forceStop
    forceStop = True
    ctx.respond("Session stopped. Wait for the current round to conclude.")

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
    global hasRound
    if hasRound:
        await ctx.respond("There is currently an active round, please wait or cancel the current round.")
        return
    hasRound = True
    if genre == "vocab":
        await sgvocab(ctx, dataset, rounds, time, hints)
        
async def processText(fileName):
    # processText assumes that the file fileName is already processed. 
    with open(fileName) as cin:
        output = [word.split("&") for word in cin.readlines()]
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
        for i in range(hintCnt):
            await asyncio.sleep(10)
            if hintCnt % 2 == 1:
                hint = await generateHint(answer, hint)
            hintEmbed = discord.Embed(
                title="**Hint**",
                description=f"`{hint}`"
            )
            if not sglistening: break
            await ctx.send(embed=hintEmbed)
    
    async def monitor_sglistening():
        global sglistening
        while sglistening:
            await asyncio.sleep(0.1)
    
    async def sglisten(message):
        global sglistening
        print(message.content)
        if message.channel == ctx.channel and sglistening:
            if message.content.lower() in definition.lower() and len(message.content.lower()) > 2:
                correctEmbed = discord.Embed(
                    title="Correct!",
                    description=f"{message.author.mention} got it right!",
                )
                correctEmbed.add_field(name=f"Guess: `{message.content}`", value="", inline=True)
                correctEmbed.add_field(name=f"**{term}**", value=f"{definition}", inline=True)
                await ctx.send(embed=correctEmbed)
                hint.cancel()  # Cancel the hint task if the correct answer is found
                sglistening = False

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
            forceStop = False
            stopEmbed = discord.Embed(
                title="Session terminated.",
                description=f"L"
            )
            ctx.send(embed=stopEmbed)
            print("test")
            return

        word = random.choice(vocab)
        term = word[0]
        definition = word[1]
        mnemonic = word[2]

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
        sglistening = True
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

#GPT testing
@bot.slash_command(name="askgpt", description="Ask a question to AI!")
@option(
    "Inquiry",
    description="Ask something!",
    required=True,
)

async def askgpt(ctx: discord.ApplicationContext, inquiry: str):
    banned_ppl = [815017361215979541]
    banned = False
    # # toggle the banned filter (banned_ppl currently contains lever)
    # try: 
    #     banned = True if banned_ppl.index(ctx.author.id) != -1 else False
    # except ValueError:
    #     banned = False
    if banned:
        await ctx.respond("https://tenor.com/view/alya-sometimes-hides-her-feelings-in-russian-roshidere-qazira-alisa-mikhailovna-kujou-alya-san-gif-14476115292297719268")
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f'Respond to this message as prompted: {inquiry}.'},
                {"role": "user", "content": f'Respond to this message as prompted: {inquiry}.'}
                ])
        await ctx.respond(f'Question: {inquiry}'+'\n'*2 + 'Response: '+response["choices"][0]["message"]["content"])
        # await ctx.respond('Sorry, askgpt is currently under maintenance. Maybe try Clyde or the ChatGPT Website?')

@bot.slash_command(name="orca", description="Show a random gif of an orca!")
async def flip(ctx: discord.ApplicationContext,):
    # Initialize a list to store the file contents
    orcaGifs = []

    # thank you chatgpt for the optimized list-based gif storage system
    # Check if the file has already been read and stored

    if not orcaGifs:
        with open("orcaCommand.in") as rFile:
            # Read the file and store its contents
            lines = rFile.readlines()
            orcaGifs.extend([line.rstrip() for line in lines])
    await ctx.respond(random.choice(orcaGifs))

print("running")

bot.run(discord_api)
