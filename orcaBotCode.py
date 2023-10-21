import discord
from discord.ext import commands
from discord.commands import option
import openai
import random
import os

openai_api = os.environ.get('openai_api')
discord_api = os.environ.get('discord_api')

openai.api_key = openai_api
intents = discord.Intents.default()
client = discord.Client(intents=intents)

bot = commands.Bot()

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

# bark command 
@bot.slash_command(name="bark", description="Make the bot bark!")
@option(
    "length",
    description="Enter the number of barks.",
    required=False,
    default=2
)
async def bark(
        ctx: discord.ApplicationContext,
        length: int
):
    await ctx.respond('ARF '*length)

#GPT testing
@bot.slash_command(name="askgpt", description="Ask a question to AI!")
@option(
    "Inquiry",
    description="Ask something!",
    required=True,
)
async def askgpt(
        ctx: discord.ApplicationContext,
        inquiry: str
):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f'Respond to this message as prompted: {inquiry}.'},
            {"role": "user", "content": f'Respond to this message as prompted: {inquiry}.'}
            ])
    await ctx.respond(f'Question: {inquiry}'+'\n'*2 + 'Response: '+response["choices"][0]["message"]["content"])
    # await ctx.respond('Sorry, askgpt is currently under maintenance. Maybe try Clyde or the ChatGPT Website?')

#"fun" command group
secret = bot.create_group("secret", "Secret commands requested by special people! (Password protected)")

@secret.command(name='dylan', description='Password protected command.')
@option(
    "password",
    descrption="Enter a password.",
    required=True,
)
async def dylan(
    ctx: discord.ApplicationContext,
    password: str
):
    if password == "master orka":
        await ctx.respond('you cannot escape the monika simps')
    else:
        await ctx.respond('Password incorrect.')

@bot.slash_command(name="orca", description="Show a random gif of an orca!")
async def flip(
        ctx: discord.ApplicationContext,
):
    # Initialize a list to store the file contents
    orcaGifs = []

    # thank you chatgpt for the optimized list-based gif storage system
    
    # Check if the file has already been read and stored
    if not orcaGifs:
        with open('orcaCommand.in', 'r') as rFile:
            # Read the file and store its contents
            lines = rFile.readlines()
            orcaGifs.extend([line.rstrip() for line in lines])

    # Generate a random index to select a line from flipGifs
    rand = random.randint(0, len(orcaGifs) - 1)
    await ctx.respond(orcaGifs[rand])

bot.run(discord_api)
