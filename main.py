import asyncio
import discord
from discord.ext import commands
from openai import OpenAI
import pickle
import threading
import time
import re

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
modes = {}


try:
    with open("data.pkl", "rb") as f:
        modes, modes_fmt = pickle.load(f)
except Exception as e:
    print(e)


with open("openai.txt", "r") as f:
    client = OpenAI(api_key=f.read())


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


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
            {"role": "user", "content": ctx.message.content}
        ]
    )

    await ctx.send(completion.choices[0].message.content)


@bot.command()
async def mode(ctx):
    match = re.match(r"!mode ([\w_{}]+) (on|off) (<@\d+>)", ctx.message.content)
    if match:
        fmt, _mode, _ = match.groups()
        fmt = fmt.replace('_', ' ')
        user = ctx.message.mentions[0].name

        if fmt not in modes:
            modes[fmt] = set()

        if _mode == "on":
            modes[fmt].add(user)
        elif _mode == "off":
            modes[fmt].discard(user)
    else:
        await ctx.send("Usage: !mode <fmt> <on|off> <@user>")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for fmt, users in modes.items():
        if message.author.name in users:
            await message.channel.send(fmt.replace('{}', message.author.mention))

    await bot.process_commands(message)


def save_modes():
    while True:
        time.sleep(60)
        with open("data.pkl", "wb") as _f:
            pickle.dump([modes, modes_fmt], _f)


threading.Thread(target=save_modes).start()


with open("discord.txt") as f:
    token = f.read()

bot.run(token)
