document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Active navigation highlight
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-links a');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - sectionHeight / 3)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').slice(1) === current) {
                link.classList.add('active');
            }
        });
    });

    // FAQ Accordion
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', () => {
            const answer = question.nextElementSibling;
            const isOpen = answer.style.display === 'block';

            // Close all answers
            document.querySelectorAll('.faq-answer').forEach(a => {
                a.style.display = 'none';
            });

            // Open clicked answer if it was closed
            if (!isOpen) {
                answer.style.display = 'block';
            }
        });
    });

    // File Upload and Image Preview
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const resultContainer = document.getElementById('resultContainer');
    const emotionsResult = document.getElementById('emotionsResult');

    // Click to upload
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and drop functionality
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
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.hidden = false;
                resultContainer.style.display = 'block';

                // Simulate emotion analysis (replace with actual API call in production)
                setTimeout(() => {
                    const mockEmotions = {
                        'Радость': '75%',
                        'Нейтральность': '15%',
                        'Удивление': '10%'
                    };
                    displayEmotions(mockEmotions);
                }, 1500);
            };
            reader.readAsDataURL(file);
        }
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
                    <div style="width: ${probability}; background-color: var(--primary-color); height: 20px; border-radius: 5px"></div>
                </div>
                <span>${probability}</span>
            `;
            emotionsResult.appendChild(bar);
        });
    }

    // Contact Form
    const contactForm = document.getElementById('contactForm');
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        // Simulate form submission
        alert('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.');
        contactForm.reset();
    });
});