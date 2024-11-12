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
modes = {}
ignore = {}
admins_list = {'stratofortress_b52'}

try:
    with open("data.pkl", "rb") as f:
        admins_list, modes = pickle.load(f)
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
async def mode(ctx, fmt: str, _mode: str, user: discord.Member):
    if ctx.message.author.name not in admins_list:
        await ctx.send("You're not an admin!")
        return

    fmt = fmt.replace('_', ' ')
    user = user.name

    if fmt not in modes:
        modes[fmt] = set()

    if _mode == "on":
        modes[fmt].add(user)
        await ctx.send(f"{fmt.replace('{}', user)}'ing {user}")
    elif _mode == "off":
        modes[fmt].discard(user)
        await ctx.send(f"stopped {fmt.replace('{}', user)}'ing {user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for fmt, users in modes.items():
        if message.author.name in users:
            await message.channel.send(fmt.replace('{}', message.author.mention))

    if message.author.name not in ignore:
        await bot.process_commands(message)


@bot.command()
async def admins(ctx):
    if admins_list:
        admin_list = ', '.join(admins_list)
        await ctx.send(f"Current admins: {admin_list}")
    else:
        await ctx.send("No admins available.")


@bot.command()
async def admin(ctx, action: str, member: discord.Member):
    if ctx.message.author.name not in admins_list:
        await ctx.send("You're not an admin!")
        return

    if action not in ("add", "remove"):
        await ctx.send("Usage: !admin <add/remove> <@user>")
        return

    if action == "add":
        admins_list.add(member.name)
        await ctx.send(f"{member.name} was added to the admins.")
    elif action == "remove":
        if member.name in admins_list:
            admins_list.remove(member.name)
            await ctx.send(f"{member.name} was removed from the admins.")
        else:
            await ctx.send(f"{member.name} is not an admin.")


def save_modes():
    while True:
        time.sleep(60)
        with open("data.pkl", "wb+") as _f:
            pickle.dump([admins_list, modes], _f)


threading.Thread(target=save_modes).start()

with open("discord.txt") as f:
    token = f.read()

bot.run(token)
