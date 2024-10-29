document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM entièrement chargé et analysé');
    var socket = io.connect('https://' + document.domain + ':' + location.port);
    var username = "{{ username }}"; // Récupérer le nom d'utilisateur du rendu serveur

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
                            <span>${user}</span>
                        </div>
                    </div>`;
                contactsList.appendChild(userElement);
            }
        });
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

});
