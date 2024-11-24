document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const resultContainer = document.getElementById('resultContainer');
    const emotionsResult = document.getElementById('emotionsResult');
    const errorMessage = document.getElementById('errorMessage'); // Добавим элемент для отображения ошибок

    // Обработчик клика по зоне перетаскивания, чтобы вызвать диалог выбора файла
    dropZone.addEventListener('click', () => {
        fileInput.click();  // Открывает диалог выбора файла
    });

    // Обработчик перетаскивания файлов
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();  // Предотвращаем стандартное поведение
        dropZone.style.backgroundColor = '#f0f0f0';  // Изменяем цвет фона при перетаскивании
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.backgroundColor = '';  // Возвращаем прежний цвет фона
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = '';  // Возвращаем прежний цвет фона
        const file = e.dataTransfer.files[0];  // Получаем файл из перетаскивания
        handleFile(file);  // Обрабатываем файл
    });

    // Обработчик изменения выбора файла через input
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);  // Обрабатываем выбранный файл
    });

    // Функция для обработки файла
    function handleFile(file) {
        if (!file) {
            showError("Файл не выбран.");
            return;
        }

        if (!file.type.startsWith('image/')) {
            showError("Пожалуйста, выберите изображение.");
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;  // Устанавливаем изображение для предварительного просмотра
            previewImage.hidden = false;  // Показываем изображение
            resultContainer.style.display = 'block';  // Показываем блок с результатами

            // Отправляем изображение на сервер для анализа
            uploadImage(file);
        };

        reader.onerror = (error) => {
            showError(`Ошибка при чтении файла: ${error.message}`);
        };

        reader.readAsDataURL(file);
    }

    // Функция для отображения ошибок
    function showError(message) {
        errorMessage.innerHTML = `<p style="color: red;">Ошибка: ${message}</p>`;
        errorMessage.style.display = 'block'; // Показываем сообщение об ошибке
    }

    // Функция для отправки изображения на сервер
    function uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Скрываем сообщения об ошибках при новой отправке
        errorMessage.style.display = 'none';

        // Отправка POST запроса на FastAPI сервер
        fetch('/analyze', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(`Ошибка анализа: ${data.error}`);
            }
            displayEmotions(data.emotions);  // Отображаем результат анализа эмоций
        })
        .catch(error => {
            showError(`Ошибка: ${error.message}`);
        });
    }

    // Функция для отображения результатов анализа
    function displayEmotions(emotions) {
        emotionsResult.innerHTML = '<h3>Результаты анализа:</h3>';
        if (!emotions || Object.keys(emotions).length === 0) {
            emotionsResult.innerHTML += '<p>Не удалось проанализировать эмоции.</p>';
            return;
        }

        Object.entries(emotions).forEach(([emotion, probability]) => {
            const bar = document.createElement('div');
            bar.style.display = 'flex';
            bar.style.alignItems = 'center';
            bar.style.marginBottom = '10px';
            bar.innerHTML = `
                <span style="width: 100px">${emotion}:</span>
                <div style="flex-grow: 1; background-color: #eee; border-radius: 5px; margin: 0 10px">
                    <div style="width: ${probability}; background-color: var(--primary-color); height: 20px; border-radius: 5px"></div>
                </div>
                <span>${probability}</span>
            `;
            emotionsResult.appendChild(bar);
        });
    }
});
