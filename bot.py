import discord
from discord.ext import commands
import sys
import asyncio
import os
from discord.utils import get
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions
from setup import prefix, authorid, serverid, token

description = 'Reddit votes bot'
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=prefix, description=description, intents=intents)
typeStatusPlay = discord.ActivityType.playing
typeStatusListen = discord.ActivityType.listening
bot.remove_command("help")
server = None
upvote = None
downvote = None

@bot.event
async def on_ready():
    global server
    global upvote
    global downvote
    server = discord.utils.get(bot.guilds, id=serverid)
    if not server:
        print('The server ID with the downvote and upvote emojis is required for the bot to function.\n'
        'Please assign it in the setup.py file.\n'
        'Read the README.md for more information.\n'
        'Thank you.')
        sys.exit()
    upvote = discord.utils.get(server.emojis, name='upvote')
    downvote = discord.utils.get(server.emojis, name='downvote')
    if not upvote or not downvote:
        print('The upvote and downvote emojis are required for the use of this bot.\n'
        'Please add them to your server\'s emojis.\n'
        'Read the README.md for more information.\n'
        'Thank you.')
        sys.exit()
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=typeStatusListen, name='new posts | ~help'))

@bot.event
async def on_message(message):
    channeltemp=str(message.channel.id)
    with open ("id.txt", "r") as channelsearch:
        for channelline in channelsearch:
            if channeltemp in channelline:
                await message.add_reaction(upvote)
                await message.add_reaction(downvote)
    with open ("attid.txt", "r") as channelsearch:
        for channelline in channelsearch:
            if channeltemp in channelline:
                if message.attachments:
                    await message.add_reaction(upvote)
                    await message.add_reaction(downvote)
    await bot.process_commands(message)

