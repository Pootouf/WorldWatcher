import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks
import discord
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

intents = discord.Intents.default()
client = discord.Client(intents=intents)

load_dotenv()
surface_temperature_channel: int | None = int(os.getenv("CHANNEL_SURFACE_TEMPERATURE"))
surface_temperature_map_channel: int | None = int(os.getenv("CHANNEL_SURFACE_TEMPERATURE_MAP"))
sea_temperature_channel: int | None = int(os.getenv("CHANNEL_SEA_TEMPERATURE"))
sea_temperature_map_channel: int | None = int(os.getenv("CHANNEL_SEA_TEMPERATURE_MAP"))
ice_volume_channel: int | None = int(os.getenv("CHANNEL_ICE_VOLUME"))
co2_graph_channel: int | None = int(os.getenv("CHANNEL_CO2_GRAPH"))


async def wait_until(hour: int, minute: int = 0):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())


class UnsafeTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT:HIGH:!DH:!aNULL')
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx,
            **pool_kwargs
        )


async def send_image_or_link(channel, link, message, filename):
    try:
        session = requests.Session()
        session.mount('https://', UnsafeTLSAdapter())
        response = session.get(link)
        print(response.status_code)
        print(response.headers.get("Content-Type", ""))
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("image"):
            image_bytes = BytesIO(response.content)
            file = discord.File(fp=image_bytes, filename=filename)
            await channel.send(content=message, file=file)
        else:
            await channel.send(f"{message} {link}")
    except Exception as e:
        print(f"Exception lors du téléchargement ou de l'envoi de l'image : {e}")
        await channel.send(f"{message} {link}")


@client.event
async def on_ready():
    await wait_until(8)
    update_surface_temperature.start()
    update_surface_temperature_map.start()
    update_sea_temperature.start()
    update_sea_temperature_map.start()
    update_ice_volume.start()
    update_co2_graph.start()


@tasks.loop(hours=24)
async def update_surface_temperature():
    if surface_temperature_channel is None:
        return
    channel = client.get_channel(surface_temperature_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/timeseries/era5_daily_series_2t_global_{date_str}.png"
    filename = f"surface_temperature_{date_str}.png"
    await send_image_or_link(channel, link, "Graphique des températures de surface mise à jour :", filename)


@tasks.loop(hours=24)
async def update_surface_temperature_map():
    if surface_temperature_map_channel is None:
        return
    channel = client.get_channel(surface_temperature_map_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y%m%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/maps/download/daily/2t/anomaly/2025/climpulse_map_era5_download_daily_2t_anomaly_{date_str}.png"
    filename = f"surface_temperature_map_{date_str}.png"
    await send_image_or_link(channel, link, "Map des températures de surface mise à jour :", filename)


@tasks.loop(hours=24)
async def update_sea_temperature():
    if sea_temperature_channel is None:
        return
    channel = client.get_channel(sea_temperature_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/timeseries/era5_daily_series_sst_60S-60N_ocean_{date_str}.png"
    filename = f"sea_temperature_{date_str}.png"
    await send_image_or_link(channel, link, "Graphique des températures de l'océan mise à jour :", filename)


@tasks.loop(hours=24)
async def update_sea_temperature_map():
    if sea_temperature_map_channel is None:
        return
    channel = client.get_channel(sea_temperature_map_channel)
    date_str = (datetime.now() - timedelta(days=4)).strftime("%Y%m%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/maps/download/daily/sst/anomaly/2025/climpulse_map_era5_download_daily_sst_anomaly_{date_str}.png"
    filename = f"sea_temperature_map_{date_str}.png"
    await send_image_or_link(channel, link, "Map des températures de l'océan mise à jour :", filename)


@tasks.loop(hours=24)
async def update_ice_volume():
    if ice_volume_channel is None:
        return
    channel = client.get_channel(ice_volume_channel)
    date_str = datetime.now().strftime("%Y%m%d")
    link = f"https://polarportal.dk/fileadmin/polarportal/sea/CICE_curve_thick_LA_EN_{date_str}.png"
    filename = f"ice_volume_{date_str}.png"
    await send_image_or_link(channel, link, "Graphique du volume de glace arctique :", filename)


@tasks.loop(hours=24)
async def update_co2_graph():
    if co2_graph_channel is None:
        return
    channel = client.get_channel(co2_graph_channel)
    link = "https://scripps.ucsd.edu/bluemoon/co2_400/mlo_two_years.png"
    filename = f"co2_graph.png"
    await send_image_or_link(channel, link, "Graphique de la concentration en CO2", filename)


TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)
