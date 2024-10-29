from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import session
from .models.message import MessageDB
from .models.connected import ConnectedUserDB
import random
import time

socketio = SocketIO()
msg_db = MessageDB()
conn_db = ConnectedUserDB()
# history=[]
# for msg in range(len(msg_db.get_all_messages())):
#     history=msg_db.get_all_messages()[msg][0]+ ' : '+ msg_db.get_all_messages()[msg][1]
#     time.sleep(0.1)


@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        username = session['username']
        join_room(username)
        emit('status', {'msg': f"{username} has entered the room."}, broadcast=True)
        update_user_list()

@socketio.on('message')
def handle_message(data):
    username = session.get('username')
    if username:
        msg = data['msg']
        emit('message', {'username': username, 'msg': msg}, broadcast=True, include_self=False)
        msg_db.add_message(username, "all", msg)

@socketio.on('private_message')
def handle_private_message(data):
    username = session.get('username')
    recipient = data['recipient']
    if username and recipient:
        msg = data['msg']
        emit('private_message', {'sender': username, 'msg': msg}, room=recipient)
        msg_db.add_message(username, recipient, msg)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username:
        conn_db.update_disconnected_at(username)  # Log disconnection time
        leave_room(username)
        emit('status', {'msg': f"{username} has left the room."}, broadcast=True)
        update_user_list()

@socketio.on('mdpgenerate')
def genreatemdp():
    maj="AZERTYUIOPMLKJHGFDSQWXCVBN"
    min="azertyuiopmlkjhgfdsqwxcvbn"
    spe="ù*^!@][]{}&-_"
    chiffres="0123456789"
    mdp=""
    for k in range((12)):
        a=random.randrange(4)
        if a==0:
            choice=random.randrange(len(maj))
            mdp=mdp+maj[choice]
        if a==1:
            choice=random.randrange(len(min))
            mdp=mdp+min[choice]
        if a==2:
            choice=random.randrange(len(spe))
            mdp=mdp+spe[choice]
        if a==3:
            choice=random.randrange(len(chiffres))
            mdp=mdp+chiffres[choice]
    c=0
    m=0
    M=0
    s=0
    for elt in mdp:
        if elt in chiffres:
            c+=1
        if elt in maj:
            m+=1
        if elt in min:
            M+=1
        if elt in spe:
            s+=1
    if s==0 or m==0 or M==0 or c==0 :
            
        return genreatemdp()
    emit("genpass", mdp)

@socketio.on('document')
def handle_document(data):
    emit('document', data, broadcast=True)

@socketio.on('audio_message')
def handle_audio_message(data):
    emit('audio_message', data, broadcast=True)

def update_user_list():
    users = conn_db.get_all_users()
    emit('update_user_list', users, broadcast=True)

def init_socketio(socketio):
    socketio.on_event('connect', handle_connect)
    socketio.on_event('message', handle_message)
    socketio.on_event('private_message', handle_private_message)
    socketio.on_event('disconnect', handle_disconnect)
    socketio.on_event('mdpgenerate', genreatemdp)
    socketio.on_event('document', handle_document)
    socketio.on_event('audio_message',handle_audio_message)
