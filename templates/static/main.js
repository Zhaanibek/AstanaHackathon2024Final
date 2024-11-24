// Элементы DOM
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewImage = document.getElementById('previewImage');
const resultContainer = document.getElementById('resultContainer');
const emotionsResult = document.getElementById('emotionsResult');

// Нажатие для выбора файла
dropZone.addEventListener('click', () => fileInput.click());

// Перетаскивание файла
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.backgroundColor = '#f0f0f0';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.backgroundColor = '';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.backgroundColor = '';
    const file = e.dataTransfer.files[0];
    if (file) {
        handleFile(file);
    }
});

// Выбор файла через input
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

function handleFile(file) {
    if (file && file.type.startsWith('image/')) {
        if (file.size > 5 * 1024 * 1024) { // Ограничение на размер (5 МБ)
            emotionsResult.innerHTML = `<p style="color: red;">Ошибка: Файл слишком большой. Максимальный размер — 5 МБ.</p>`;
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.hidden = false;
            resultContainer.style.display = 'block';

            // Отправка файла на сервер
            uploadImage(file);
        };
        reader.readAsDataURL(file);
    } else {
        emotionsResult.innerHTML = `<p style="color: red;">Ошибка: Пожалуйста, выберите файл изображения.</p>`;
    }
}

function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    emotionsResult.innerHTML = '<p>Загрузка и анализ изображения...</p>';

    // Отправка на сервер
    fetch('/analyze', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка анализа изображения. Проверьте сервер.');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                emotionsResult.innerHTML = `<p style="color: red;">Ошибка: ${data.error}</p>`;
            } else if (data.emotions) {
                displayEmotions(data.emotions);
            } else {
                emotionsResult.innerHTML = `<p>Анализ завершён, но данных о эмоциях не найдено.</p>`;
            }
        })
        .catch(error => {
            emotionsResult.innerHTML = `<p style="color: red;">Ошибка: ${error.message}</p>`;
        });
}

function displayEmotions(emotions) {
    emotionsResult.innerHTML = '<h3>Результаты анализа:</h3>';
    Object.entries(emotions).forEach(([emotion, probability]) => {
        const bar = document.createElement('div');
        bar.style.display = 'flex';
        bar.style.alignItems = 'center';
        bar.style.marginBottom = '10px';
        bar.innerHTML = `
            <span style="width: 100px">${emotion}:</span>
            <div style="flex-grow: 1; background-color: #eee; border-radius: 5px; margin: 0 10px">
                <div style="width: ${probability}%; background-color: var(--primary-color); height: 20px; border-radius: 5px"></div>
            </div>
            <span>${probability}%</span>
        `;
        emotionsResult.appendChild(bar);
    });
}
