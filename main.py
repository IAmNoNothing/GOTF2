import asyncio
import discord
from discord.ext import commands
from openai import OpenAI
import pickle
import threading
import time

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
modes = {'gotf2': set(), 'admins': {'stratofortress_b52'}, 'ignore': {'buvav'}, 'separ': set()}

try:
    with open("data.pkl", "rb") as f:
        modes = pickle.load(f)

    if 'gotf2' not in modes:
        modes['gotf2'] = set()
    if 'admins' not in modes:
        modes['admins'] = {'stratofortress_b52'}
    if 'ignore' not in modes:
        modes['ignore'] = {'buvav'}
    if 'separ' not in modes:
        modes['separ'] = set()

except Exception as e:
    print(e)

with open("openai.txt", "r") as f:
    client = OpenAI(api_key=f.read())


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def gotf2(ctx):
    if ctx.message.author.name not in modes['admins']:
        await ctx.send('ю аре нот едмін, пліс сак пінес оф адмін ту юз зіс комманд')
        return
    if not ctx.message.mentions:
        await ctx.send('Usage: !gotf2 @username <on/off>')
        return

    mentioned_user = ctx.message.mentions[0]
    on_off = ctx.message.content.split(' ')[-1]

    if mentioned_user.name == "GOTF2":
        await ctx.send('ті лох')
        return

    if on_off == 'on':
        modes['gotf2'].add(mentioned_user.name)
        await ctx.send(f'GoTF2 activated for {mentioned_user.name}')
    elif on_off == 'off':
        if mentioned_user.name in modes['gotf2']:
            modes['gotf2'].remove(mentioned_user.name)
        await ctx.send(f'GoTF2 deactivated for {mentioned_user.name}')
    else:
        await ctx.send('Usage: !gotf2 @username <on/off>')


@bot.command()
async def admin(ctx):
    if ctx.message.author.name not in modes['admins']:
        await ctx.send('ю аре нот едмін, пліс сак пінес оф адмін ту юз зіс комманд')
        return
    if not ctx.message.mentions:
        await ctx.send('Usage: !admin @username <add/remove>')
        return

    mentioned_user = ctx.message.mentions[0]
    on_off = ctx.message.content.split(' ')[-1]

    if on_off == 'add':
        modes['admins'].add(mentioned_user.name)
        await ctx.send(f'Admin added: {mentioned_user.name}')
    elif on_off == 'remove':
        if mentioned_user.name in admins:
            modes['admins'].remove(mentioned_user.name)
        await ctx.send(f'Admin removed: {mentioned_user.name}')
    else:
        await ctx.send('Usage: !admin @username <add/remove>')


@bot.command()
async def admins(ctx):
    await ctx.send(', '.join(modes['admins']))


@bot.command()
async def separ(ctx):
    if ctx.message.author.name not in modes['admins']:
        await ctx.send('ю аре нот едмін, пліс сак пінес оф адмін ту юз зіс комманд')
        return
    if not ctx.message.mentions:
        await ctx.send('Usage: !separ @username <on/off>')
        return

    mentioned_user = ctx.message.mentions[0]
    on_off = ctx.message.content.split(' ')[-1]

    if mentioned_user.name == "GOTF2":
        await ctx.send('ті лох')
        return

    if on_off == 'on':
        modes['separ'].add(mentioned_user.name)
        await ctx.send(f'Separ activated for {mentioned_user.name}')
    elif on_off == 'off':
        if mentioned_user.name in modes['separ']:
            modes['separ'].remove(mentioned_user.name)
        await ctx.send(f'Separ deactivated for {mentioned_user.name}')
    else:
        await ctx.send('Usage: !separ @username <on/off>')


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


@bot.command()
async def calc(ctx):
    try:
        expr = ctx.message.content[len('!calc '):]
        if 'exec' in expr:
            await ctx.send('`exec` is not allowed')
            return
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(loop.run_in_executor(None, eval, expr), timeout=1.0)

        await ctx.send(str(result))
    except asyncio.TimeoutError:
        await ctx.send('Timeout!')
    except Exception as e:
        await ctx.send(f"Error: {e}")


@bot.command()
async def chat(ctx):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "Ти діскорд-бот."},
            {"role": "user", "content": f"Користувач {ctx.message.author.name} написав: {ctx.message.content}"}
        ]
    )

    await ctx.send(completion.choices[0].message.content)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.name in modes['gotf2']:
        await message.channel.send(f'{message.author.mention} gotf2')

    if message.author.name in modes['separ']:
        await message.channel.send(f'ті сепар {message.author.mention}')

    if message.author.name in modes['ignore']:
        return

    await bot.process_commands(message)


def save_modes():
    while True:
        time.sleep(60)
        with open("data.pkl", "wb") as _f:
            pickle.dump(modes, _f)


threading.Thread(target=save_modes).start()


with open("discord.txt") as f:
    token = f.read()

bot.run(token)
