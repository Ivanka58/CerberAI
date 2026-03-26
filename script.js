const DEV_PASSWORD = typeof process !== 'undefined' && process.env.DEV_PASSWORD 
    ? process.env.DEV_PASSWORD 
    : '040111';

let devMode = false;
let currentChat = [];
let currentUser = null;
let telegramCode = null;

function initParticles() {
    const particlesContainer = document.getElementById('particles');
    for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (10 + Math.random() * 10) + 's';
        particlesContainer.appendChild(particle);
    }
}

function initCounters() {
    const animateCounter = (el) => {
        const target = parseInt(el.dataset.target);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                el.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                el.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    };

    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counters = entry.target.querySelectorAll('.stat-number');
                counters.forEach(counter => animateCounter(counter));
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stats-grid').forEach(grid => {
        statsObserver.observe(grid);
    });
}

function handleHeroInput(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    
    const sendBtn = document.getElementById('heroSendBtn');
    if (textarea.value.trim().length > 0) {
        sendBtn.classList.add('active');
    } else {
        sendBtn.classList.remove('active');
    }
}

function handleHeroKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        startChat();
    }
}

function setHeroInput(text) {
    document.getElementById('heroInput').value = text;
    handleHeroInput(document.getElementById('heroInput'));
    document.getElementById('heroInput').focus();
}

function checkDevPassword(message) {
    if (message.trim() === DEV_PASSWORD) {
        toggleDevMode();
        return true;
    }
    return false;
}

function toggleDevMode() {
    devMode = !devMode;
    const banner = document.getElementById('devBannerFull');
    
    if (banner) {
        if (devMode) {
            banner.classList.add('active');
        } else {
            banner.classList.remove('active');
        }
    }
    
    if (devMode) {
        addChatMessage('🔐 Режим разработчика АКТИВИРОВАН\n\nВсе сообщения будут сохраняться как системные команды.\nИспользуй формат: +ключ=значение', 'bot');
    } else {
        addChatMessage('🔓 Режим разработчика ВЫКЛЮЧЕН', 'bot');
    }
    
    return true;
}

function startChat() {
    const input = document.getElementById('heroInput');
    const message = input.value.trim();
    if (!message) return;

    if (checkDevPassword(message)) {
        input.value = '';
        handleHeroInput(input);
        document.getElementById('heroSendBtn').classList.remove('active');
        return;
    }

    document.getElementById('chatApp').classList.add('active');
    
    addChatMessage(message, 'user');
    
    input.value = '';
    handleHeroInput(input);
    document.getElementById('heroSendBtn').classList.remove('active');
    
    showTyping();
    
    setTimeout(() => {
        hideTyping();
        const response = generateResponse(message);
        addChatMessage(response, 'bot');
    }, 1500);
}

function closeChat() {
    document.getElementById('chatApp').classList.remove('active');
}

function handleChatInput(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    
    const sendBtn = document.getElementById('chatSendBtn');
    if (textarea.value.trim().length > 0) {
        sendBtn.classList.add('active');
    } else {
        sendBtn.classList.remove('active');
    }
}

function handleChatKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    if (checkDevPassword(message)) {
        input.value = '';
        handleChatInput(input);
        document.getElementById('chatSendBtn').classList.remove('active');
        return;
    }

    addChatMessage(message, 'user');
    
    input.value = '';
    handleChatInput(input);
    document.getElementById('chatSendBtn').classList.remove('active');
    
    showTyping();
    
    setTimeout(() => {
        hideTyping();
        const response = generateResponse(message);
        addChatMessage(response, 'bot');
    }, 1500);
}

function addChatMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    if (sender === 'bot') {
        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = 'CerberAI';
        messageDiv.appendChild(header);
    }
    
    const content = document.createElement('div');
    content.textContent = text;
    messageDiv.appendChild(content);
    
    const typingIndicator = document.getElementById('typingIndicatorFull');
    container.insertBefore(messageDiv, typingIndicator);
    
    container.scrollTop = container.scrollHeight;
    
    currentChat.push({role: sender, content: text});
}

function showTyping() {
    document.getElementById('typingIndicatorFull').classList.add('active');
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    document.getElementById('typingIndicatorFull').classList.remove('active');
}

