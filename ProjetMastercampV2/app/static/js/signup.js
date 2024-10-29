document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM entièrement chargé et analysé');
    var socket = io.connect('https://' + document.domain + ':' + location.port);

    socket.on('genpass', (mdp) =>{
        console.log(mdp);
        alert('Ton mot de passe est ' + mdp + " \n Attention tu ne le verras qu'une seule fois")
        document.getElementById('password').value = mdp;
    }
    );
    document.getElementById('generator').addEventListener('click', () => {
        socket.emit('mdpgenerate');
    });
});

