from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from flask_socketio import SocketIO,emit,disconnect
from flask_session import Session

app=Flask(__name__,template_folder='templates')
app.config['SECRET_KEY']='secret!'
app.config['SESSION_TYPE']='filesystem'
Session(app)

socketio=SocketIO(app,manage_session=False)

users={}
admin_password="adminpass"

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        if not username:
            return render_template('login.html',error="Номата навис")
        if not password or not confirm_password:
            return render_template('login.html',error="Пароль мон ягонта")
        if password!=confirm_password:
            return render_template('login.html',error="Паролы навистагит хархела")
        session['username']=username
        session['approved']=False
        return redirect(url_for('pending'))
    return render_template('login.html')

@app.route('/pending')
def pending():
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('approved'):
        return redirect(url_for('index'))
    return render_template('pending.html')

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not session.get('approved'):
        return redirect(url_for('pending'))
    return render_template('index.html')

@app.route('/set_approved',methods=['POST'])
def set_approved():
    session['approved']=True
    return jsonify({'status':'approved'})

@app.route('/admin')
def admin():
    if 'username' not in session:
        session['username']='admin_temp'
    return render_template('admin.html')

@socketio.on('connect')
def on_connect():
    sid=request.sid
    username=session.get('username')
    if not username:
        disconnect()
        return
    users[sid]={
        'sid':sid,
        'username':username,
        'is_admin':False,
        'can_write':True,
        'approved':session.get('approved',False)
    }
    emit('user-list',list(users.values()),broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    sid=request.sid
    if sid in users:
        del users[sid]
    emit('user-list',list(users.values()),broadcast=True)

@socketio.on('admin-login')
def admin_login(data):
    sid=request.sid
    if data.get('password')==admin_password:
        if sid in users:
            users[sid]['is_admin']=True
        else:
            users[sid]={'sid':sid,
                        'username':'admin',
                        'is_admin':True,
                        'can_write':True,
                        'approved':True}
        emit('admin-login-success',{'message':'Logged in as admin'})
        emit('user-list',list(users.values()),broadcast=True)
    else:
        emit('admin-login-failure',{'message':'Туя ким инчава даро гуфтос'})

@socketio.on('approve-registration')
def approve_registration(data):
    sid_admin=request.sid
    if not users.get(sid_admin,{}).get('is_admin',False):
        emit('error',{'message':'Only admin can approve registrations'})
        return
    target_sid=data.get('target_sid')
    if target_sid in users:
        users[target_sid]['approved']=True
        socketio.emit('registration-approved',{'message':'Дарою аз паи кор шав'},room=target_sid)
        emit('user-list',list(users.values()),broadcast=True)
    else:
        emit('error',{'message':'User not foundас'})

@socketio.on('reject-registration')
def reject_registration(data):
    sid_admin=request.sid
    if not users.get(sid_admin,{}).get('is_admin',False):
        emit('error',{'message':'Only admin can reject registrations'})
        return
    target_sid=data.get('target_sid')
    if target_sid in users:
        socketio.emit('registration-rejected',{'message':'Ту дакор не инчава аз паи корат шав'},room=target_sid)
        del users[target_sid]
        emit('user-list',list(users.values()),broadcast=True)
    else:
        emit('error',{'message':'User not found'})

@socketio.on('code-change')
def on_code_change(data):
    sid=request.sid
    if users.get(sid,{}).get('can_write',True):
        emit('code-change',data,broadcast=True,include_self=False)
    else:
        emit('error',{'message':'Writing disabled'})

@socketio.on('toggle-user-write')
def toggle_user_write(data):
    sid=request.sid
    if not users.get(sid,{}).get('is_admin',False):
        emit('error',{'message':'Ту наметони'})
        return
    target_sid=data.get('target_sid')
    can_write=data.get('can_write',True)
    if target_sid in users:
        users[target_sid]['can_write']=can_write
        emit('user-permission-updated',{'target_sid':target_sid,
                                        'can_write':can_write},
             broadcast=True)
    else:
        emit('error',{'message':'User not found'})

@socketio.on('get-user-list')
def get_user_list():
    sid=request.sid
    if users.get(sid,{}).get('is_admin',False):
        emit('user-list',list(users.values()))
    else:
        emit('error',{'message':'Кори ту не'})

@socketio.on('delete-user')
def delete_user(data):
    admin_sid=request.sid
    if not users.get(admin_sid,{}).get('is_admin',False):
        emit('error',{'message':'Only admin can delete users.'})
        return
    target_sid=data.get('target_sid')
    if target_sid==admin_sid:
        emit('error',{'message':'You cannot delete yourself'})
        return
    print(f"Admin {admin_sid} requested deletion of user {target_sid}")
    if target_sid in users:
        socketio.disconnect(target_sid)
        del users[target_sid]
        print(f"User {target_sid} deleted")
        emit('user-list',list(users.values()),broadcast=True)
    else:
        emit('error',{'message':'User not found'})

if __name__=='__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
