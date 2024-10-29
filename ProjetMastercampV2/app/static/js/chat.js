document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM entièrement chargé et analysé');
    var socket = io.connect('https://' + document.domain + ':' + location.port);
    var username = document.getElementById('username').value;

    socket.on('connect', () => {
        console.log('Connected to the server.');
        socket.emit('join', { room: username });
    });

    $('#action_menu_btn').click(function(){
        $('.action_menu').toggle();
    });


    
    socket.on('update_user_list', (users) => {
        const contactsList = document.querySelector('.contacts');
        contactsList.innerHTML = '';
        users.forEach(user => {
            if (user !== username) {
                const userElement = document.createElement('li');
                userElement.classList.add('active');
                userElement.innerHTML = `
                    <div class="d-flex bd-highlight">
                    <div class="user_info">
                        <a href="/privatechat?user=${encodeURIComponent(user)}" class="user-link">

                            <span>${user}</span>
                        </a>
                    </div>
                </div>`;
                contactsList.appendChild(userElement);
            }
        });
    });

    socket.on('message', (data) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('d-flex', 'justify-content-start', 'mb-4');

        const messageBubble = document.createElement('div');
        messageBubble.classList.add('msg_cotainer');
        messageBubble.innerHTML = `<strong>${data.username}:</strong> ${data.msg}`;

        const messageTime = document.createElement('span');
        messageTime.classList.add('msg_time');
        const now = new Date();
        messageTime.innerText = now.toLocaleTimeString();

        messageBubble.appendChild(messageTime);
        messageElement.appendChild(messageBubble);

        document.querySelector('.msg_card_body').appendChild(messageElement);
    });

    socket.on('private_message', (data) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('d-flex', 'justify-content-start', 'mb-4');

        const messageBubble = document.createElement('div');
        messageBubble.classList.add('msg_cotainer');
        messageBubble.innerHTML = `<strong>${data.sender} (private):</strong> ${data.msg}`;

        const messageTime = document.createElement('span');
        messageTime.classList.add('msg_time');
        const now = new Date();
        messageTime.innerText = now.toLocaleTimeString();

        messageBubble.appendChild(messageTime);
        messageElement.appendChild(messageBubble);

        document.querySelector('.msg_card_body').appendChild(messageElement);
    });

    document.getElementById('send_button').addEventListener('click', (event) => {
        event.preventDefault();
        const message = document.getElementById('message_input').value;

        if (message.trim()) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('d-flex', 'justify-content-end', 'mb-4');

            const messageBubble = document.createElement('div');
            messageBubble.classList.add('msg_cotainer_send');
            messageBubble.innerHTML = message;

            const messageTime = document.createElement('span');
            messageTime.classList.add('msg_time_send');
            const now = new Date();
            messageTime.innerText = now.toLocaleTimeString();

            messageBubble.appendChild(messageTime);
            messageElement.appendChild(messageBubble);

            document.querySelector('.msg_card_body').appendChild(messageElement);

            socket.emit('message', { msg: message });
            document.getElementById('message_input').value = '';
        }
    });

    document.getElementById('send_private_button').addEventListener('click', (event) => {
        event.preventDefault();
        const message = document.getElementById('message_input').value;
        const recipient = prompt("Enter recipient username:");

        if (message.trim() && recipient) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('d-flex', 'justify-content-end', 'mb-4');

            const messageBubble = document.createElement('div');
            messageBubble.classList.add('msg_cotainer_send');
            messageBubble.innerHTML = message;

            const messageTime = document.createElement('span');
            messageTime.classList.add('msg_time_send');
            const now = new Date();
            messageTime.innerText = now.toLocaleTimeString();

            messageBubble.appendChild(messageTime);
            messageElement.appendChild(messageBubble);

            document.querySelector('.msg_card_body').appendChild(messageElement);

            socket.emit('private_message', { msg: message, recipient: recipient });
            document.getElementById('message_input').value = '';
        }
    });

    document.getElementById('logout_button').addEventListener('click', () => {
        console.log('Logout button clicked');
        fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                console.log('Logout successful');
                window.location.href = '/login';
            } else {
                console.error('Logout failed');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    document.getElementById('send_document_button').addEventListener('click', () => {
        document.getElementById('document_input').click();
    });

    document.getElementById('document_input').addEventListener('change', () => {
        const file = document.getElementById('document_input').files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64Document = reader.result.split(',')[1];
                socket.emit('document', { username: username, document: base64Document, fileName: file.name });
            };
            reader.readAsDataURL(file);
        }
    });

    socket.on('document', (data) => {
        const documentElement = document.createElement('div');
        documentElement.classList.add('d-flex', 'justify-content-start', 'mb-4');

        const documentBubble = document.createElement('div');
        documentBubble.classList.add('msg_cotainer');
        const linkElement = document.createElement('a');
        linkElement.href = `data:application/octet-stream;base64,${data.document}`;
        linkElement.download = data.fileName;
        linkElement.textContent = `${data.username} sent a document: ${data.fileName}`;

        documentBubble.appendChild(linkElement);
        documentElement.appendChild(documentBubble);

        document.querySelector('.msg_card_body').appendChild(documentElement);
    });

    let audioChunks = [];
    let mediaRecorder;

    document.getElementById('startRecording').addEventListener('click', async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = [];
            sendAudioMessage(audioBlob);
        });

        document.getElementById('startRecording').disabled = true;
        document.getElementById('stopRecording').disabled = false;
    });

    document.getElementById('stopRecording').addEventListener('click', () => {
        mediaRecorder.stop();
        document.getElementById('startRecording').disabled = false;
        document.getElementById('stopRecording').disabled = true;
    });

    function sendAudioMessage(audioBlob) {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64AudioMessage = reader.result.split(',')[1];
            socket.emit('audio_message', { username: username, audio: base64AudioMessage });
        };
        reader.readAsDataURL(audioBlob);
    }

    socket.on('audio_message', (data) => {
        const audioElement = document.createElement('audio');
        audioElement.controls = true;
        audioElement.src = `data:audio/wav;base64,${data.audio}`;
        const messageElement = document.createElement('div');
        messageElement.classList.add('d-flex', 'justify-content-start', 'mb-4');

        const audioBubble = document.createElement('div');
        audioBubble.classList.add('msg_cotainer');
        audioBubble.appendChild(audioElement);

        messageElement.appendChild(audioBubble);
        document.querySelector('.msg_card_body').appendChild(messageElement);
    });
    document.getElementById('call_button').addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = '/call';
    });
    document.getElementById('callgroup_button').addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = '/groupecall';
    });
});



