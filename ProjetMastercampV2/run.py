from app import create_app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    #socketio.run(app, debug=True)
    #commit marvin test
    socketio.run(app, host="0.0.0.0", port=443,debug=True,ssl_context=("cert.pem","cert-key.pem"))