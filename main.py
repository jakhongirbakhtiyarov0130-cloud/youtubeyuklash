import os, asyncio, logging, uvicorn, socket
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, Request
from aiogram.types import Update
from contextlib import asynccontextmanager
from utils import download_video, download_audio
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Sozlamalar
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Render yoki Hugging Face-dan keladigan avtomat URL
BASE_URL = os.getenv("RENDER_EXTERNAL_URL") 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Assalomu alaykum! YouTube yuklovchi bot tayyor holatda! ✅")

@dp.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def handle_link(m: types.Message):
    user_data[m.from_user.id] = m.text
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎵 MP3", callback_data="dl_mp3"),
           types.InlineKeyboardButton(text="🎥 MP4", callback_data="dl_mp4"))
    await m.answer("Formatni tanlang:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("dl_"))
async def process_dl(cb: types.CallbackQuery):
    uid, url, fmt = cb.from_user.id, user_data.get(cb.from_user.id), cb.data.split("_")[1]
    if not url: return
    await cb.message.edit_text("Yuklanmoqda... ⏳")
    try:
        path = await download_audio(url) if fmt == "mp3" else await download_video(url)
        await bot.send_document(cb.message.chat.id, types.FSInputFile(path))
        if os.path.exists(path): os.remove(path)
        await cb.message.delete()
    except Exception as e:
        await cb.message.edit_text(f"Xatolik: {e}")
    finally:
        user_data.pop(uid, None)

app = FastAPI()
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root(): return {"status": "ok"}

async def setup_webhook():
    logger.info("Internet tarmog'i kutilmoqda...")
    while True:
        try:
            socket.gethostbyname("api.telegram.org")
            
            webhook_url = ""
            if os.getenv("RENDER_EXTERNAL_URL"):
                webhook_url = f"{os.getenv('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"
            elif os.getenv("SPACE_ID"):
                u, s = os.getenv("SPACE_ID").split("/")
                webhook_url = f"https://{u}-{s.replace('_', '-')}.hf.space{WEBHOOK_PATH}"
            
            if webhook_url:
                logger.info(f"Setting webhook: {webhook_url}")
                await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
                logger.info("Bot Webhook orqali ishga tushdi! ✅")
                break
            else:
                logger.info("Webhook URL topilmadi. Polling rejimiga o'tilmoqda...")
                await bot.delete_webhook(drop_pending_updates=True)
                await dp.start_polling(bot)
                break
        except Exception as e:
            logger.error(f"Xatolik: {e}")
            await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(setup_webhook())
    yield
    await bot.session.close()

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    # Agar webhook URL bo'lsa FastAPI ishga tushadi, aks holda polling
    if os.getenv("RENDER_EXTERNAL_URL") or os.getenv("SPACE_ID"):
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Lokal polling uchun FastAPI kerakmas, lekin xatolik bo'lmasligi uchun setup_webhook dan foydalanamiz
        asyncio.run(setup_webhook())

