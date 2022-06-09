import datetime as dt
import sqlitedict
import hikari
import lightbulb
from lightbulb.ext import tasks

import config as c


plugin = lightbulb.Plugin("activity")
db = sqlitedict.SqliteDict(c.config["db"], tablename=str(c.config["guild"]), autocommit=True)


# Check every minute if inactive
@tasks.task(s=60)
async def check_activity():
    for author_id, timestamp in db.items():
        if dt.datetime.now(dt.timezone.utc) - timestamp >= dt.timedelta(seconds=c.config["duration"]):
            member = plugin.bot.cache.get_member(c.config["guild"], author_id)

            if c.config["active"] and c.config["active"] in member.role_ids:
                await member.remove_role(c.config["active"])
            if c.config["inactive"] and c.config["inactive"] not in member.role_ids:
                await member.add_role(c.config["inactive"])


# Listener for bot ready
@plugin.listener(hikari.StartedEvent)
async def on_ready(event):
    check_activity.start()


# Listener for guild messages
@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_message(event):
    if event.is_bot or event.guild_id != c.config["guild"]:
        return

    db[event.author_id] = event.message.timestamp  # or datetime.datetime.utcnow()

    if c.config["active"] and c.config["active"] not in event.member.role_ids:
        await event.member.add_role(c.config["active"])
    if c.config["inactive"] and c.config["inactive"] in event.member.role_ids:
        await event.member.remove_role(c.config["inactive"])


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)