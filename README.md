# 📚 Library Resource Hub  
A full-featured web-based Library Management System built using **Flask**, **SQLAlchemy**, and **TailwindCSS**.  
The system supports **User Authentication**, **book borrowing**, **return tracking**, **late fee calculation**, **admin management**, and **user analytics**.

---

## 🚀 Features

### 👤 **For Users**
- View all available books with search and advanced filtering  
- Borrow books with automatic **due date assignment (14 days)**  
- Return borrowed books  
- View full **borrowing history**  
- See real-time book availability  
- Personalized **recommended books**  

---

### 🛠️ **For Admin**
- Dashboard showing:
  - Total Books  
  - Borrowed Books  
  - Available Books  
- Manage Books (Add / Edit / Delete)  
- Manage Users  
- Recent borrows section with:
  - CSV Download  
  - Pagination  
- Category Analytics using **Chart.js**  
- Late fee & due date management  

---

## 🧠 Smart Features
- Auto-check book availability  
- 14-day due date  
- Automatic late fee calculation  
- OTP verification for password reset  
- Flash messages fade automatically  
- Tailwind-based UI  
- Global pagination:
  - Books page  
  - Borrow history  
  - Admin recent borrows  

---

## 🧰 Tech Stack

### **Backend**
- Python 3
- Flask
- Flask-Login
- SQLAlchemy
- MySQL (or SQLite)

### **Frontend**
- HTML5  
- TailwindCSS  
- JavaScript  
- Chart.js  

---

## 📁 Folder Structure

```
library-hub/
├── app.py
├── models.py
├── .env 
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── admin_dashboard.html
│   ├── manage_books.html
│   ├── edit_book.html
│   ├── manage_users.html
│   ├── user_history.html
│   ├── books.html
│   ├── verify_otp.html
│   ├── reset_password.html
│   ├── forgot_password.html
│   └── change_password.html
└── static/
    └── login.css
```

---

## 🔧 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/library-resource-hub.git
cd library-resource-hub
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# Windows
venv/Scripts/activate

# Mac/Linux
source venv/bin/activate
```

### 3️⃣ Install Requirements
```bash
pip install -r requirements.txt
```

### 4️⃣ Run Application
```bash
$env:EMAIL_BACKEND = "console"   # Only for Windows PowerShell
python app.py
```

### ✔ Open in Browser
```
http://127.0.0.1:5000
```

---