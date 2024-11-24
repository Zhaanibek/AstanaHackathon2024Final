from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from deepface import DeepFace
import requests
import os

app = FastAPI()


class EmotionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        self.NEGATIVE_EMOTIONS = ['angry', 'sad', 'fear', 'disgust']

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

    def analyze_image_emotion(self, image_path):
        """Анализ эмоций на изображении"""
        try:
            analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])
            if analysis:
                result = analysis[0]  # Результаты для первого обнаруженного лица
                dominant_emotion = result['dominant_emotion']

                emotions_summary = "\n".join(
                    [f"{emotion}: {score:.2f}%" for emotion, score in result['emotion'].items()]
                )
                gemini_prompt = (
                    f"Я проанализировал изображение. Доминирующая эмоция: {dominant_emotion}. "
                    f"Все вероятности эмоций: \n{emotions_summary}. "
                    f"Объясните, что это может означать и как можно интерпретировать эти данные."
                )

                gemini_response = self.explain_with_gemini(gemini_prompt)
                return {
                    "dominant_emotion": dominant_emotion,
                    "emotions": result['emotion'],
                    "gemini_response": gemini_response,
                    "face_region": result['region'],
                    "face_confidence": result['face_confidence']
                }
            else:
                return {"error": "Лицо не обнаружено на изображении."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


API_KEY = "AIzaSyBZ1P73TqceCvS-0uYUhaZ8Qb7KtGoakuE"
analyzer = EmotionAnalyzer(API_KEY)


@app.post("/analyze_emotion/")
async def analyze_emotion(file: UploadFile = File(...)):
    if not file.filename.endswith(("jpg", "jpeg", "png")):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением (jpg, jpeg, png)")

    # Сохраняем временный файл
    temp_file_path = "temp_image.jpg"
    with open(temp_file_path, "wb") as f:
        f.write(file.file.read())

    try:
        # Анализ изображения
        result = analyzer.analyze_image_emotion(temp_file_path)
        return JSONResponse(content=result)
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
