// Сохраняем текущий выбранный userId и WebSocket соединение
let selectedUserId = null;
let socket = null;
let messagePollingInterval = null;

// Функция выхода из аккаунта
async function logout() {
    try {
        if (socket) socket.close();
        const response = await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/auth';
        } else {
            console.error('Ошибка при выходе');
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
    }
}

// Функция выбора пользователя
async function selectUser(userId, userName, event) {
    selectedUserId = userId;
    document.getElementById('chatHeader').innerHTML = `<span>Чат с ${userName}</span><button class="logout-button" id="logoutButton">Выход</button>`;
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendButton').disabled = false;

    document.querySelectorAll('.user-item').forEach(item => item.classList.remove('active'));
    document.querySelectorAll(`[data-user-id='${selectedUserId}']`).forEach(item => item.classList.add('active'));
//    event.target.classList.add('active');

    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';
    messagesContainer.style.display = 'block';

    await loadMessages(userId);
    let userMesCount = document.getElementById('notif-'+userId);
    if (userMesCount !== null) {
        userMesCount.remove();
    }
    document.getElementById('logoutButton').onclick = logout;

//    startMessagePolling(userId);
}

// Загрузка сообщений
async function loadMessages(userId) {
    try {
        const response = await fetch(`/chat/messages/${userId}`);
        const messages = await response.json();
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = messages.map(message =>
            createMessageElement(message.content, message.sender_id)
        ).join('');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Ошибка загрузки сообщений:', error);
    }
}

// Подключение WebSocket
function connectWebSocket() {
    if (socket) socket.close();

    socket = new WebSocket(`ws://${window.location.host}/chat/ws`);
//    socket = new WebSocket(`ws://${window.location.host}/chat/ws/${currentUserId}-${selectedUserId}`);

    socket.onopen = () => console.log('WebSocket соединение установлено');

    socket.onmessage = (event) => {
        const incomingMessage = JSON.parse(event.data);
        if (incomingMessage.type === 'status') {
            updateOnlineStatus(incomingMessage.user_id, incomingMessage.is_online)
        } else {
            if (incomingMessage.sender_id === parseInt(selectedUserId, 10)) {
                addMessage(incomingMessage.content, incomingMessage.sender_id);
            } else {
                updateNotifyIcon(incomingMessage.sender_id)
            }
        }
    };

    socket.onclose = () => console.log('WebSocket соединение закрыто');
}

// Отправка сообщения
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    let to_all = false
    if (message === null) {
        return;
    }
    if (currentUserRole === "admin" && document.getElementById('to_all').checked) {
        to_all = true;
    }
    const recipient_id = to_all ? 0 : selectedUserId
    const payload = {recipient_id: recipient_id, content: message};
    try {
        socket.send(JSON.stringify(payload));
        if (selectedUserId) {
            addMessage(message, currentUserId);
        }
        messageInput.value = '';
    } catch (error) {
        console.error('Ошибка при отправке сообщения:', error);
    }
}

