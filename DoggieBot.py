import discord
from discord.ext import commands
import asyncio
from itertools import cycle

token = 'NTI3MjcwMDExNzE5NTE2MTc0.DwRSWQ.o_YM13B_-vUtHbja9cxFlInF3Os'
client = commands.Bot(command_prefix = 'doggie ')
client.remove_command('help')
status = ['Licc time', 'for you ;3','use \'doggie addcolor {color)\'', 'or \'doggie removecolor {color}\'']

async def change_status():
	await client.wait_until_ready()
	msg = cycle(status)
	
	while not client.is_closed:
		current_status = next(msg)
		await client.change_presence(game=discord.Game(name=current_status))
		await asyncio.sleep(3)

@client.event
async def on_ready():
	print('DoggieBot is Ready!')
	
@client.event
async def on_member_join(member):
	role = discord.utils.get(member.server.roles, name='Member')
	messageChannel = discord.utils.get(member.server.channels, name='new-members')
	mention = member.mention
	serverName = member.server.name
	await client.add_roles(member, role)
	await client.send_message(messageChannel, 'Welcome {} to the {}!'.format(mention, serverName) )
	
@client.command(pass_context=True)
async def addcolor(ctx, color):
	
	channel = ctx.message.channel
	await client.send_typing(channel)
	author = ctx.message.author
	role = discord.utils.get(ctx.message.server.roles, name=color.capitalize())
	try:
		await client.add_roles(author, role)
		await client.say('Color Added')
	except discord.Forbidden:
		await client.say('Not a valid color role!')
	except AttributeError:
		await client.say('This color role doesn\'t exist! (check spelling, or the color list!)')
	
@client.command(pass_context=True)
async def removecolor(ctx, color):
	channel = ctx.message.channel
	await client.send_typing(channel)
	author = ctx.message.author
	role = discord.utils.get(ctx.message.server.roles, name=color.capitalize())
	try:
		await client.remove_roles(author, role)
		await client.say('Color Removed')
	except discord.Forbidden:
		await client.say('Not a valid color role!')
	except AttributeError:
		await client.say('This color role doesn\'t exist! (check spelling, or the color list!)')
	
@client.command(pass_context=True)
@commands.has_permissions(administartor=True)
async def logout():
	await client.logout()
	
@client.command(pass_context=True)
async def licc(ctx):
	channel = ctx.message.channel
	mention = ctx.message.author.mention
	await client.send_typing(channel)
	await client.say('*liccs {}*'.format(mention))
	print(ctx.message.author)

@client.command(pass_context=True)
async def liccdae(ctx):
	channel = ctx.message.channel
	await client.send_typing(channel)
	await client.say('*liccs <@229803640888623104>*')
	

client.loop.create_task(change_status())
	
client.run(token)