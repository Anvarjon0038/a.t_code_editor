# ✨ A.T Code Editor  

A.T Code Editor is a web-based code editor with authentication, an admin panel, and real-time collaboration.  
The project is built using **Flask, HTML, CSS, and JavaScript**.  

## 🚀 Features  

- 🔐 **Authentication & Registration** – Users register, but access is granted only after admin approval.  
- ✍️ **Real-time Code Editing** – All participants can write and see each other’s code in real time.  
- 🎯 **Flexible Access Control**:  
  - 🛑 The admin can disable users from editing or switch them to observer mode.  
  - 📝 Users can write code privately without others seeing it.  
- 🛠️ **Admin Panel**:  
  - 👤 Manage users.  
  - 🔄 Enable/disable user access to the editor.  
  - 🗑️ Remove users from the system.  

## 🛠️ Tech Stack  

- 🐍 **Back-end:** Python (Flask)  
- 🎨 **Front-end:** HTML, CSS, JavaScript  
- ⚡ **Real-time Functionality:** Flask-SocketIO  

## 📥 Installation & Setup  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/Anvarjon0038/a.t_code_editor
cd a.t_code_editor
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Run the application
python app.py
