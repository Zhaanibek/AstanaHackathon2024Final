document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const resultContainer = document.getElementById('resultContainer');
    const emotionsResult = document.getElementById('emotionsResult');
    const resultImage = document.getElementById('resultImage');
    const errorMessage = document.getElementById('errorMessage');

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

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
        handleFile(file);
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (!file) {
            showError("Файл не выбран.");
            return;
        }

        if (!file.type.startsWith('image/')) {
            showError("Пожалуйста, выберите файл изображения.");
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';
            resultContainer.style.display = 'block';
            uploadImage(file);
        };

        reader.onerror = () => {
            showError("Ошибка при чтении файла.");
        };

        reader.readAsDataURL(file);
    }

    function uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/analyze', {
            method: 'POST',
            body: formData,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.gemini_response) {
                emotionsResult.innerHTML = formatGeminiResponse(data.gemini_response);
                resultImage.src = previewImage.src;
            } else {
                showError(data.message || "Произошла ошибка при анализе изображения.");
            }
        })
        .catch((error) => {
            showError(`Ошибка при отправке файла: ${error.message}`);
        });
    }

    function formatGeminiResponse(text) {
        // Разбиваем текст на секции по двойным звездочкам
        const sections = text.split(/\*\*\*|\*\*/);  // Разделяем как по **, так и по ***

        // Форматируем текст, сохраняя структуру абзацев
        let formattedText = sections.map((section, index) => {
            // Если это заголовок (нечетный индекс)
            if (index % 2 === 1) {
                return `<h3 class="section-title">${section}</h3>`;
            }
            // Форматируем обычный текст, разбивая на абзацы
            return section.split('\n')
                .filter(paragraph => paragraph.trim() !== '')
                .map(paragraph => `<p>${paragraph.trim()}</p>`)
                .join('');
        }).join('');

        return `
            <div class="emotions-analysis">
                ${formattedText}
            </div>
            <style>
                .emotions-analysis {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #2c3e50;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                }
                .section-title {
                    color: #2c3e50;
                    margin: 20px 0 16px 0;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #e9ecef;
                }
                p {
                    margin: 12px 0;
                }
                .emotions-analysis > p:first-child {
                    margin-top: 0;
                }
            </style>
        `;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
});
