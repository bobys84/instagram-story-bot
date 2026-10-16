import os
import asyncio
from pathlib import Path
import instaloader
from pyrobale import Client, InputFile

BALE_BOT_TOKEN = os.environ.get("BALE_BOT_TOKEN")
BALE_CHAT_ID = os.environ.get("BALE_CHAT_ID")
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
TARGET_USERNAME = os.environ.get("TARGET_USERNAME")

LAST_STORY_FILE = Path("last_story.txt")

def get_last_story_id():
    if LAST_STORY_FILE.exists():
        return LAST_STORY_FILE.read_text().strip()
    return None

def save_last_story_id(story_id):
    LAST_STORY_FILE.write_text(str(story_id))

async def main():
    L = instaloader.Instaloader()

    if IG_USERNAME and IG_PASSWORD:
        try:
            L.login(IG_USERNAME, IG_PASSWORD)
        except Exception as e:
            print(f"Login failed: {e}")
            return

    try:
        profile = instaloader.Profile.from_username(L.context, TARGET_USERNAME)
    except Exception as e:
        print(f"Profile not found: {e}")
        return

    last_id = get_last_story_id()
    found_new = False

    bot = Client(BALE_BOT_TOKEN)

    for story in L.get_stories(userids=[profile.userid]):
        for item in story.get_items():
            story_id = str(item.mediaid)

            if story_id == last_id:
                continue

            print(f"Downloading new story: {story_id}")
            L.download_storyitem(item, target=f"story_{story_id}")
            found_new = True

            downloaded_files = list(Path(".").glob(f"story_{story_id}*"))
            if not downloaded_files:
                continue

            file_path = downloaded_files[0]

            try:
                if file_path.suffix.lower() == ".mp4":
                    await bot.send_video(BALE_CHAT_ID, InputFile(str(file_path)))
                else:
                    await bot.send_photo(BALE_CHAT_ID, InputFile(str(file_path)))
                print(f"Sent to Bale: {file_path.name}")
            except Exception as e:
                print(f"Bale send error: {e}")

            save_last_story_id(story_id)
            file_path.unlink()

    if not found_new:
        print("No new stories.")

if __name__ == "__main__":
    asyncio.run(main())