function generateResponse(message) {
    const lowerMsg = message.toLowerCase();
    
    if (lowerMsg.includes('возможност')) {
        return "Я CerberAI — оркестратор из 50+ моделей. У меня есть долгосрочная память, умная маршрутизация и адаптивный характер. Каждый твой запрос я направляю к лучшей модели: код → DeepSeek, творчество → Claude, скорость → Groq.";
    }
    
    if (lowerMsg.includes('запомни')) {
        if (devMode) {
            return "✓ [DEV MODE] Факт сохранён в систему.";
        }
        return "✓ Запомнил! Этот факт сохранён в мою долгосрочную память. Я буду использовать его в наших будущих разговорах.";
    }
    
    if (lowerMsg.includes('создатель') || lowerMsg.includes('кто тебя')) {
        return "Мой создатель — Каин Сумрак. Он разработал мою архитектуру, систему памяти и интеллектуальный маршрутизатор. Я горжусь своим происхождением!";
    }
    
    if (lowerMsg.includes('код') || lowerMsg.includes('python') || lowerMsg.includes('json')) {
        return "Я направил твой запрос к DeepSeek Coder — лучшей модели для программирования. Вот решение:\n\n```python\nimport json\n\nwith open('data.json') as f:\n    data = json.load(f)\n    \nprint(data['key'])\n```\n\nНужна помощь с чем-то ещё?";
    }
    
    if (lowerMsg.includes('квант') || lowerMsg.includes('физик')) {
        return "Запрос направлен к Claude 3.5 Sonnet — лучшей модели для объяснений. Квантовая физика изучает поведение материи на микроуровне. Представь, что частицы могут быть в двух местах одновременно — это и есть квантовая суперпозиция!";
    }
    
    if (lowerMsg.includes('привет') || lowerMsg.includes('здравствуй')) {
        return "Привет! Я CerberAI, твой AI-компаньон с памятью. Чем могу помочь сегодня? Можешь спросить меня о чём угодно — от программирования до философии.";
    }
    
    return "Я получил твоё сообщение. Сейчас мой маршрутизатор анализирует запрос и выбирает оптимальную модель из 50 доступных. Скоро здесь будет точный и полезный ответ!";
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function newChat() {
    currentChat = [];
    document.getElementById('chatMessages').innerHTML = `
        <div class="typing-indicator-full" id="typingIndicatorFull">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    closeChat();
}

function loadChat(id) {
    alert('Загрузка чата из истории...');
}

function showLogin() {
    document.getElementById('loginModal').classList.add('active');
}

function showRegister() {
    document.getElementById('registerModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function loginWithTelegram() {
    closeModal('loginModal');
    closeModal('registerModal');
    
    telegramCode = Math.floor(100000 + Math.random() * 900000).toString();
    
    const botUsername = 'your_bot_username';
    const uniqueCode = btoa(Date.now().toString()).substring(0, 10);
    const telegramLink = `https://t.me/${botUsername}?start=${uniqueCode}`;
    
    window.open(telegramLink, '_blank');
    
    setTimeout(() => {
        document.getElementById('telegramCodeModal').classList.add('active');
        initCodeInputs();
    }, 1000);
}

function initCodeInputs() {
    const inputs = document.querySelectorAll('.code-input');
    
    inputs.forEach((input, index) => {
        input.value = '';
        input.addEventListener('keydown', (e) => {
            if (e.key >= '0' && e.key <= '9') {
                input.value = e.key;
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
                e.preventDefault();
            } else if (e.key === 'Backspace') {
                input.value = '';
                if (index > 0) {
                    inputs[index - 1].focus();
                }
            }
        });
        
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const paste = e.clipboardData.getData('text').slice(0, 6);
            paste.split('').forEach((char, i) => {
                if (i < inputs.length && char >= '0' && char <= '9') {
                    inputs[i].value = char;
                }
            });
        });
    });
    
    inputs[0].focus();
}

function verifyTelegramCode() {
    const inputs = document.querySelectorAll('.code-input');
    let enteredCode = '';
    inputs.forEach(input => {
        enteredCode += input.value;
    });
    
    if (enteredCode === telegramCode) {
        closeModal('telegramCodeModal');
        
        currentUser = {
            id: Date.now(),
            username: 'TelegramUser',
            avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + Date.now(),
            joinDate: new Date(),
            daysCount: 0
        };
        
        updateUIForLoggedInUser();
        addChatMessage('✓ Авторизация успешна! Добро пожаловать, ' + currentUser.username, 'bot');
    } else {
        alert('Неверный код. Попробуйте ещё раз.');
        inputs.forEach(input => input.value = '');
        inputs[0].focus();
    }
}

function updateUIForLoggedInUser() {
    document.getElementById('sidebarAuth').classList.add('hidden');
    document.getElementById('sidebarUser').classList.remove('hidden');
    
    document.getElementById('sidebarAvatar').src = currentUser.avatar;
    document.getElementById('sidebarUsername').textContent = currentUser.username;
    
    document.getElementById('profileAvatar').src = currentUser.avatar;
    document.getElementById('profileName').textContent = currentUser.username;
    
    updateDaysCount();
}

function updateDaysCount() {
    if (!currentUser) return;
    
    const now = new Date();
    const joinDate = new Date(currentUser.joinDate);
    const diffTime = Math.abs(now - joinDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    document.getElementById('profileDays').textContent = diffDays + ' дней с нами';
    document.getElementById('profileDaysCount').textContent = diffDays;
}

function showProfile() {
    if (currentUser) {
        updateDaysCount();
        document.getElementById('profileModal').classList.add('active');
    } else {
        showLogin();
    }
}

function showBalance() {
    document.getElementById('balanceModal').classList.add('active');
}

function confirmLogout() {
    document.getElementById('logoutConfirmModal').classList.add('active');
}

function confirmLogoutYes() {
    closeModal('logoutConfirmModal');
    closeModal('profileModal');
    
    currentUser = null;
    
    document.getElementById('sidebarAuth').classList.remove('hidden');
    document.getElementById('sidebarUser').classList.add('hidden');
    
    document.getElementById('sidebarAvatar').src = '';
    document.getElementById('sidebarUsername').textContent = 'Гость';
    
    addChatMessage('Вы вышли из аккаунта.', 'bot');
}

function logout() {
    confirmLogout();
}

function initEventListeners() {
    const heroInput = document.getElementById('heroInput');
    const heroSendBtn = document.getElementById('heroSendBtn');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    
    if (heroInput) {
        heroInput.addEventListener('input', () => handleHeroInput(heroInput));
        heroInput.addEventListener('keydown', handleHeroKeyPress);
    }
    
    if (heroSendBtn) {
        heroSendBtn.addEventListener('click', startChat);
    }
    
    if (chatInput) {
        chatInput.addEventListener('input', () => handleChatInput(chatInput));
        chatInput.addEventListener('keydown', handleChatKeyPress);
    }
    
    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', sendChatMessage);
    }
    
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => setHeroInput(chip.dataset.text));
    });
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
    
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initCounters();
    initEventListeners();
});
