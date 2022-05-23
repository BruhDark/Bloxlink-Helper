import discord
import jaro
import motor

client = motor.motor_tornado.MotorClient(
    "mongodb+srv://bloxlinkHelper:ZR8otSoEzWCuGLye@cluster0.gee6w.mongodb.net/")
database = client["bloxlinkHelper"]
collection = database["tags"]

async def get_tags(ctx: discord.ApplicationContext) -> list:
    """ Get all tags names"""
    def jaro_sort(key):
        return jaro.jaro_winkler_metric(key, ctx.value.lower())

    tags = []
    async for tag in collection.find():
        tags.append(tag["name"])

    return sorted(tags, key=jaro_sort, reverse=True)[0:15]

async def get_tags_and_alias(ctx: discord.ApplicationContext) -> list:
    """Get all tags and aliases"""

    def jaro_sort(key):
        return jaro.jaro_winkler_metric(key, ctx.value.lower())

    tags = []

    async for tag in collection.find():
        tags.append(tag["name"])
        if tag["aliases"] != ["None"]:
            tags.extend(tag["aliases"])

    return sorted(tags, key=jaro_sort, reverse=True)[0:15]

async def get_aliases(ctx: discord.ApplicationContext) -> list:
    "Get all aliases"

    aliases = []

    async for tag in collection.find():
        if tag["aliases"] != ["None"]:
            aliases.extend(tag["aliases"])

    return [alias for alias in aliases if alias.startswith(ctx.value.lower())]

async def return_all_tags():
    """Returns all tags"""
    find = collection.find()
    tags = []
    for tag in await find.to_list(length=None):
        tags.append(tag)

    return tags

async def insert_one(doc: dict):
    """Inserts a new document"""
    find = await collection.insert_one(doc)
    return find

async def find_one(check: dict):
    """Finds a document"""
    find = await collection.find_one(check)
    return find

async def find_tag(name: str):
    """Finds a tag. If not found by name, finds by aliases"""
    find = await collection.find_one({"name": name})
    if find is None:
        find = await collection.find_one({"aliases": name})
    return find

async def delete_one(query: dict):
    """Deletes a document"""
    find = await collection.delete_one(query)
    return find

async def update_tag(check: dict, update: dict):
    """Updates a document"""
    find = await collection.find_one_and_update(check, {"$set": update})
    return find