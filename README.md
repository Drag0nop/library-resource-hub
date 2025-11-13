# 📚 Library Resource Hub  
A full-featured web-based Library Management System built using **Flask**, **SQLAlchemy**, and **TailwindCSS**.  
The system supports **User Authentication**, **book borrowing**, **return tracking**, **late fee calculation**, **admin management**, and **user analytics**.

---

## 🚀 Features

### 👤 **For Users**
- View all available books with search and advanced filtering  
- Borrow books with automatic **due date assignment (14 days)**  
- Return borrowed books  
- View full **borrowing history** with due dates and penalties
- See book availability in real time  
- Personalized **recommended books**  

---

### 🛠️ **For Admin**
- Admin dashboard with:
  - Total Books  
  - Borrowed Books  
  - Available Books  
- Manage Books (Add, Edit, Delete)  
- Manage Users  
- View recent borrows with:  
  - Download CSV for recent borrows  
- Category-based borrow analysis with **Chart.js**  
- Due dates, late fees & borrow tracking  

---

## 🧠 **Smart Features**
- Auto-check availability before borrowing  
- Auto-calculate late fee when returning
- OTP verifycation for password reset  
- Flash message fade-out animation  
- Clean UI built with **Tailwind CSS**  
- Pagination added everywhere:
  - Books list  
  - Recent borrows  
  - User borrowing history  

---

## 🧰 **Tech Stack**

### **Backend**
- Python 3
- Flask
- Flask-Login (Authentication)
- SQLAlchemy (ORM)
- MySQL (Configurable)

### **Frontend**
- HTML5
- Tailwind CSS
- Chart.js (Analytics)
- Vanilla JavaScript

---

## 📁 Folder Structure

library-hub/
├── app.py
├── models.py
├── .env 
├── requirements.txt
├── templates/
│ ├── login.html
│ ├── register.html
│ ├── home.html
│ ├── admin_dashboard.html
│ ├── manage_books.html
│ ├── edit_book.html
│ ├── manage_users.html
│ ├── user_history.html
│ ├── books.html
│ ├── verify_otp.html
│ ├── reset_password.html
│ ├── forgot_password.html
│ └── change_password.html
└── static/
  └── login.css

## 🔧 Installation & Setup

### 1️⃣ **Clone the Repository**

git clone https://github.com/your-username/library-resource-hub.git
cd library-resource-hub

### 2️⃣ Create Virtual Environment

python -m venv venv
venv/Scripts/activate   # Windows
source venv/bin/activate # Mac/Linux


### 3️⃣ Install Requirements

pip install -r requirements.txt

### 4️⃣ Run Application

python app.py

### Open the link

http://127.0.0.1:5000
