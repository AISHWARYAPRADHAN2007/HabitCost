<p align="center">
  <img src="assets/logo.png" width="170">
</p>

<h1 align="center">
💸 HabitCost
</h1>

<p align="center">
Track habits • Understand spending • Build wealth
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)

![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)

![Supabase](https://img.shields.io/badge/Supabase-Backend-green?logo=supabase)

![License](https://img.shields.io/badge/License-MIT-yellow)

</p>

## About

HabitCost is a modern personal finance application that helps users understand the real financial impact of everyday habits.

Instead of simply tracking expenses, HabitCost analyzes recurring spending, estimates long-term investment opportunities, generates insightful reports, and provides personalized financial recommendations.

The application was developed using **Python**, **Streamlit**, and **Supabase**, with a premium dark-themed interface inspired by modern SaaS products.

# Features

✅ Secure Authentication

- Login
- Sign Up
- Password Reset

---

✅ Habit Tracking

- Daily habit tracking
- Monthly calendar
- Recurring expenses
- Automatic & manual habits

---

✅ Dashboard

- Monthly spending
- Financial score
- Budget tracking
- Smart recommendations

---

✅ Analytics

- Spending trends
- Category analysis
- Interactive charts
- Monthly insights

---

✅ Investment Calculator

- Future value calculator
- Investment growth projection
- Opportunity cost visualization

---

✅ Reports

- Download PDF reports
- Download CSV reports
- Executive summary
- Spending history

---

✅ Settings

- Budget management
- Financial goals
- Personal notes
- Currency support

# Tech Stack

Frontend

- Streamlit
- HTML
- CSS

Backend

- Supabase

Programming Language

- Python

Libraries

- Pandas
- Plotly
- ReportLab

Authentication

- Supabase Auth

Database

- PostgreSQL (Supabase)

# Project Structure

```text
HabitCost/

│

├── app.py

├── auth.py

├── database.py

├── calculations.py

├── requirements.txt

├── README.md

│

├── assets/

│ ├── logo.png

│ └── style.css

│

├── pages/

│ ├── Habits

│ ├── Dashboard

│ ├── Analytics

│ ├── Investments

│ ├── Reports

│ └── Settings
```

# Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/HabitCost.git
```

Go inside the folder

```bash
cd HabitCost
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```