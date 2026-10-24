# RailConnect — Train Reservation Portal

A responsive college case-study project built with HTML5, CSS3, JavaScript, Python Flask, and SQLite.

## Features
- Responsive home page and navigation
- Search sample trains by source and destination
- Booking form with validation and fare calculation
- SQLite persistence for trains and bookings
- Booking confirmation and lookup using PNR + mobile number
- Demo admin dashboard with booking totals, revenue summary, and cancellation status
- Contact form demonstration
- HTML5 semantic elements, inline/internal/external CSS examples, responsive CSS Grid/Flexbox, and form controls

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted `RailConnect` folder in VS Code.
3. Open the terminal in that folder.
4. Create a virtual environment:
   ```powershell
   python -m venv venv
   ```
5. Activate it:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt:
   ```bat
   venv\Scripts\activate.bat
   ```
6. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
7. Start the app:
   ```powershell
   python app.py
   ```
8. Open `http://127.0.0.1:5000` in your browser.

The `railconnect.db` SQLite database is created automatically when the app starts.

## Demo admin
- URL: `http://127.0.0.1:5000/admin/login`
- Username: `admin`
- Password: `rail123`

This is a demonstration login only. Do not use these credentials or the development server for a real public service.

## View the database
The database file is `railconnect.db` in the project folder. Open it with a SQLite viewer such as DB Browser for SQLite, then inspect the `trains` and `bookings` tables. Alternatively, use Python:
```powershell
python -c "import sqlite3; c=sqlite3.connect('railconnect.db'); print(c.execute('SELECT * FROM trains').fetchall()); print(c.execute('SELECT * FROM bookings').fetchall()); c.close()"
```

## Important scope notes
- Train names, schedules, and fares are sample data for a college demonstration, not live railway information.
- This project does not connect to IRCTC/Indian Railways and cannot issue real tickets.
- No real payment processing is implemented.
- The contact form does not send email.
- Admin demo credentials are hard-coded for learning purposes; replace authentication and security settings before any real deployment.
