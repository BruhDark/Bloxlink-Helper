from aioEasyPillow import Canvas, Editor, Font, load_image
import asyncio


async def spotify_card(album_cover: str):

    canva = Canvas((900, 300), color="black")
    editor = Editor(canva)

    album_cover = await load_image(album_cover)
    await editor.paste(album_cover, (450, 150))

    await editor.show()

asyncio.run(spotify_card(
    "https://cdn.discordapp.com/avatars/449245847767482379/3a7706ee534a07418478a43297675c3b.png"))
