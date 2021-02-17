import os, sys, time
# Change current wordking directory to script "home" directory
os.chdir(os.path.dirname(sys.argv[0]))

import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from discordhooks import DiscordWebhooks
import random
import managejson, json

TOKEN = "" #Bot token goes here!

managejson.load()
status = ['.help to get commands!','Hello!']

# Change this to change command prefix
client = commands.Bot(command_prefix = '.')
client.remove_command('help')

currentHook = None
webhook = None

# Returns boolean, if string is valid url then True... duh
def check_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'localhost|'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(re.search(regex, url))

# If string could be a variable name then True...
def check_string(s):
    return bool(re.search(r'\s*[A-Za-z_]\w*\s*', s))

# Reset webhook paramaters to nothing
def clear_hook():
    webhook.set_content(title='', description='', color='')
    webhook.set_author(name='', icon_url='')
    webhook.set_footer(text='', icon_url='')
    webhook.set_image(url='')

# Keeps track of uptime.. and update discord status
async def timers():
    global uptime
    msg = cycle(status)
    uptime = 0
    while True:
        current_status = next(msg)
        await client.change_presence(activity=discord.Game(name=current_status))
        await asyncio.sleep(5)
        uptime += 5

# Send discord message in embed
async def embed_send(ctx, description, err=False):
    colors = 0xc000000 if err else 0x80f000
    if err:
        colors = 0xc00000
    else:
        colors = 0x80f000
    embed = discord.Embed(title="Command sent:",
        description="**{}**".format(description), color=colors)
    embed.set_footer(text="Command sent by {}".format(ctx.message.author),
        icon_url=ctx.message.author.avatar_url)
    message = await ctx.send(embed=embed)
    await message.delete(delay=15)

# Sends message that user has to respond to
async def get_input(ctx, sent, boolean=False, checkurl=False):
    await embed_send(ctx, sent)
    while True:
        msg = await client.wait_for("message")
        if msg.author == ctx.author and msg.channel == ctx.channel:
            if checkurl and check_url(msg.content) or not checkurl:
                if boolean and msg.content.lower() == 'yes':
                    await msg.delete()
                    return True
                elif boolean and msg.content.lower() == 'no':
                    await msg.delete()
                    return False
                elif boolean:
                    await embed_send(ctx, 'Type "Yes" or "No" as answer!', True)
                else:
                    inputs = msg.content
                    await msg.delete()
                    return inputs
            elif checkurl:
                await msg.delete()
                await embed_send(ctx, "Not a valid url!", True)

# When ready do stuff
@client.event
async def on_ready():
    print('Webhook Sender is ready!')
    client.loop.create_task(timers())

# When command is done delete user command message
@client.event
async def on_command_completion(ctx):
    print('{}: {}'.format(ctx.message.author, ctx.message.content))
    await ctx.message.delete()

# When error post it to server, delete if you dont want it
@client.event
async def on_command_error(ctx, error):
    print('{}: {}'.format(ctx.message.author, ctx.message.content))
    print(error)
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await embed_send(ctx, 'That command doesn\'t exist!', True)
    elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await embed_send(ctx, 'Missing arguments in command!', True)
    elif isinstance(error, discord.ext.commands.MissingPermissions):
        await embed_send(ctx,
            'You don\'t have permission "{}" to do that command!' \
            .format(','.join(error.missing_perms)), True)
    else:
        await embed_send(ctx, 'Error!\n```{}```'.format(error), True)
    await ctx.message.delete()

@client.event
async def on_message(message):
    author = message.author
    content = message.content
    await client.process_commands(message)

# Stops the bot on command... duh
@client.command(pass_context=True)
@commands.has_permissions(manage_guild=True)
async def stop(ctx):
    await embed_send(ctx, 'Stopping bot...')
    sys.exit()

# Custom help command
@client.command(pass_context=True)
async def help(ctx):
    embed=discord.Embed(title='Help:', description='This bot sends messages using webhooks.', color=0x00ff40)
    print(managejson.commands)
    for key, value in managejson.commands.items():
        embed.add_field(name=key, value=value, inline=False,)
    embed.set_author(name='Webhook Sender')
    embed.set_footer(text="Command sent by {}".format(ctx.message.author),icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)

# Sends webhook message without embed
@commands.has_permissions(manage_webhooks=True)
@client.command(pass_context=True)
async def raw(ctx,message):
    webhook.set_content(content=message)
    webhook.send()
    await embed_send(ctx, 'Message Sent.')

