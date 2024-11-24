import os
import shutil
import logging
from urllib import request

import requests
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from deepface import DeepFace

# Настройка логирования
LOG_FILE = "app.log"
logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),  # Логи в файл
        logging.StreamHandler()  # Вывод логов в консоль
    ]
)
logger = logging.getLogger()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

class EmotionAnalyzer:
    NEGATIVE_EMOTIONS = ['angry', 'sad', 'fear', 'disgust']

    def __init__(self, api_key):
        self.api_key = api_key
        self.GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        logger.info(f"Инициализация анализатора с API ключом: {api_key}")

    def notify(self, authority, emotion, details):
        """Отправка уведомления о негативной эмоции"""
        logger.warning(f"⚠ Уведомление для {authority}: Обнаружена негативная эмоция ({emotion}).")
        logger.debug(f"Дополнительные данные: {details}")

    def explain_with_gemini(self, prompt):
        """Запрос к Gemini API"""
        try:
            logger.info(f"Запрос к Gemini API с промптом: {prompt[:50]}...")  # Логируем первые 50 символов
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.GEMINI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                logger.info(f"Ответ от Gemini получен: {response.status_code}")
                candidates = response.json().get("candidates", [])
                return candidates[0]["content"]["parts"][0]["text"] if candidates else "Нет ответа от Gemini"
            else:
                logger.error(f"Ошибка Gemini API: {response.status_code} - {response.text}")
                return f"Ошибка Gemini API: {response.status_code} - {response.text}"
        except Exception as e:
            logger.error(f"Ошибка при обращении к Gemini: {str(e)}")
            return f"Ошибка при обращении к Gemini: {str(e)}"

    def analyze_image_emotion(self, image_path):
        """Анализ эмоций на изображении"""
        logger.info(f"Начало анализа изображения: {image_path}")

        try:
            # Анализируем эмоции с помощью DeepFace
            analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])
            if analysis:
                logger.info("Эмоции на изображении успешно проанализированы.")
                result = analysis[0]  # Результаты для первого обнаруженного лица
                dominant_emotion = result['dominant_emotion']
                logger.info(f"Доминирующая эмоция: {dominant_emotion}")

                # Проверка на негативную эмоцию
                if dominant_emotion in self.NEGATIVE_EMOTIONS:
                    self.notify(
                        authority="Психолога и Командира",
                        emotion=dominant_emotion,
                        details=result
                    )

                # Подготовка промпта для Gemini
                emotions_summary = "\n".join(
                    [f"{emotion}: {score:.2f}%" for emotion, score in result['emotion'].items()]
                )
                gemini_prompt = (
                    f"Я проанализировал изображение. Доминирующая эмоция: {dominant_emotion}. "
                    f"Все вероятности эмоций: \n{emotions_summary}. "
                    f"Объясните, что это может означать и как можно интерпретировать эти данные."
                    f"Все это для предотвращения несчастных случаев в армии, дается и анализируется изображение солдата."
                )

                # Запрос к Gemini
                gemini_response = self.explain_with_gemini(gemini_prompt)

                return {
                    "dominant_emotion": dominant_emotion,
                    "emotions": result['emotion'],
                    "gemini_response": gemini_response,
                    "face_region": result['region']
                }
            else:
                logger.warning(f"Лицо не обнаружено на изображении: {image_path}")
                return {"error": "Лицо не обнаружено на изображении."}

        except Exception as e:
            logger.error(f"Произошла ошибка при анализе изображения {image_path}: {str(e)}")
            return {"error": str(e)}


@app.get("/")
async def root(request: Request):
    """Главная страница"""
    logger.info("Запрос главной страницы.")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Обработка и анализ изображения"""
    # Логируем начало обработки изображения
    logger.info(f"Получен файл для анализа: {file.filename}")

    # Сохраняем файл во временную папку
    image_path = os.path.join(TEMP_DIR, file.filename)
    with open(image_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    logger.info(f"Файл сохранен в {image_path}")

    # Инициализация анализатора
    API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key")
    analyzer = EmotionAnalyzer(API_KEY)

    # Анализ изображения
    result = analyzer.analyze_image_emotion(image_path)

    # Удаляем временный файл
    os.remove(image_path)
    logger.info(f"Временный файл {image_path} удален.")

    # Возвращаем результат в шаблон
    logger.info("Отправка результата анализа.")
    return templates.TemplateResponse("result.html", {"request": request, "result": result})
