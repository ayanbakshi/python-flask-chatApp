from flask import Flask, render_template,request,redirect,url_for,session
from flask_socketio import SocketIO,join_room,leave_room,emit
from flask_session import Session
import json


with open('parameters.json','r') as f:
    params=json.load(f)["params"]

app=Flask(__name__)
app.debug=True

app.config['SECRET_TYPE'] = params['secure_key']
app.config['SESSION_TYPE'] = params['session_type']

Session(app)
socketio = SocketIO(app,manage_session=False)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/chat',methods=['GET','POST'])
def chatroom():
    if request.method=='POST':
        user=request.form['username']
        room=request.form['room']
        session['username']=user
        session['room']=room
        return render_template('chat.html',session=session)
    
    else:
        if session.get('username') is not None:
            return render_template('chat.html', session=session)  
        else:
            return redirect(url_for('index'))

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')  
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)
    

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)

if __name__=='__main__':
    socketio.run(app)
