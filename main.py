import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from utils import download_video, download_audio

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("Xatolik: .env fayliga Telegram bot tokenini kiriting!")
    exit()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Store user's URL temporarily (in a real app, use Redis or DB)
user_data = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Menga YouTube linkini yuboring, men uni video yoki MP3 formatda yuklab beraman. 🎥🎵"
    )

@dp.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def handle_youtube_link(message: types.Message):
    url = message.text
    user_data[message.from_user.id] = url
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🎵 MP3 (Audio)", callback_data="download_mp3"),
        types.InlineKeyboardButton(text="🎥 MP4 (Video)", callback_data="download_mp4")
    )
    
    await message.answer("Qaysi formatda yuklamoqchisiz?", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("download_"))
async def process_download(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data:
        await callback.answer("Xatolik: Link topilmadi. Qayta yuboring.")
        return

    url = user_data[user_id]
    format_type = callback.data.split("_")[1]
    
    status_msg = await callback.message.edit_text("Tayyorlanmoqda... ⏳")
    
    try:
        if format_type == "mp3":
            file_path = await download_audio(url)
            await callback.message.edit_text("MP3 yuklab olinmoqda... 🎵")
            await bot.send_audio(
                chat_id=callback.message.chat.id, 
                audio=types.FSInputFile(file_path),
                caption="Muvaffaqiyatli yuklandi! ✅"
            )
        else:
            file_path = await download_video(url)
            await callback.message.edit_text("Video yuklab olinmoqda... 🎥")
            await bot.send_video(
                chat_id=callback.message.chat.id, 
                video=types.FSInputFile(file_path),
                caption="Muvaffaqiyatli yuklandi! ✅"
            )
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logging.error(f"Download error: {e}")
        await callback.message.edit_text(f"Xatolik yuz berdi: {str(e)}")
    
    finally:
        if user_id in user_data:
            del user_data[user_id]

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
