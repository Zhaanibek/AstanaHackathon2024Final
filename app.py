from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from deepface import DeepFace  # Убедитесь, что DeepFace установлена
import requests  # Для взаимодействия с Gemini API

app = FastAPI()

# Папки для шаблонов и статики
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
templates = Jinja2Templates(directory="templates")

# Папка для временных файлов
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

class EmotionAnalyzer:
    NEGATIVE_EMOTIONS = ['angry', 'sad', 'fear', 'disgust']

    def __init__(self, api_key):
        self.api_key = api_key
        self.GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

    def notify(self, authority, emotion, details):
        """Отправка уведомления о негативной эмоции"""
        print(f"⚠ Уведомление для {authority}: Обнаружена негативная эмоция ({emotion}).")
        print(f"  Дополнительные данные: {details}")

    def explain_with_gemini(self, prompt):
        """Запрос к Gemini API"""
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.GEMINI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                return candidates[0]["content"]["parts"][0]["text"] if candidates else "Нет ответа от Gemini"
            else:
                return f"Ошибка Gemini API: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Ошибка при обращении к Gemini: {str(e)}"

    def analyze_image_emotion(self, image_path):
        """Анализ эмоций на изображении"""
        try:
            # Анализ эмоций с помощью DeepFace
            analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])
            result = analysis[0]  # Результаты для первого обнаруженного лица
            dominant_emotion = result['dominant_emotion']

            # Проверка на негативную эмоцию
            if dominant_emotion in self.NEGATIVE_EMOTIONS:
                self.notify(
                    authority="Психолога и Командира",
                    emotion=dominant_emotion,
                    details=result
                )

            # Подготовка данных для Gemini
            emotions_summary = "\n".join(
                [f"{emotion}: {score:.2f}%" for emotion, score in result['emotion'].items()]
            )
            gemini_prompt = (
                f"Доминирующая эмоция: {dominant_emotion}. "
                f"Все вероятности эмоций: \n{emotions_summary}. "
                f"Объясните, что это может означать."
            )
            gemini_response = self.explain_with_gemini(gemini_prompt)

            return {
                "dominant_emotion": dominant_emotion,
                "emotions": result['emotion'],
                "gemini_response": gemini_response,
                "face_region": result['region']
            }

        except Exception as e:
            return {"error": str(e)}


@app.get("/")
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Обработка и анализ изображения"""
    # Сохраняем файл во временную папку
    image_path = os.path.join(TEMP_DIR, file.filename)
    with open(image_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Инициализация анализатора
    API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBZ1P73TqceCvS-0uYUhaZ8Qb7KtGoakuE")
    analyzer = EmotionAnalyzer(API_KEY)

    # Анализ изображения
    result = analyzer.analyze_image_emotion(image_path)

    # Удаляем временный файл
    os.remove(image_path)

    return JSONResponse(content=result)
