import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks
import discord
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
client = discord.Client(intents=intents)

load_dotenv()
surface_temperature_channel: int | None = int(os.getenv("CHANNEL_SURFACE_TEMPERATURE"))
surface_temperature_map_channel: int | None = int(os.getenv("CHANNEL_SURFACE_TEMPERATURE_MAP"))
sea_temperature_channel: int | None = int(os.getenv("CHANNEL_SEA_TEMPERATURE"))
sea_temperature_map_channel: int | None = int(os.getenv("CHANNEL_SEA_TEMPERATURE_MAP"))

async def wait_until(hour: int, minute: int = 0):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())


@client.event
async def on_ready():
    #await wait_until(8)
    update_surface_temperature.start()
    update_surface_temperature_map.start()
    update_sea_temperature.start()
    update_sea_temperature_map.start()


@tasks.loop(hours=24)
async def update_surface_temperature():
    if surface_temperature_channel is None:
        return
    channel = client.get_channel(surface_temperature_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/timeseries/era5_daily_series_2t_global_{date_str}.png"
    await channel.send(f"Graphique des températures de surface mise à jour: {link}")


@tasks.loop(hours=24)
async def update_surface_temperature_map():
    if surface_temperature_map_channel is None:
        return
    channel = client.get_channel(surface_temperature_map_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y%m%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/maps/download/daily/2t/anomaly/2025/climpulse_map_era5_download_daily_2t_anomaly_{date_str}.png"
    await channel.send(f"Map des températures de surface mise à jour: {link}")


@tasks.loop(hours=24)
async def update_sea_temperature():
    if sea_temperature_channel is None:
        return
    channel = client.get_channel(sea_temperature_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/timeseries/era5_daily_series_sst_60S-60N_ocean_{date_str}.png"
    await channel.send(f"Graphique des températures de l'océan mise à jour: {link}")


@tasks.loop(hours=24)
async def update_sea_temperature_map():
    if sea_temperature_map_channel is None:
        return
    channel = client.get_channel(sea_temperature_map_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y%m%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/maps/download/daily/sst/anomaly/2025/climpulse_map_era5_download_daily_sst_anomaly_{date_str}.png"
    await channel.send(f"Map des températures de l'océan mise à jour: {link}")


TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)
