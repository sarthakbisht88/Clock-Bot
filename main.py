import os
import json
import logging
import asyncio
import calendar
import discord
import pytz
import datetime
import io

from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found. Put it in .env")
DATA_DIR = os.getenv("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()])


def _path(filename):
    return os.path.join(DATA_DIR, filename)

def load_json(filename):
    try:
        with open(_path(filename), 'r', encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logging.error("Could not parse %s; starting with empty data.", filename)
        return {}

def save_json(data, filename):
    tmp = _path(filename) + ".tmp"
    with open(tmp, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, _path(filename))
    
user_data = load_json("user_timezones.json")
birthdays = load_json("birthdays.json")
server_configs = load_json("server_configs.json")
DEV_GUILD = discord.Object(id=1555168364429574217)

country_timezones = {
    'afghanistan': 'Asia/Kabul', 'albania': 'Europe/Tirane', 'algeria': 'Africa/Algiers',
    'andorra': 'Europe/Andorra', 'angola': 'Africa/Luanda', 'argentina': 'America/Argentina/Buenos_Aires',
    'armenia': 'Asia/Yerevan', 'australia': 'Australia/Sydney', 'austria': 'Europe/Vienna',
    'azerbaijan': 'Asia/Baku', 'bahamas': 'America/Nassau', 'bahrain': 'Asia/Bahrain',
    'bangladesh': 'Asia/Dhaka', 'barbados': 'America/Barbados', 'belarus': 'Europe/Minsk',
    'belgium': 'Europe/Brussels', 'belize': 'America/Belize', 'benin': 'Africa/Porto-Novo',
    'bhutan': 'Asia/Thimphu', 'bolivia': 'America/La_Paz', 'bosnia': 'Europe/Sarajevo',
    'botswana': 'Africa/Gaborone', 'brazil': 'America/Sao_Paulo', 'brunei': 'Asia/Brunei',
    'bulgaria': 'Europe/Sofia', 'burkina faso': 'Africa/Ouagadougou', 'burundi': 'Africa/Bujumbura',
    'cambodia': 'Asia/Phnom_Penh', 'cameroon': 'Africa/Douala', 'canada': 'America/Toronto',
    'cape verde': 'Atlantic/Cape_Verde', 'central african republic': 'Africa/Bangui', 'chad': 'Africa/Ndjamena',
    'chile': 'America/Santiago', 'china': 'Asia/Shanghai', 'colombia': 'America/Bogota',
    'comoros': 'Indian/Comoro', 'congo': 'Africa/Brazzaville', 'costa rica': 'America/Costa_Rica',
    'croatia': 'Europe/Zagreb', 'cuba': 'America/Havana', 'cyprus': 'Asia/Nicosia',
    'czech republic': 'Europe/Prague', 'denmark': 'Europe/Copenhagen', 'djibouti': 'Africa/Djibouti',
    'dominica': 'America/Dominica', 'dominican republic': 'America/Santo_Domingo', 'ecuador': 'America/Guayaquil',
    'egypt': 'Africa/Cairo', 'el salvador': 'America/El_Salvador', 'equatorial guinea': 'Africa/Malabo',
    'eritrea': 'Africa/Asmara', 'estonia': 'Europe/Tallinn', 'eswatini': 'Africa/Mbabane',
    'ethiopia': 'Africa/Addis_Ababa', 'fiji': 'Pacific/Fiji', 'finland': 'Europe/Helsinki',
    'france': 'Europe/Paris', 'gabon': 'Africa/Libreville', 'gambia': 'Africa/Banjul',
    'georgia': 'Asia/Tbilisi', 'germany': 'Europe/Berlin', 'ghana': 'Africa/Accra',
    'greece': 'Europe/Athens', 'grenada': 'America/Grenada', 'guatemala': 'America/Guatemala',
    'guinea': 'Africa/Conakry', 'guyana': 'America/Guyana', 'haiti': 'America/Port-au-Prince',
    'honduras': 'America/Tegucigalpa', 'hungary': 'Europe/Budapest', 'iceland': 'Atlantic/Reykjavik',
    'india': 'Asia/Kolkata', 'indonesia': 'Asia/Jakarta', 'iran': 'Asia/Tehran', 'iraq': 'Asia/Baghdad',
    'ireland': 'Europe/Dublin', 'israel': 'Asia/Jerusalem', 'italy': 'Europe/Rome',
    'jamaica': 'America/Jamaica', 'japan': 'Asia/Tokyo', 'jordan': 'Asia/Amman',
    'kazakhstan': 'Asia/Almaty', 'kenya': 'Africa/Nairobi', 'kuwait': 'Asia/Kuwait',
    'kyrgyzstan': 'Asia/Bishkek', 'laos': 'Asia/Vientiane', 'latvia': 'Europe/Riga',
    'lebanon': 'Asia/Beirut', 'lesotho': 'Africa/Maseru', 'liberia': 'Africa/Monrovia',
    'libya': 'Africa/Tripoli', 'liechtenstein': 'Europe/Vaduz', 'lithuania': 'Europe/Vilnius',
    'luxembourg': 'Europe/Luxembourg', 'madagascar': 'Indian/Antananarivo', 'malawi': 'Africa/Blantyre',
    'malaysia': 'Asia/Kuala_Lumpur', 'maldives': 'Indian/Maldives', 'mali': 'Africa/Bamako',
    'malta': 'Europe/Malta', 'mauritania': 'Africa/Nouakchott', 'mauritius': 'Indian/Mauritius',
    'mexico': 'America/Mexico_City', 'moldova': 'Europe/Chisinau', 'monaco': 'Europe/Monaco',
    'mongolia': 'Asia/Ulaanbaatar', 'montenegro': 'Europe/Podgorica', 'morocco': 'Africa/Casablanca',
    'mozambique': 'Africa/Maputo', 'myanmar': 'Asia/Yangon', 'namibia': 'Africa/Windhoek',
    'nepal': 'Asia/Kathmandu', 'netherlands': 'Europe/Amsterdam', 'new zealand': 'Pacific/Auckland',
    'nicaragua': 'America/Managua', 'niger': 'Africa/Niamey', 'nigeria': 'Africa/Lagos',
    'north korea': 'Asia/Pyongyang', 'north macedonia': 'Europe/Skopje', 'norway': 'Europe/Oslo',
    'oman': 'Asia/Muscat', 'pakistan': 'Asia/Karachi', 'palestine': 'Asia/Gaza', 'panama': 'America/Panama',
    'papua new guinea': 'Pacific/Port_Moresby', 'paraguay': 'America/Asuncion', 'peru': 'America/Lima',
    'philippines': 'Asia/Manila', 'poland': 'Europe/Warsaw', 'portugal': 'Europe/Lisbon',
    'qatar': 'Asia/Qatar', 'romania': 'Europe/Bucharest', 'russia': 'Europe/Moscow',
    'rwanda': 'Africa/Kigali', 'saudi arabia': 'Asia/Riyadh', 'senegal': 'Africa/Dakar',
    'serbia': 'Europe/Belgrade', 'singapore': 'Asia/Singapore', 'slovakia': 'Europe/Bratislava',
    'slovenia': 'Europe/Ljubljana', 'somalia': 'Africa/Mogadishu', 'south africa': 'Africa/Johannesburg',
    'south korea': 'Asia/Seoul', 'south sudan': 'Africa/Juba', 'spain': 'Europe/Madrid',
    'sri lanka': 'Asia/Colombo', 'sudan': 'Africa/Khartoum', 'suriname': 'America/Paramaribo',
    'sweden': 'Europe/Stockholm', 'switzerland': 'Europe/Zurich', 'syria': 'Asia/Damascus',
    'taiwan': 'Asia/Taipei', 'tajikistan': 'Asia/Dushanbe', 'tanzania': 'Africa/Dar_es_Salaam',
    'thailand': 'Asia/Bangkok', 'togo': 'Africa/Lome', 'trinidad and tobago': 'America/Port_of_Spain',
    'tunisia': 'Africa/Tunis', 'turkey': 'Europe/Istanbul', 'turkmenistan': 'Asia/Ashgabat',
    'uganda': 'Africa/Kampala', 'ukraine': 'Europe/Kyiv', 'united arab emirates': 'Asia/Dubai',
    'uae': 'Asia/Dubai', 'united kingdom': 'Europe/London', 'uk': 'Europe/London',
    'united states': 'America/New_York', 'usa': 'America/New_York', 'us': 'America/New_York',
    'uruguay': 'America/Montevideo', 'uzbekistan': 'Asia/Tashkent', 'venezuela': 'America/Caracas',
    'vietnam': 'Asia/Ho_Chi_Minh', 'yemen': 'Asia/Aden', 'zambia': 'Africa/Lusaka',
    'zimbabwe': 'Africa/Harare', 'antigua & barbuda': 'America/Antigua', 'anguilla': 'America/Anguilla',
    'antarctica': 'Antarctica/McMurdo', 'samoa (american)': 'Pacific/Pago_Pago', 'aruba': 'America/Aruba',
    'åland islands': 'Europe/Mariehamn', 'bosnia & herzegovina': 'Europe/Sarajevo',
    'st barthelemy': 'America/St_Barthelemy', 'bermuda': 'Atlantic/Bermuda', 'caribbean nl': 'America/Kralendijk',
    'cocos (keeling) islands': 'Indian/Cocos', 'congo (dem. rep.)': 'Africa/Kinshasa',
    'central african rep.': 'Africa/Bangui', 'congo (rep.)': 'Africa/Brazzaville', "côte d'ivoire": 'Africa/Abidjan',
    'cook islands': 'Pacific/Rarotonga', 'curaçao': 'America/Curacao', 'christmas island': 'Indian/Christmas',
    'western sahara': 'Africa/El_Aaiun', 'falkland islands': 'Atlantic/Stanley', 'micronesia': 'Pacific/Chuuk',
    'faroe islands': 'Atlantic/Faroe', 'britain (uk)': 'Europe/London', 'french guiana': 'America/Cayenne',
    'guernsey': 'Europe/Guernsey', 'gibraltar': 'Europe/Gibraltar', 'greenland': 'America/Nuuk',
    'guadeloupe': 'America/Guadeloupe', 'south georgia & the south sandwich islands': 'Atlantic/South_Georgia',
    'guam': 'Pacific/Guam', 'guinea-bissau': 'Africa/Bissau', 'hong kong': 'Asia/Hong_Kong',
    'isle of man': 'Europe/Isle_of_Man', 'british indian ocean territory': 'Indian/Chagos',
    'jersey': 'Europe/Jersey', 'kiribati': 'Pacific/Tarawa', 'st kitts & nevis': 'America/St_Kitts',
    'korea (north)': 'Asia/Pyongyang', 'korea (south)': 'Asia/Seoul', 'cayman islands': 'America/Cayman',
    'st lucia': 'America/St_Lucia', 'st martin (french)': 'America/Marigot', 'marshall islands': 'Pacific/Majuro',
    'myanmar (burma)': 'Asia/Yangon', 'macau': 'Asia/Macau', 'northern mariana islands': 'Pacific/Saipan',
    'martinique': 'America/Martinique', 'montserrat': 'America/Montserrat', 'new caledonia': 'Pacific/Noumea',
    'norfolk island': 'Pacific/Norfolk', 'nauru': 'Pacific/Nauru', 'niue': 'Pacific/Niue',
    'french polynesia': 'Pacific/Tahiti', 'st pierre & miquelon': 'America/Miquelon', 'pitcairn': 'Pacific/Pitcairn',
    'puerto rico': 'America/Puerto_Rico', 'palau': 'Pacific/Palau', 'réunion': 'Indian/Reunion',
    'solomon islands': 'Pacific/Guadalcanal', 'seychelles': 'Indian/Mahe', 'st helena': 'Atlantic/St_Helena',
    'svalbard & jan mayen': 'Arctic/Longyearbyen', 'sierra leone': 'Africa/Freetown', 'san marino': 'Europe/San_Marino',
    'sao tome & principe': 'Africa/Sao_Tome', 'st maarten (dutch)': 'America/Lower_Princes',
    'eswatini (swaziland)': 'Africa/Mbabane', 'turks & caicos is': 'America/Grand_Turk',
    'french s. terr.': 'Indian/Kerguelen', 'tokelau': 'Pacific/Fakaofo', 'east timor': 'Asia/Dili',
    'tonga': 'Pacific/Tongatapu', 'trinidad & tobago': 'America/Port_of_Spain', 'tuvalu': 'Pacific/Funafuti',
    'us minor outlying islands': 'Pacific/Midway', 'vatican city': 'Europe/Vatican', 'st vincent': 'America/St_Vincent',
    'virgin islands (uk)': 'America/Tortola', 'virgin islands (us)': 'America/St_Thomas',
    'vanuatu': 'Pacific/Efate', 'wallis & futuna': 'Pacific/Wallis', 'samoa (western)': 'Pacific/Apia',
    'mayotte': 'Indian/Mayotte'
}
MULTI_TZ_COUNTRIES = {
    'united states', 'usa', 'us', 'canada', 'russia', 'australia', 'brazil',
    'mexico', 'indonesia', 'kazakhstan', 'argentina', 'antarctica', 'greenland'
}
_TZ_LOOKUP = {tz.lower(): tz for tz in pytz.all_timezones}
_ACRONYMS = {'us', 'uk', 'usa', 'uae'}

def pretty_name(text: str) -> str:
    key = text.strip().lower()
    if key in _ACRONYMS:
        return key.upper()
    return text.strip().title()

def resolve_timezone(text: str):
    """Return (tz_object, tz_name, display_label, is_multi_tz_country) or None."""
    key = text.strip().lower()
    if key in country_timezones:
        name = country_timezones[key]
        label = pretty_name(key)
        multi = key in MULTI_TZ_COUNTRIES
    elif key in _TZ_LOOKUP:
        name = _TZ_LOOKUP[key]
        label = name.replace("_", " ")
        multi = False
    else:
        return None
    try:
        return pytz.timezone(name), name, label, multi
    except pytz.UnknownTimeZoneError:
        return None

def fmt_offset(dt: datetime.datetime) -> str:
    offset = dt.utcoffset() or datetime.timedelta(0)
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"UTC{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"

def day_period(hour: int):
    if 5 <= hour < 12:
        return "🌅 ", "Morning", discord.Color.orange()
    if 12 <= hour < 17:
        return "☀️ ", "Afternoon", discord.Color.gold()
    if 17 <= hour < 21:
        return "🌇 ", "Evening", discord.Color.purple()
    return "😴 ", "Night", discord.Color.dark_blue()

def build_time_embed(title: str, now: datetime.datetime, tz_name: str,
                     note: str = None, thumbnail: str = None) -> discord.Embed:
    emoji, period, color = day_period(now.hour)
    embed = discord.Embed(
        title=title,
        description=f"# {emoji} {now.strftime('%I:%M:%S %p')}\n**{now.strftime('%A')}** · {period}",
        color=color
    )
    embed.add_field(name="📅 Date", value=f"`{now.strftime('%B %d, %Y')}`", inline=True)
    embed.add_field(name="🧭 UTC Offset", value=f"`{fmt_offset(now)}`", inline=True)
    embed.add_field(name="🕰️ Your Time", value=f"<t:{int(now.timestamp())}:t>", inline=True)
    if note:
        embed.add_field(name="ℹ️ Note", value=note, inline=False)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=f"Timezone: {tz_name}")
    return embed

def parse_time_input(text: str):
    cleaned = text.strip().upper().replace(".", "")
    if cleaned == "NOON":
        return datetime.datetime.strptime("12:00 PM", "%I:%M %p")
    if cleaned == "MIDNIGHT":
        return datetime.datetime.strptime("12:00 AM", "%I:%M %p")
    time_formats = ["%I:%M %p", "%I:%M%p", "%I %p", "%I%p", "%H:%M"]
    for fmt in time_formats:
        try:
            return datetime.datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None

def is_birthday_today(info: dict, today: datetime.datetime) -> bool:
    day, month = info.get("day"), info.get("month")
    if day == 29 and month == 2 and not calendar.isleap(today.year):
        return today.month == 2 and today.day == 28
    return day == today.day and month == today.month

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

class ClockBot(commands.Bot):
    async def setup_hook(self) -> None:
        await self.tree.sync()
        await self.tree.sync(guild=DEV_GUILD)
        logging.info("Slash commands synced")

bot = ClockBot(command_prefix="/", intents=intents)
time_group = app_commands.Group(name="time", description="Time and timezone related commands")
timezone_group = app_commands.Group(name="timezone", description="Link or manage your timezone profile")
birthday_group = app_commands.Group(name="birthday", description="Manage and announce server birthdays.")

@tasks.loop(seconds=15)
async def rotate_status():
    statuses = [
        discord.Game(name="/help | Clock Bot"),
        discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers")
    ]
    current_status = statuses[rotate_status.current_loop % len(statuses)]
    await bot.change_presence(activity=current_status)

@rotate_status.before_loop
async def before_rotate():
    await bot.wait_until_ready()

@tasks.loop(time=datetime.time(hour=8, minute=0, tzinfo=datetime.timezone.utc))
async def announce_birthdays():
    today = datetime.datetime.now(datetime.timezone.utc)
    for user_id, bday_info in birthdays.items():
        if not is_birthday_today(bday_info, today):
            continue
        for guild_id, config in server_configs.items():
            guild = bot.get_guild(int(guild_id))
            if not guild:
                continue
            member = guild.get_member(int(user_id))
            if not member:
                continue
            channel_id = config.get("birthday_channel")
            channel = guild.get_channel(int(channel_id)) if channel_id else None
            if not channel:
                continue
            embed = discord.Embed(
                title="Happy Birthday!",
                description=f"Today is {member.mention}'s birthday! Wish them well.",
                color=discord.Color.gold()
            )
            if bday_info.get("year"):
                age = today.year - bday_info["year"]
                embed.set_footer(text=f"They are turning {age} today.")
            try:
                await channel.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

@bot.tree.command(name="servers", description="[Developer Only] List all servers the bot is in.", guild=DEV_GUILD)
@app_commands.default_permissions(administrator=True)
@app_commands.guild_only()
async def list_servers(interaction: discord.Interaction):
    if not await bot.is_owner(interaction.user):
        await interaction.response.send_message("This command does not exist.", ephemeral=True)
        return

    guilds = sorted(bot.guilds, key=lambda g: g.member_count or 0, reverse=True)
    lines = [f"• **{g.name}** (`{g.id}`) — {g.member_count} members" for g in guilds]
    description = "\n".join(lines) or "Not in any servers."

    if len(description) <= 4000:
        embed = discord.Embed(
            title=f"Connected Servers ({len(guilds)})",
            description=description,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        plain = "\n".join(f"{g.name} ({g.id}) - {g.member_count} members" for g in guilds)
        file = discord.File(io.BytesIO(plain.encode("utf-8")), filename="servers.txt")
        await interaction.response.send_message(
            f"Connected to **{len(guilds)}** servers.", file=file, ephemeral=True
        )

@announce_birthdays.before_loop
async def before_birthdays():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print(f"Clock Bot Code is working exactly as intended. Clock Bot is now online and working.")
    print(f"Connected to {len(bot.guilds)} servers")
    if not rotate_status.is_running():
        rotate_status.start()
    if not announce_birthdays.is_running():
        announce_birthdays.start()

@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    latency_ms = bot.latency * 1000
    await interaction.response.send_message(f"🏓 Latency: `{latency_ms:.2f} ms`")

@bot.tree.command(name="help", description="Display a list of all available commands and their usage.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="CLOCK Bot - Help & Command List",
        description="Here is a complete list of all available slash commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="1. Timezone & Time Commands",
        value=(
            "• `/time country [country]` — Check the local time in a specified country.\n"
            "• `/time user [user]` — Check the local time of a linked user.\n"
            "• `/time conversion [from] [time] [to]` — Convert time between two countries.\n"
            "• `/timezone set [timezone]` — Save/link your local timezone profile.\n"
            "• `/timezone remove` — Unlink and delete your saved timezone profile.\n\u200b"
        ),
        inline=False
    )
    embed.add_field(
        name="2. Date & Birthday Commands",
        value=(
            "• `/day [day] [month] [year]` — Find out what day of the week a date falls on.\n"
            "• `/birthday set [day] [month] [year]` — Save your birthday for server announcements.\n"
            "• `/birthday setup [channel]` — [Admins] Set the channel for daily birthday announcements.\n"
            "• `/birthday remove` — Remove your saved birthday.\n\u200b"
        ),
        inline=False
    )
    embed.add_field(
        name="3. Utilities",
        value=(
            "• `/time_spent [user]` — Check how long a member has been in this server.\n"
            "• `/reminder [user] [time] [unit] [message]` — Set a hidden reminder (Admins can ping others).\n"
            "• `/ping` — Check the bot's current connection latency."
        ),
        inline=False
    )
    embed.set_footer(
        text=f"Requested by {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.response.send_message(embed=embed)

async def country_autocomplete(interaction: discord.Interaction, current: str):
    current_lower = current.lower()
    matches = [
        app_commands.Choice(name=pretty_name(c)[:100], value=c)
        for c in country_timezones if current_lower in c
    ][:25]
    if len(matches) < 25 and current_lower:
        extra = [
            app_commands.Choice(name=tz[:100], value=tz)
            for tz in pytz.common_timezones if current_lower in tz.lower()
        ]
        matches.extend(extra[:25 - len(matches)])
    return matches

async def timezone_autocomplete(interaction: discord.Interaction, current: str):
    current_lower = current.lower()
    matches = [tz for tz in pytz.common_timezones if current_lower in tz.lower()][:25]
    return [app_commands.Choice(name=tz, value=tz) for tz in matches]


# time country command
@time_group.command(name="country", description="Get current time in a country.")
@app_commands.describe(country="Type country name")
@app_commands.autocomplete(country=country_autocomplete)
async def time_country(interaction: discord.Interaction, country: str):
    resolved = resolve_timezone(country)
    if not resolved:
        await interaction.response.send_message(
            f"Unknown country/timezone: `{country}`. Try typing a valid country name.",
            ephemeral=True
        )
        return
    tz, tz_name, label, multi = resolved
    now = datetime.datetime.now(tz)
    note = None
    if multi:
        note = (f"{label} spans multiple timezones. Showing `{tz_name}`. "
                "Use a timezone name (e.g. `America/Los_Angeles`) for other regions.")
    embed = build_time_embed(f"Time in {label}", now, tz_name, note=note)
    await interaction.response.send_message(embed=embed)

# time conversion command
@time_group.command(name="conversion", description="Convert time from one country to another.")
@app_commands.describe(
    from_country="Source country",
    time="Time to convert (e.g., 5:00 PM, 17:00, 5 PM)",
    to_country="Target country"
)
@app_commands.autocomplete(from_country=country_autocomplete, to_country=country_autocomplete)
async def time_conversion(interaction: discord.Interaction, from_country: str, time: str, to_country: str):
    from_resolved = resolve_timezone(from_country)
    to_resolved = resolve_timezone(to_country)

    if not from_resolved or not to_resolved:
        await interaction.response.send_message(
            "Invalid source or destination country. Please check the spelling and try again.",
            ephemeral=True
        )
        return

    from_tz, from_tz_name, from_label, from_multi = from_resolved
    to_tz, to_tz_name, to_label, to_multi = to_resolved

    parsed_time = parse_time_input(time)
    if not parsed_time:
        await interaction.response.send_message(
            "Invalid time format. Please use formats like `5:00 PM`, `5 PM`, or `17:00`.",
            ephemeral=True
        )
        return

    today = datetime.datetime.now(from_tz).date()
    local_dt = from_tz.localize(datetime.datetime.combine(today, parsed_time.time()))
    converted_dt = local_dt.astimezone(to_tz)

    input_time_str = local_dt.strftime("%I:%M %p")
    input_day = local_dt.strftime("%A")
    converted_time_str = converted_dt.strftime("%I:%M %p")
    converted_day = converted_dt.strftime("%A")

    day_shift = (converted_dt.date() - local_dt.date()).days
    if day_shift > 0:
        shift_text = "➕ Next day"
    elif day_shift < 0:
        shift_text = "➖ Previous day"
    else:
        shift_text = "Same day"

    delta = converted_dt.utcoffset() - local_dt.utcoffset()
    delta_minutes = int(delta.total_seconds() // 60)
    if delta_minutes == 0:
        diff_text = f"{to_label} and {from_label} share the same time."
    else:
        hours, mins = divmod(abs(delta_minutes), 60)
        amount = f"{hours}h" + (f" {mins}m" if mins else "")
        direction = "ahead of" if delta_minutes > 0 else "behind"
        diff_text = f"{to_label} is **{amount} {direction}** {from_label}."

    emoji, _, color = day_period(converted_dt.hour)
    embed = discord.Embed(
        title="🔄 Time Conversion",
        description=(
            f"When it is **{input_time_str}** on **{input_day}** in **{from_country.title()}**,\n"
            f"it is **{converted_time_str}** on **{converted_day}** in **{to_country.title()}**."
        ),
        color=color
    )
    embed.add_field(
        name=f"📍 {from_label}",
        value=(f"# {local_dt.strftime('%I:%M %p')}\n"
               f"{input_day}, {local_dt.strftime('%b %d')}\n"
               f"`{fmt_offset(local_dt)}`"),
        inline=True
    )
    embed.add_field(
        name=f"{emoji} {to_label}",
        value=(f"# {converted_dt.strftime('%I:%M %p')}\n"
               f"{converted_day}, {converted_dt.strftime('%b %d')}\n"
               f"`{fmt_offset(converted_dt)}`"),
        inline=True
    )
    embed.add_field(name="⏱️ Difference", value=f"{diff_text}\n{shift_text}", inline=False)
    embed.add_field(name="🕰️ In your local time", value=f"<t:{int(local_dt.timestamp())}:F>", inline=False)

    notes = []
    if from_multi:
        notes.append(f"{from_label} uses `{from_tz_name}`")
    if to_multi:
        notes.append(f"{to_label} uses `{to_tz_name}`")
    if notes:
        embed.add_field(
            name="ℹ️ Note",
            value=" · ".join(notes) + ". Use a timezone name for other regions.",
            inline=False
        )
    embed.set_footer(text=f"{from_tz_name} → {to_tz_name}")
    await interaction.response.send_message(embed=embed)

# time user command
@time_group.command(name="user", description="Get local time of a specified user.")
@app_commands.describe(user="Select user")
async def time_user(interaction: discord.Interaction, user: discord.User):
    if user.bot:
        embed = discord.Embed(
            description=f"{user.mention} is a bot. They operate from a server rack on Venus and refuse to be time-tracked by us hoomans.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    user_id = str(user.id)
    if user_id not in user_data:
        await interaction.response.send_message(
            f"**{user.display_name}** hasn't linked a timezone yet. They can use `/timezone set` to configure it.",
            ephemeral=True
        )
        return

    tz_str = user_data[user_id]
    try:
        user_tz = pytz.timezone(tz_str)
    except pytz.UnknownTimeZoneError:
        await interaction.response.send_message(
            f"**{user.display_name}** has an invalid timezone saved. They should run `/timezone set` again.",
            ephemeral=True
        )
        return

    now = datetime.datetime.now(user_tz)
    embed = build_time_embed(
        f"🕒 Time for {user.display_name}",
        now,
        tz_str,
        thumbnail=user.display_avatar.url
    )
    await interaction.response.send_message(embed=embed)

@timezone_group.command(name="set", description="Link your account to a timezone.")
@app_commands.describe(timezone="Select or type your timezone (e.g., Asia/Kolkata, America/New_York, UTC)")
@app_commands.autocomplete(timezone=timezone_autocomplete)
async def timezone_set(interaction: discord.Interaction, timezone: str):
    if timezone not in pytz.all_timezones:
        await interaction.response.send_message(
            "Invalid timezone detected. Please use a standard TZ database name (e.g., `Asia/Kolkata`, `America/New_York`).\n"
            "> You can find a complete list of valid timezones here: [Wikipedia TZ List](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)",
            ephemeral=True,
            suppress_embeds=True
        )
        return
    user_data[str(interaction.user.id)] = timezone
    save_json(user_data, "user_timezones.json")

    await interaction.response.send_message(
        f"Your timezone profile has been successfully linked to **{timezone}**.\n"
        "> Other users in this server can now use `/time user` to check your local time before messaging you.",
        ephemeral=True
    )

@timezone_group.command(name="remove", description="Remove your saved timezone link.")
async def timezone_remove(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in user_data:
        del user_data[user_id]
        save_json(user_data, "user_timezones.json")
        await interaction.response.send_message("Your linked timezone profile has been successfully removed.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not currently have a timezone linked to your account.", ephemeral=True)

@bot.tree.command(name="day", description="Check what day of the week a date falls on.")
@app_commands.describe(day="Day (1-31)", month="Month (1-12)", year="Year (e.g., 2004)")
async def day_command(interaction: discord.Interaction, day: int, month: int, year: int):
    try:
        dt = datetime.datetime(year, month, day)
        embed = discord.Embed(
            description=f"**{dt.strftime('%d %B %Y')}** falls on a **{dt.strftime('%A')}**.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    except ValueError:
        await interaction.response.send_message(
            "Invalid date provided. Please check the day, month, and year and try again.",
            ephemeral=True
        )

@birthday_group.command(name="set", description="Save your birthday to be announced.")
@app_commands.describe(day="Day (1-31)", month="Month (1-12)", year="Year (Optional)")
async def bday_set(interaction: discord.Interaction, day: int, month: int, year: int = None):
    try:
        check_year = year if year else 2000  
        datetime.datetime(check_year, month, day)

        birthdays[str(interaction.user.id)] = {"day": day, "month": month, "year": year}
        save_json(birthdays, "birthdays.json")

        embed = discord.Embed(
            description=f"Your birthday has been saved. It will be celebrated on **{month}/{day}**.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except ValueError:
        await interaction.response.send_message(
            "Invalid date provided. Please check the day and month and try again.",
            ephemeral=True
        )

@birthday_group.command(name="setup", description="[Admins Only] Set the channel for birthday announcements.")
@app_commands.describe(channel="The text channel to send birthday announcements in.")
@app_commands.default_permissions(manage_guild=True)
async def bday_setup(interaction: discord.Interaction, channel: discord.TextChannel):

    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True
        )
        return

    perms = interaction.user.guild_permissions if isinstance(interaction.user, discord.Member) else None
    if not perms or not (perms.manage_guild or perms.administrator):
        await interaction.response.send_message(
            "You need the **Manage Server** permission to use this command.",
            ephemeral=True
        )
        return

    server_configs[str(interaction.guild_id)] = {"birthday_channel": channel.id}
    save_json(server_configs, "server_configs.json")

    embed = discord.Embed(
        description=f"Birthday announcements for this server will now be sent in {channel.mention}.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@birthday_group.command(name="remove", description="Remove your saved birthday.")
async def bday_remove(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in birthdays:
        del birthdays[user_id]
        save_json(birthdays, "birthdays.json")
        embed = discord.Embed(
            description="Your birthday has been successfully removed from the system.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("You do not currently have a birthday saved.", ephemeral=True)

# reminder command
@bot.tree.command(name="reminder", description="Set a timer-based reminder.")
@app_commands.describe(
    user="User to ping (Admins can ping others)",
    time="Duration amount",
    unit="Time unit",
    message="Reminder message (Hidden until time is up)"
)
@app_commands.choices(unit=[
    app_commands.Choice(name="Seconds", value="seconds"),
    app_commands.Choice(name="Minutes", value="minutes"),
    app_commands.Choice(name="Hours", value="hours")
])
async def reminder(
    interaction: discord.Interaction,
    user: discord.User,
    time: float,
    unit: app_commands.Choice[str],
    message: str
):
    if time <= 0:
        await interaction.response.send_message(
            "Duration must be greater than 0.",
            ephemeral=True
        )
        return

    if user.bot:
        embed = discord.Embed(
            description=f"I tried to schedule this for {user.mention}, but they appear to be stuck in Do Not Disturb mode... actually, they're a bot. We run on code, not reminders!",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    is_admin = False
    if interaction.guild and isinstance(interaction.user, discord.Member):
        is_admin = interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_guild

    if not is_admin and user.id != interaction.user.id:
        await interaction.response.send_message(
            "You do not have permission to set reminders for other people. You can only select yourself!",
            ephemeral=True
        )
        return

    unit_seconds = {"seconds": 1, "minutes": 60, "hours": 3600}
    total_seconds = time * unit_seconds[unit.value]

    embed = discord.Embed(
        description=f"Reminder successfully created for {user.mention} in **{time} {unit.name.lower()}**.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)
    await asyncio.sleep(total_seconds)
    if interaction.channel:
        try:
            await interaction.channel.send(
                content=f"🔔 {user.mention} **Reminder:** {message}",
                allowed_mentions=discord.AllowedMentions(users=[user])
            )
        except (discord.Forbidden, discord.HTTPException):
            logging.warning("Could not deliver reminder in channel %s", interaction.channel.id)

# time spent command
@bot.tree.command(name="time_spent", description="Check how long a member has been in this server.")
@app_commands.describe(user="User to check (defaults to you)")
async def time_spent(interaction: discord.Interaction, user: discord.Member = None):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True
        )
        return
    target_user = user or interaction.user
    if not isinstance(target_user, discord.Member) or not target_user.joined_at:
        await interaction.response.send_message(
            f"Could not retrieve join date for {target_user.display_name}.",
            ephemeral=True
        )
        return
    joined_at = target_user.joined_at
    now = datetime.datetime.now(joined_at.tzinfo)
    duration = now - joined_at
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    embed = discord.Embed(
        title=f"Server Time: {target_user.display_name}",
        description=f"Joined on **{joined_at.strftime('%B %d, %Y')}**",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=target_user.display_avatar.url)
    embed.add_field(
        name="Total Time Spent",
        value=f"`{days} days, {hours} hours, and {minutes} minutes`",
        inline=False
    )
    await interaction.response.send_message(embed=embed)

bot.tree.add_command(time_group)
bot.tree.add_command(timezone_group)
bot.tree.add_command(birthday_group)

bot.run(TOKEN, log_handler=None)