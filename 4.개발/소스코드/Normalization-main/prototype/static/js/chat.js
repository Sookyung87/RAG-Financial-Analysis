document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.querySelector('.typing-indicator');

    function addMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-bubble ${sender === 'User' ? 'user-message' : 'bot-message'}`;
        messageElement.innerHTML = message;
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function resetUIAfterError() {
        userInput.disabled = false;
        sendBtn.disabled = false;
        hideTypingIndicator();
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage('User', message);
            userInput.value = '';
            userInput.focus();
            showTypingIndicator();
            userInput.disabled = true;
            sendBtn.disabled = true;

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                hideTypingIndicator();
                resetUIAfterError();
                if (data.error) {
                    addMessage('Bot', `오류: ${data.error}`);
                } else {
                    addMessage('Bot', data.response);
                }
            })
            .catch(error => {
                hideTypingIndicator();
                resetUIAfterError();
                if (error.error) {
                    addMessage('Bot', `오류: ${error.error}`);
                } else {
                    console.error('오류:', error);
                    addMessage('Bot', '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.');
                }
            });
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // 채팅 기록 불러오기
    fetch('/chat_history')
    .then(response => response.json())
    .then(data => {
        data.forEach(item => {
            addMessage('User', item.message);
            addMessage('Bot', item.response);
        });
    })
    .catch(error => {
        console.error('채팅 기록 불러오기 오류:', error);
    });

    // 환영 메시지 추가
    addMessage('Bot', 'COMJSH RAG에 오신 것을 환영합니다. 어떤 도움이 필요하신가요?');
});