// Добавление сообщения в чат
function addMessage(text, sender_id) {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.insertAdjacentHTML('beforeend', createMessageElement(text, sender_id));
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Создание HTML элемента сообщения
function createMessageElement(text, sender_id) {
    const messageClass = currentUserId === sender_id ? 'my-message' : 'other-message';
    return `<div class="message ${messageClass}">${text}</div>`;
}

// Создание иконки с непрочитанными сообщениями
function createNotifyIcon(userId, new_mes_count) {
    const userMesCount = document.createElement('div');
    userMesCount.classList.add('newmes-count');
    userMesCount.id = "notif-"+userId;
    userMesCount.textContent = new_mes_count;
    return userMesCount;
}

// Создание иконки со статусом пользователя
function createOnlineIcon(userId) {
    const userOnline = document.createElement('div');
    userOnline.classList.add('online');
    userOnline.id = "online-"+userId;
    userOnline.textContent = 'online';
    return userOnline;
}

// Изменение значения в иконке с непрочитанными сообщениями
function updateNotifyIcon(userId) {
    let userMesCount = document.getElementById('notif-'+userId);
    if (userMesCount === null) {
        userMesCount = createNotifyIcon(userId, 1);
        const userElement = document.querySelector(`[data-user-id='${userId}']`);
        const userOnlineIcon = document.getElementById('online-'+userId)
        if (userOnlineIcon !== null) {
            userElement.insertBefore(userMesCount, userOnlineIcon);
        } else {
            userElement.append(userMesCount);
        }
    } else {
        userMesCount.textContent = parseInt(userMesCount.textContent, 10) + 1;
    }
}

// Изменение статуса пользователя
function updateOnlineStatus(userId, isOnline) {
    let userOnlineIcon = document.getElementById('online-'+userId);
    if (userOnlineIcon === null && isOnline === true) {
        userOnlineIcon = createOnlineIcon(userId);
        const userElement = document.querySelector(`[data-user-id='${userId}']`);
        if (userElement !== null) {
            userElement.append(userOnlineIcon);
        }
    }
    if (userOnlineIcon !== null && isOnline === false) {
        userOnlineIcon.remove();
    }
}

// Запуск опроса новых сообщений
function startMessagePolling(userId) {
    clearInterval(messagePollingInterval);
    messagePollingInterval = setInterval(() => loadMessages(userId), 1000);
}

// Обработка нажатий на пользователя
function addUserClickListeners() {
    document.querySelectorAll('.user-item').forEach(item => {
        item.onclick = event => selectUser(item.getAttribute('data-user-id'), item.textContent, event);
    });
}

// Первоначальная настройка событий нажатия на пользователей
addUserClickListeners();

// Обновление списка пользователей
async function fetchUsers() {
    try {
        const response = await fetch('/auth/users');
        const users = await response.json();
        const userList = document.getElementById('userList');

        // Очищаем текущий список пользователей
        userList.innerHTML = '';
        // Генерация списка пользователей
        users.forEach(user => {
            if (user.id !== currentUserId) {
                const userElement = document.createElement('div');
                userElement.classList.add('user-item');
                userElement.setAttribute('data-user-id', user.id);

                const userNameElement = document.createElement('div');
                userNameElement.classList.add('user-name');
                userNameElement.textContent = user.name;
                userElement.append(userNameElement);

                if (user.new_mes_count > 0) {
                    const userMesCount = createNotifyIcon(user.id, user.new_mes_count);
                    userElement.append(userMesCount);
                }
                if (user.is_online === true) {
                    const userOnline = createOnlineIcon(user.id);
                    userElement.append(userOnline);
                }
                userList.appendChild(userElement);
            }
        });

        if (selectedUserId !== null) {
            document.querySelectorAll(`[data-user-id='${selectedUserId}']`).forEach(item => item.classList.add('active'));
        }
        // Повторно добавляем обработчики событий для каждого пользователя
        addUserClickListeners();
    } catch (error) {
        console.error('Ошибка при загрузке списка пользователей:', error);
    }
}

document.addEventListener('DOMContentLoaded', fetchUsers);
setInterval(fetchUsers, 60000); // Обновление каждые 60 секунд

// Обработчики для кнопки отправки и ввода сообщения
document.getElementById('sendButton').onclick = sendMessage;
// Обработчики для кнопки выхода
document.getElementById('logoutButton').onclick = logout;

document.getElementById('messageInput').onkeypress = async (e) => {
    if (e.key === 'Enter') {
        await sendMessage();
    }
};

if (currentUserRole === "admin") {
    document.getElementById('to_all').addEventListener('change', function() {
          if (this.checked) {
               document.getElementById('messageInput').disabled = false;
               document.getElementById('sendButton').disabled = false;
          } else {
            if (selectedUserId === null) {
               document.getElementById('messageInput').disabled = true;
               document.getElementById('sendButton').disabled = true;
            }
          }
        });
}

connectWebSocket();
