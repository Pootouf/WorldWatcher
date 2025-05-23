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


def get_channel_env(var_name):
    value = os.getenv(var_name)
    return int(value) if value is not None else None


surface_temperature_channel: int | None = get_channel_env("CHANNEL_SURFACE_TEMPERATURE")
surface_temperature_map_channel: int | None = get_channel_env("CHANNEL_SURFACE_TEMPERATURE_MAP")
sea_temperature_channel: int | None = get_channel_env("CHANNEL_SEA_TEMPERATURE")
sea_temperature_map_channel: int | None = get_channel_env("CHANNEL_SEA_TEMPERATURE_MAP")
ice_volume_channel: int | None = get_channel_env("CHANNEL_ICE_VOLUME")
ice_volume_map_channel: int | None = get_channel_env("CHANNEL_ICE_VOLUME_MAP")
co2_graph_channel: int | None = get_channel_env("CHANNEL_CO2_GRAPH")
greenland_surface_channel: int | None = get_channel_env("CHANNEL_GREENLAND_SURFACE")
greenland_melt_channel: int | None = get_channel_env("CHANNEL_GREENLAND_MELT")
antarctic_sea_ice_extent_graph: int | None = get_channel_env("CHANNEL_ANTARCTIC_SEA_ICE_EXTENT_GRAPH")
antarctic_sea_ice_extent_map: int | None = get_channel_env("CHANNEL_ANTARCTIC_SEA_ICE_EXTENT_MAP")
antarctic_sea_ice_concentration_map: int | None = get_channel_env("CHANNEL_ANTARCTIC_SEA_ICE_CONCENTRATION_MAP")


async def wait_until(hour: int, minute: int = 0):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    print(f"Waiting until {target} to start tasks.")
    print(f"Current time: {now}")
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
    await wait_until(20)
    print("Bot is ready.")
    update_surface_temperature.start()
    update_surface_temperature_map.start()
    update_sea_temperature.start()
    update_sea_temperature_map.start()
    update_ice_volume.start()
    update_co2_graph.start()
    update_ice_volume_map.start()
    update_greenland_surface.start()
    update_greenland_melt.start()
    update_antarctic_sea_ice_concentration_map.start()
    update_antarctic_sea_ice_extent_map.start()
    update_antarctic_sea_ice_extent_graph.start()


@tasks.loop(hours=24)
async def update_surface_temperature():
    if surface_temperature_channel is None:
        return
    print("Updating surface temperature...")
    channel = client.get_channel(surface_temperature_channel)
    date_str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/timeseries/era5_daily_series_2t_global_{date_str}.png"
    filename = f"surface_temperature_{date_str}.png"
    await send_image_or_link(channel, link, "Graphique des températures de surface mise à jour :", filename)


@tasks.loop(hours=24)
async def update_surface_temperature_map():
    if surface_temperature_map_channel is None:
        return
    print("Updating surface temperature map...")
    channel = client.get_channel(surface_temperature_map_channel)
    date_str = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/maps/download/daily/2t/anomaly/2025/climpulse_map_era5_download_daily_2t_anomaly_{date_str}.png"
    filename = f"surface_temperature_map_{date_str}.png"
    await send_image_or_link(channel, link, "Map des températures de surface mise à jour :", filename)


@tasks.loop(hours=24)
async def update_sea_temperature():
    if sea_temperature_channel is None:
        return
    print("Updating sea temperature...")
    channel = client.get_channel(sea_temperature_channel)
    date_str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/timeseries/era5_daily_series_sst_60S-60N_ocean_{date_str}.png"
    filename = f"sea_temperature_{date_str}.png"
    await send_image_or_link(channel, link, "Graphique des températures de l'océan mise à jour :", filename)


@tasks.loop(hours=24)
async def update_sea_temperature_map():
    if sea_temperature_map_channel is None:
        return
    print("Updating sea temperature map...")
    channel = client.get_channel(sea_temperature_map_channel)
    date_str = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
    link = f"https://sites.ecmwf.int/data/climatepulse/maps/download/daily/sst/anomaly/2025/climpulse_map_era5_download_daily_sst_anomaly_{date_str}.png"
    filename = f"sea_temperature_map_{date_str}.png"
    await send_image_or_link(channel, link, "Map des températures de l'océan mise à jour :", filename)


