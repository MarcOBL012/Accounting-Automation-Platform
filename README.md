# Accounting System

A web-based accounting management system developed with **Django** for recording, tracking, and analyzing financial transactions. This application allows users to manage journal entries and automatically generates essential financial statements.

## 🚀 Features

- **Journal Entries:** Record daily financial transactions (Asientos Contables) with support for different account types and amounts.
- **Opening Balances:** Manage and set initial balances for specific accounts.
- **General Journal :** View a chronological record of all transactions.
- **Income Statement :** Automatic calculation of net income, including sales, costs, expenses, and taxes.
- **Statement of Financial Position:** Detailed view of Assets, Liabilities, and Equity.
- **General Ledger :** Filter ledgers by account type or specific account codes.
- **Responsive UI:** Built with Tailwind CSS and Flowbite for a modern, mobile-friendly interface.

## 🛠️ Tech Stack

- **Backend:** Python 3.8+, Django 4.2
- **Database:** SQLite (Default for development) / PostgreSQL compatible
- **Frontend:** HTML5, Tailwind CSS, JavaScript
- **Containerization:** Docker & Docker Compose

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- [Python](https://www.python.org/) (v3.8 or higher)
- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/) (Optional, for containerized deployment)

## 💻 Installation & Setup

### Option 1: Standard Installation (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/MarcOBL012/Accounting-Automation-Platform.git
   cd Accounting-Automation-Platform
   ```
2. **Create and activate a virtual environment**

```Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```
3. **Install dependencies**

```Bash

pip install -r requirements.txt
cd AppWeb
```
4. **Apply database migrations**

```Bash

python manage.py makemigrations
python manage.py migrate

```
5. Run the development server

```Bash

python manage.py runserver
```
6. **Access the application Open your browser and navigate to**
```
http://localhost:8000.
```

## 📬 Contact
If you use or extend this project, please add a note in the README or contact:

Marco Obispo — marco.obispo.l@uni.pe
