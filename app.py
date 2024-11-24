from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import requests  # Убедитесь, что эта библиотека установлена
from io import BytesIO
from deepface import DeepFace  # Убедитесь, что эта библиотека установлена

app = FastAPI()

# Подключаем папки для шаблонов и статики
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class EmotionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        self.NEGATIVE_EMOTIONS = ['angry', 'sad', 'fear', 'disgust']

    def notify(self, authority, emotion, details):
        """Отправка уведомления о негативной эмоции"""
        print(f"⚠ Уведомление для {authority}: Обнаружена негативная эмоция ({emotion}).")
        print(f"  Дополнительные данные: {details}")

    def explain_with_gemini(self, prompt):
        """Запрос к Gemini API"""
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.GEMINI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                return candidates[0]["content"]["parts"][0]["text"] if candidates else "Нет ответа от Gemini"
            else:
                return f"Ошибка Gemini API: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Ошибка при обращении к Gemini: {str(e)}"

    def analyze_image_emotion(self, image_data):
        """Анализ эмоций на изображении"""
        try:
            # Анализ эмоций с помощью DeepFace
            analysis = DeepFace.analyze(img_path=image_data, actions=['emotion'])

            if analysis:
                result = analysis[0]  # Результаты для первого обнаруженного лица
                dominant_emotion = result['dominant_emotion']
                print(f"Доминирующая эмоция: {dominant_emotion}")

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
                print("**Ответ Gemini:**")
                print(gemini_response)

                # Вывод всех эмоций
                print("\n**Все эмоции (вероятности):**")
                for emotion, score in result['emotion'].items():
                    print(f"  - {emotion.capitalize()}: {score:.2f}%")

                # Вывод информации о лице
                print("\n**Регион лица:**")
                print(f"  - Координаты: x={result['region']['x']}, y={result['region']['y']}, "
                      f"ширина={result['region']['w']}, высота={result['region']['h']}")
                print(f"  - Уверенность в лице: {result['face_confidence']:.2f}")
            else:
                print("Лицо не обнаружено на изображении.")

        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")


@app.get("/")
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Обработка и анализ изображения"""
    # Сохраняем загруженное изображение во временную память
    file_content = await file.read()

    # Сохраняем файл на диск (во временную папку)
    temp_image_path = "temp_image.jpg"
    with open(temp_image_path, "wb") as f:
        f.write(file_content)

    # Инициализация анализатора
    API_KEY = "AIzaSyBZ1P73TqceCvS-0uYUhaZ8Qb7KtGoakuE"  # Замените на ваш API-ключ
    analyzer = EmotionAnalyzer(API_KEY)

    # Анализ изображения
    analyzer.analyze_image_emotion(temp_image_path)

    # После обработки удаляем временный файл
    os.remove(temp_image_path)

    return JSONResponse(content={"message": "Анализ завершен."})
