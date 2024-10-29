from flask import render_template, request, redirect, url_for, session, flash
import hashlib
from .models.person import PersonDB
from .models.connected import ConnectedUserDB
import smtplib
from email.mime.text import MIMEText
from random import randint
from itsdangerous import URLSafeTimedSerializer


user_db = PersonDB()
conn_db = ConnectedUserDB()

def init_routes(app):

    @app.route('/startpage')
    def startpage():
        return render_template('startpage.html')

    @app.route('/')
    def index():
        return redirect(url_for('startpage'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            password += 'noa'
            password_hashed = hashlib.sha256(password.encode()).hexdigest()
            if user_db.check_user(username, password_hashed):
                user = user_db.get_user_by_username(username) 
                if user:
                    session['username'] = username
                    session['mail'] = user[2]  
                    conn_db.add_user(username)  
                    return redirect(url_for('chat'))
                
            flash("Nom d'utilisateur ou mot de passe incorrect")
        return render_template('chat-sec.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            mail = request.form['mail']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash("Les mots de passe ne correspondent pas.")
                return redirect(url_for('register'))

            if checkpassword(password):
                password+='noa'
                password_hashed = hashlib.sha256(password.encode()).hexdigest()
                if not user_db.exists_user(username) and not user_db.exists_mail(mail):
                    success, message = user_db.add_user(username, mail, password_hashed)
                    if not success:
                        flash(message)
                        return redirect(url_for('register'))
                    
                    confirmation_code = randint(1000, 9999)
                    print(confirmation_code)
                    if send_confirmation_mail(mail, confirmation_code):
                        session['mail_for_confirmation'] = mail
                        session['confirmation_code'] = confirmation_code
                        flash("Vérifiez votre email pour le code de confirmation.")
                    else:
                        flash("Échec de l'envoi de l'email de confirmation.")
                    return redirect(url_for('confirm_mail'))
                flash("Ce nom d'utilisateur ou adresse e-mail existe déjà.")
            else:
                flash("Mot de passe invalide")

        return render_template('signup.html')   

    @app.route('/confirm_mail', methods=['GET', 'POST'])
    def confirm_mail():
        if request.method == 'POST':
            code = request.form['code']
            if 'confirmation_code' in session and int(code) == session['confirmation_code']:
                if user_db.confirm_user(session['mail_for_confirmation']):
                    flash("Email confirmé avec succès. Vous pouvez vous connecter.")
                    return redirect(url_for('login'))
                else:
                    flash("Echec de la mise a jour du statut de confirmation.")
            else:
                flash("code de confirmation invalide ou session expiree.")
        return render_template('confirm_mail.html')
     

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            username = request.form['username']
            mail = request.form['email']
            user = user_db.get_user_by_username_and_email(username, mail)
            if user:
                token = generate_reset_token(mail)
                reset_url = url_for('reset_password', token=token, _external=True)
                subject = "Password Reset Requested"
                body = f"To reset your password, click the following link: {reset_url}"
                send_mail(mail, subject, body)
                flash('A password reset link has been sent to your email.', 'succes')
                return redirect(url_for('login'))
            else:
                flash('Invalid username or email.', 'danger')
        return render_template('forgot_password.html')
    

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        email = confirm_reset_token(token)
        if not email:
            flash('The reset link is invalid or has expired.', 'danger')
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('reset_password', token=token))
            
            password += 'noa'
            password_hashed = hashlib.sha256(password.encode()).hexdigest()
            if user_db.update_password(email, password_hashed):
                flash('Your password has been updated!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Failed to update password.', 'danger')

        return render_template('reset_password.html', token=token)

    @app.route('/chat')
    def chat():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('chatpage.html')
    @app.route('/privatechat')
    def privatechat():
        if 'username' not in session:
            return redirect(url_for('login'))
        chat_with_user = request.args.get('user', 'default_user') 
        return render_template('privatechat.html', chat_with_user=chat_with_user)


    @app.route('/profile')
    def profile():
        if 'username' not in session:
            return redirect(url_for('login'))
        user_info = {'username': session['username'], 'phone': '+1234567890', 'email': 'rikya@example.com'}
        return render_template('profile.html', user=user_info)

    @app.route('/editprofile')
    def edit_profile():
        return render_template('editprofile.html')
    
    @app.route('/call')
    def call():
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        return render_template('call.html', username=username)
    
    @app.route('/groupecall')
    def groupecall():
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        return render_template('groupcall.html', username=username)


    @app.route('/logout', methods=['POST'])
    def logout():
        username = session.get('username')
        if username:
            print(f"Logging out user: {username}")
            conn_db.update_disconnected_at(username)  # Log disconnection time
            session.pop('username', None)
            print("User logged out successfully")
        return redirect(url_for('login'))
    

    def send_confirmation_mail(mail, confirmation_code):
        sender = "chatlocksafe@gmail.com"
        password = "prneywwqbeihwjvg"
        receiver = mail
        msg = MIMEText(f"Votre code de confirmation est {confirmation_code}")
        msg['Subject'] = "Confirmez votre adresse e-mail"
        msg['From'] = sender
        msg['To'] = receiver

        # Setup your SMTP server and credentials
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
        
    def generate_reset_token(mail):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(mail, salt=app.config['SECURITY_PASSWORD_SALT'])
    
    def confirm_reset_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            mail = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
        except:
            return False
        return mail
    
    def send_mail(to, subject, body):
        sender = "chatlocksafe@gmail.com"
        password = "prneywwqbeihwjvg"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, to, msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False


    def checkpassword(mdp):
        maj = "AZERTYUIOPMLKJHGFDSQWXCVBN"
        min = "azertyuiopmlkjhgfdsqwxcvbn"
        spe = "ù*^!@][]{}&-_"
        chiffres = "0123456789"
        s = 0
        M = 0
        m = 0
        c = 0
        for elt in mdp:
            if elt in chiffres:
                c += 1
            if elt in maj:
                m += 1
            if elt in min:
                M += 1
            if elt in spe:
                s += 1
        if s == 0 or m == 0 or M == 0 or c == 0:
            print("Mot de passe non valide")
            print("Retentez un nouveau mot de passe")
            return False
        return True
