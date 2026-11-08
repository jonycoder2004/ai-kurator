# gemini_ai.py — Gemini bilan mazmun tayyorlash
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _model = genai.GenerativeModel("gemini-1.5-flash")
else:
    _model = None


def summarize(title: str, description: str) -> str:
    """Video mazmunini o'zbek tilida qisqacha tushuntiradi."""
    if not _model:
        return "⚠️ Gemini API key sozlanmagan."
    try:
        prompt = (
            f"YouTube video nomi: {title}\n"
            f"Video tavsifi: {description[:1500]}\n\n"
            "Bu video nima haqida ekanligini o'zbek tilida 2-3 jumlada "
            "oddiy va tushunarli qilib tushuntir. Faqat mazmunni yoz, boshqa hech narsa yozma."
        )
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.warning(f"Gemini xatosi: {exc}")
        return "📝 Mazmun tayyorlanmadi."