@tasks.loop(hours=24)
async def update_ice_volume():
    if ice_volume_channel is None:
        return
    print("Updating ice volume...")
    channel = client.get_channel(ice_volume_channel)
    date_str = datetime.now().strftime("%Y%m%d")
    link = f"https://polarportal.dk/fileadmin/polarportal/sea/CICE_curve_thick_LA_EN_{date_str}.png"
    filename = f"ice_volume_{date_str}.png"
    await send_image_or_link(channel, link, "Graphique du volume de glace arctique :", filename)


@tasks.loop(hours=24)
async def update_ice_volume_map():
    if ice_volume_map_channel is None:
        return
    print("Updating ice volume map...")
    channel = client.get_channel(ice_volume_map_channel)
    date_str = datetime.now().strftime("%Y%m%d")
    link = f"https://polarportal.dk/fileadmin/polarportal/sea/CICE_map_thick_LA_EN_{date_str}.png"
    filename = f"ice_volume_map_{date_str}.png"
    await send_image_or_link(channel, link, "Map du volume de glace arctique :", filename)


@tasks.loop(hours=24)
async def update_greenland_surface():
    if greenland_surface_channel is None:
        return
    print("Updating Greenland surface stats...")
    channel = client.get_channel(greenland_surface_channel)
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    link = f"https://polarportal.dk/fileadmin/polarportal/surface/SMB_combine_SM_day_EN_{date_str}.png"
    filename = f"greenland_surface_{date_str}.png"
    await send_image_or_link(channel, link, "Informations sur les conditions de surface de la glace du Groenland :", filename)


@tasks.loop(hours=24)
async def update_greenland_melt():
    if greenland_melt_channel is None:
        return
    print("Updating Greenland melt stats...")
    channel = client.get_channel(greenland_melt_channel)
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    link = f"https://polarportal.dk/fileadmin/polarportal/meltarea/MELTA_combine_SM_EN_{date_str}.png"
    filename = f"greenland_melt_{date_str}.png"
    await send_image_or_link(channel, link, "Informations sur la surface de fonte de la glace du Groenland :", filename)


@tasks.loop(hours=24)
async def update_antarctic_sea_ice_extent_graph():
    if antarctic_sea_ice_extent_graph is None:
        return
    print("Updating Antarctic sea ice extent graph...")
    channel = client.get_channel(antarctic_sea_ice_extent_graph)
    link = "https://nsidc.org/data/seaice_index/images/daily_images/S_iqr_timeseries.png"
    filename = "antarctic_sea_ice_extent.png"
    await send_image_or_link(channel, link, "Graphique sur l'extension de la mer de glace Antarctique :", filename)


@tasks.loop(hours=24)
async def update_antarctic_sea_ice_extent_map():
    if antarctic_sea_ice_extent_map is None:
        return
    print("Updating Antarctic sea ice extent map...")
    channel = client.get_channel(antarctic_sea_ice_extent_map)
    link = "https://nsidc.org/data/seaice_index/images/daily_images/S_daily_extent_hires.png"
    filename = "antarctic_sea_ice_extent_map.png"
    await send_image_or_link(channel, link, "Map de l'extension de la mer de glace Antarctique :", filename)


@tasks.loop(hours=24)
async def update_antarctic_sea_ice_concentration_map():
    if antarctic_sea_ice_concentration_map is None:
        return
    print("Updating Antarctic sea ice extent map...")
    channel = client.get_channel(antarctic_sea_ice_extent_map)
    link = "https://nsidc.org/data/seaice_index/images/daily_images/S_daily_concentration_hires.png"
    filename = "antarctic_sea_ice_concentration_map.png"
    await send_image_or_link(channel, link, "Map de la concentration de la mer de glace Antarctique :", filename)


@tasks.loop(hours=24)
async def update_co2_graph():
    if co2_graph_channel is None:
        return
    print("Updating CO2 graph...")
    channel = client.get_channel(co2_graph_channel)
    link = "https://scripps.ucsd.edu/bluemoon/co2_400/mlo_two_years.png"
    filename = f"co2_graph.png"
    await send_image_or_link(channel, link, "Graphique de la concentration en CO2 :", filename)


TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)
