document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const resultContainer = document.getElementById('resultContainer');
    const emotionsResult = document.getElementById('emotionsResult');
    const resultImage = document.getElementById('resultImage');

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
                emotionsResult.innerHTML = `Эмоции: ${data.gemini_response}`;
                resultImage.src = previewImage.src;
            } else {
                showError(data.message || "Произошла ошибка при анализе изображения.");
            }
        })
        .catch((error) => {
            showError(`Ошибка при отправке файла: ${error.message}`);
        });
    }

    function showError(message) {
        alert(message);
    }
});