# Changes the hook the bot is using
@client.command(pass_context=True)
@commands.has_permissions(manage_webhooks=True)
async def sethook(ctx,hook):
    global webhook, currentHook
    hookCaps = hook.capitalize()
    if check_string(hook):
        if managejson.get(hookCaps,'name') != None:
            webhook = DiscordWebhooks(managejson.get(hookCaps,'hookURL'))
            currentHook = managejson.get(hookCaps)
            await embed_send(ctx,
                'Set webhook to {}.'.format(managejson.get(hookCaps,'name')))
        else:
            await embed_send(ctx,
                'Webhook "{}" doesn\'t exist!'.format(hookCaps), True)
    else:
        await embed_send(ctx,
        'Webhook names don\'t have special characters!', True)

# Send a message to the webhook using embed
@commands.has_permissions(manage_webhooks=True)
@client.command(pass_context=True)
async def send(ctx,title,description='',footer='',url=''):
    if webhook == None:
        await embed_send(ctx, 'No webhook set yet!', True)
    else:
        color = random.randint(0,256**3)
        thumbnail = managejson.get(currentHook, 'thumbnailURL')
        author = managejson.get(currentHook, 'title')
        webhook.set_content(title=title, description=description, color=color)
        webhook.set_author(name=author, icon_url=thumbnail)
        webhook.set_footer(text=footer, icon_url=thumbnail)
        if check_url(url) or url == '':
            webhook.set_image(url=url)
            webhook.send()
            await embed_send(ctx, 'Message sent')
        else:
            await embed_send(ctx, 'Invalid image url! Message not sent.', True)
        clear_hook()

# Shows information about the bot...
@client.command(pass_context=True)
async def info(ctx):
    names = []
    for z in range(len(managejson.hooks)):
        if managejson.hooks[z]['name']:
            names.append(managejson.hooks[z]['name'])
    embed=discord.Embed(title='Info', color=0x80ff00)
    if names == []:
        embed.add_field(name='List of all webhook names:',
            value=('There are no webhooks yet!'), inline=False)
    else:
	    embed.add_field(name='List of all webhook names:',
            value=(', '.join(names)), inline=False)
    if currentHook == None:
        embed.add_field(name='Currentry set webhook:',
            value='No hook set yet!', inline=False)
    else:
        embed.add_field(name='Currentry set webhook:',
            value='"{}" is set.'.format(managejson.get(currentHook)),
            inline=False)
    embed.add_field(name='Bot Uptime:',
        value='{} seconds'.format(uptime), inline=False)
    embed.add_field(name='Ping:',
        value='{} ms'.format(round(1000*(client.latency)), inline=False))
    embed.set_footer(text="Command sent by {}".format(ctx.message.author),
        icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)

# Deletes specified webhook in bot data (not from discord)
@client.command(pass_context=True)
@commands.has_permissions(manage_webhooks=True)
async def deletehook(ctx, hook):
    global currentHook, webhook
    hookCaps = hook.capitalize()
    if await get_input(ctx,
        "Are you sure you want to delete \"{}\"?".format(hookCaps), True):
        if currentHook == hookCaps:
            currentHook = None
            webhook = None
        if managejson.delete(hookCaps):
            await embed_send(ctx, 'Webhook "{}" deleted.'.format(hookCaps))
        else:
            await embed_send(ctx,
                'Webhook "{}" doesn\'t exist!'.format(hookCaps), True)
    else:
        await embed_send(ctx, "Command cancled", True)

# Adds hook to the bot data (doesnt create webhook)
@client.command(pass_context=True)
@commands.has_permissions(manage_webhooks=True)
async def addhook(ctx):
    with open('json/template.json') as f:
        template = json.load(f)
    await ctx.message.delete()
    if await get_input(ctx,
        "This command will add a webhook, conttinue? (yes/no)", True):
        name = await get_input(ctx, "Type a name for the webhook")
        if managejson.get(name.capitalize()) is None:
            hookURL = await get_input(ctx,
                "Copy and paste the webhook url", False, True)
            thumbnailURL = await get_input(ctx,
                "Copy and paste an image url for webhook to use", False, True)
            title = await get_input(ctx,
                "Type the text that will be sent with every message")
            template.update({'name':name.capitalize(),
                'hookURL':hookURL, 'thumbnailURL':thumbnailURL, 'title':title})
            if await get_input(ctx,'Do you want to add "{}"'.format(name),True):
                managejson.amend(template)
                await embed_send(ctx, "Webhook \"{}\" added".format(name))
            else:
                await embed_send(ctx, "Command canceled,", True)
        else:
            await embed_send(ctx, "Name is already taken", True)
    else:
        await embed_send(ctx, "Command canceled", True)

# If problem with login tell the user
try:
    client.run(TOKEN)
except discord.LoginFailure:
    print("The token is incorrect or missing! Closing in a few seconds...")
    time.sleep(10)