@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Reddit Votes", colour=discord.Colour(0xff5700), url="https://mi460.dev/github", description=f"Commands for {bot.user.name}")

    embed.set_thumbnail(url="https://archive.mi460.dev/images/reddit.png")
    embed.set_author(name=f"{bot.user.name}#{bot.user.discriminator}", url="https://mi460.dev/github", icon_url=f"{bot.user.avatar_url}")
    embed.set_footer(text="Simulating Reddit on Discord")

    embed.add_field(name=f"`{prefix}enable`", value="Enables new messages sent in the current channel to automatically have upvote/downvote reactions.")
    embed.add_field(name=f"`{prefix}disable`", value="Disables new messages sent in the current channel to automatically have upvote/downvote reactions.")
    embed.add_field(name=f"`{prefix}attenable`", value="Enables new messages *with attachments* sent in the current channel to automatically have upvote/downvote reactions. This is most important for meme channels when you only want images sent to be upvote-able.")
    embed.add_field(name=f"`{prefix}list`", value="Shows all enabled channels in a server.")

    await ctx.author.send(content="`All commands require administrator permission on a server. Please note that the bot will require the add reactions permission and (occasionally) the manage messages permission. Thank you for using my bot :)`", embed=embed)
    await ctx.message.add_reaction(upvote)

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def enable(ctx):
    """Enables bot abilities for a channel"""
    channelid=str(ctx.channel.id)
    found = False
    with open ("id.txt","r") as channelsetsearch:
        for channelsetline in channelsetsearch:
            if channelid in channelsetline:
                await ctx.author.send(f"<#{channelid}> is already enabled.")
                found = True
    with open ("attid.txt","r") as channelsetsearch:
        for channelsetline in channelsetsearch:
            if channelid in channelsetline:
                await ctx.author.send(f"<#{channelid}> is already enabled for attachments.")
                found = True
    if not found:
        with open ("id.txt","a") as channelsetwrite:
            channelsetwrite.write(f"{channelid}\n")
            await ctx.send(f"<#{channelid}> is now enabled.")
    await ctx.message.delete()

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def attenable(ctx):
    """Enables bot abilities for a channel with attachments required"""
    channelid=str(ctx.channel.id)
    found = False
    with open ("attid.txt","r") as channelsetsearch:
        for channelsetline in channelsetsearch:
            if channelid in channelsetline:
                await ctx.author.send(f"<#{channelid}> is already enabled for attachments.")
                found = True
    with open ("id.txt","r") as channelsetsearch:
        for channelsetline in channelsetsearch:
            if channelid in channelsetline:
                await ctx.author.send(f"<#{channelid}> is already enabled.")
                found = True
    if not found:
        with open ("attid.txt","a") as channelsetwrite:
            channelsetwrite.write(f"{channelid}\n")
            await ctx.send(f"<#{channelid}> is now enabled for attachments.")
    await ctx.message.delete()

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def disable(ctx):
    """Disables bot abilities for a channel"""
    channelid=str(ctx.channel.id)
    replace = ""
    with open ("id.txt","r") as channelsetsearch:
        contents = channelsetsearch.read()
        replace = contents.replace(f"{channelid}\n", "")
        failed = contents == replace
    if failed:
        idfailed = True
    else:
        with open ("id.txt","w") as channelsetwrite:
            channelsetwrite.write(replace)
            await ctx.send(f"<#{channelid}> is now disabled.")
    failed = False
    with open ("attid.txt","r") as channelsetsearch:
        contents = channelsetsearch.read()
        replace = contents.replace(f"{channelid}\n", "")
        failed = contents == replace
    if failed:
        attfailed = True
    else:
        with open ("attid.txt","w") as channelsetwrite:
            channelsetwrite.write(replace)
            await ctx.send(f"<#{channelid}> is now disabled from attachments.")
    if idfailed and attfailed:
        await ctx.author.send(f"<#{channelid}> was never enabled.")
    await ctx.message.delete()

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def list(ctx):
    """Lists all enabled channels on a server"""
    channels=ctx.guild.text_channels
    list = []
    listatt = []
    found = False
    for every in channels:
        with open ("id.txt","r") as idsearch:
            for channelline in idsearch:
                if str(every.id) in channelline:
                    found = True
                    list.append(every.id)
        with open ("attid.txt","r") as idsearch:
            for channelline in idsearch:
                if str(every.id) in channelline:
                    found = True
                    listatt.append(every.id)
    if found:
        embed = discord.Embed(title="List of channels enabled", colour=discord.Colour(0xff5700),description=f"Displaying list for {ctx.guild}")
        embed.set_thumbnail(url="https://archive.mi460.dev/images/reddit.png")
        embed.set_author(name=f"{bot.user.name}#{bot.user.discriminator}", url="https://mi460.dev/github", icon_url="https://archive.mi460.dev/images/reddit.png")
        embed.set_footer(text="To disable functionality for a channel, use ~disable")
        for every in list:
            embed.add_field(name=f"#{ctx.guild.get_channel(every)}", value=f"All messages are enabled for Reddit Votes in {ctx.guild.get_channel(every).mention}.",inline=False)
        for every in listatt:
            embed.add_field(name=f"#{ctx.guild.get_channel(every)}", value=f"Only attachment messages are enabled for Reddit Votes in {ctx.guild.get_channel(every).mention}.",inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No channels are enabled in `{ctx.guild}`.")
    await ctx.message.add_reaction(upvote)

@bot.command(pass_context=True)
async def stop(ctx):
    """Stops bot"""
    if authorid:
        if ctx.author.id == authorid:
            await ctx.author.send(f"Stopping...")
            await asyncio.sleep(1)
            await ctx.author.send(f"Ended session")
            sys.exit("Session Ended.")
    await ctx.send("If you're having issues with the bot, feel free to disable its features! Use ~disable.\n"
    "(Please note that this command requires administrator permissions)")
    await ctx.message.add_reaction(upvote)

@bot.command(pass_context=True)
async def restart(ctx):
    """Restarts bot"""
    if authorid:
        if ctx.author.id == authorid:
            await ctx.author.send(f"Restarting...")
            await asyncio.sleep(1)
            await ctx.author.send(f"Ended session")
            os.execl(sys.executable, sys.executable, *sys.argv)

@bot.command(pass_context=True)
async def status(ctx, *, tempgame = None):
    """Changes game"""
    if authorid:
        if ctx.author.id == authorid:
            if tempgame:
                await ctx.message.add_reaction(upvote)
                await ctx.send(f"Changing game to `{tempgame}`...")
                await asyncio.sleep(1)
                await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=typeStatusPlay, name=tempgame))
                await ctx.send(f"Changed game to `{tempgame}`.")
            else:
                await ctx.message.add_reaction(upvote)
                await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=typeStatusPlay,name=None))
                await ctx.send("Removed bot status.")

bot.run(token)
