import os
import html
import uuid
import shutil
import asyncio
import aiohttp
import aiofiles
from pyrogram import Client, filters, enums
from config import Config

saavn_regex = r"(?i)(https?:\/\/)?(www\.)?jiosaavn\.com\/[\w\-/?=%.]*"

@Client.on_message(filters.text & filters.regex(saavn_regex))
async def jiosaavndl(client, message):
    if str(message.from_user.id) not in Config.AUTHJS:
        return
    task_id = str(uuid.uuid4())[:8]
    download_dir = f"downloads/{task_id}"
    os.makedirs(download_dir, exist_ok=True)  # Ensure the downloads folder exists
    await message.reply_chat_action(enums.ChatAction.TYPING)
    text = message.text.strip()
    api = f"https://jiosaavnsearch.vercel.app/songs?link={text}"
    
    if "jiosaavn.com/song" in text:
        k = await message.reply_text("**Processing...**", quote=True)
        
        # Fetch Song Metadata
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api) as response:
                    if response.status != 200:
                        await k.edit_text(f"**Error fetching song data:** `HTTP {response.status}`")
                        return
                    req = await response.json()
        except Exception as e:
            await k.edit_text(f"**Error fetching song data:** `{str(e)}`")
            return
        
        try:
            # Extracting Song Metadata
            res = req['data'][0]
            title = html.unescape(res['name'])
            artist = html.unescape(res['primaryArtists'])
            song_url = res['downloadUrl'][3]['link']
            duration = res['duration']
            album = html.unescape(res['album']['name'])
            year = res['year']
            copyright_info = res['copyright']
            img_url = res['image'][2]['link']  # URL for cover art
            cmnt = f"(c) Koshik Kumar - {res['url']}"
            
            # File paths
            afile = os.path.join(download_dir, f"{title}.mp4")
            mp3_file = os.path.join(download_dir, f"{title}_temp.mp3")
            ofile = os.path.join(download_dir, f"{title} - {artist}.mp3")
            cover_image_path = os.path.join(download_dir, f"{title}.jpg")
            
            # Download the Song
            async with aiohttp.ClientSession() as session:
                async with session.get(song_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(afile, mode='wb') as f:
                            await f.write(await response.read())
                    else:
                        await k.edit_text(f"**Error downloading song:** `HTTP {response.status}`")
                        return
            
            # Rename the downloaded file to .mp3
            os.rename(afile, mp3_file)
            
            # Download the Cover Art
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(cover_image_path, mode='wb') as f:
                            await f.write(await response.read())
                    else:
                        cover_image_path = None
            
            # Use ffmpeg to Add Metadata
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", mp3_file,
                "-i", cover_image_path,
                "-map", "0:a", "-map", "1:v",
                "-metadata", f"title={title}",
                "-metadata", f"artist={artist}",
                "-metadata", f"album={album}",
                "-metadata", f"date={year}",
                "-metadata", f"comment={cmnt}",
                "-metadata", f"copyright={copyright_info}",
                "-id3v2_version", "3",
                "-c:a", "libmp3lame",
                "-c:v", "mjpeg",
                "-y",
                ofile, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                await k.edit_text(f"**Error adding metadata with ffmpeg:** \n`{process.stderr.decode()}`")
                return
            
            # Step 5: Send the Song
            caption = f"""**Title:** {title}\n\n**Artists:** {artist}\n\n**Album:** {album}"""
            await message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
            await message.reply_audio(
                audio=ofile,
                duration=int(duration),
                caption=caption,
                performer=artist,
                quote=True,
                title=title
            )
            
            # Step 6: Cleanup
            try:
                shutil.rmtree(download_dir)
                
            except Exception as e:
                print(f"**Error deleting files:** `{str(e)}`")
            
            await k.delete()
        
        except Exception as e:
            await k.edit_text(f"**Error:** `{str(e)}`")
