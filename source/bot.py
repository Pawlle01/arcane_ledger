import discord
import aiohttp, asyncio
import os
from dotenv import load_dotenv
import time
from discord.ext import commands

# Vars

# Bot Token
load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    raise RuntimeError("BOT_TOKEN not set")

# Intents 
intents = discord.Intents.default()
intents.message_content = True

print("Message Content Intent:", intents.message_content)
print("Presences Intent:", intents.presences)
print("Members Intent:", intents.members)


# Prefix 
bot = commands.Bot(command_prefix="ledger!", intents=intents, case_insensitive=True)

# Connect to VC
async def connect_to_vc(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Please join a voice channel and try again.")
            return
    
    channel = ctx.author.voice.channel

    return await channel.connect(self_deaf=False)


# Listening Start
@bot.command()
async def start(ctx):

    voice_client = await connect_to_vc(ctx)
    if not voice_client:
        return

    # Listen to audio, save to wav file per user

    sink = discord.sinks.WaveSink()

    voice_client.start_recording(
        sink,
        finished_callback,
        ctx
    )

    await ctx.send("Notetaking started.")

# Listening Stop
@bot.command()
async def stop(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_recording():
        await ctx.send("Not recording.")
        return

    ctx.voice_client.stop_recording()

    await ctx.send("Notetaking stopped.")


# Callback
async def finished_callback(sink: discord.sinks.WaveSink, ctx):
    date = time.strftime("%Y-%m-%d")
    out_dir = os.path.join("recordings", date)
    os.makedirs(out_dir, exist_ok=True)

    for user_id, audio in sink.audio_data.items():
        user = ctx.guild.get_member(user_id)
        name = user.display_name if user else str(user_id)

        filename = os.path.join(out_dir, f"{name}-{user_id}.wav")
        with open(filename, "wb") as f:
            f.write(audio.file.getbuffer())

        print(f"Saved {filename}")

    await ctx.voice_client.disconnect()

# Misc, Logging, Tools
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello World! I am Arcane Ledger.")



#Temporarily in here 
bot.run(bot_token)