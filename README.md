# 💸 The Real Cost of Habits

A Streamlit app that turns everyday habits (coffee, Uber, takeout, subscriptions...)
into numbers that actually register: cost per week/month/year, hours spent per year,
and what that money could have grown into if invested instead.

## Features
- Editable table (add/remove/edit any habit, right in the browser)
- Auto-calculated weekly / monthly / yearly / 5-year cost
- Time cost in hours and days per year
- "Opportunity cost" projection — what the money could be worth if invested
- Charts: cost by habit, cost by category, time by habit, growth-over-time
- Export/import your habits as CSV so your data isn't lost between sessions

## Run locally

```bash
git clone <your-repo-url>
cd habit-cost-calculator
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy for free (GitHub + Streamlit Community Cloud)

1. Create a new GitHub repo and push these files (`app.py`, `requirements.txt`, `README.md`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, pick your repo/branch, and set the main file to `app.py`.
4. Click **Deploy** — you'll get a public URL in about a minute.

Any time you push new commits to the repo, the deployed app updates automatically.

## How the math works
- **Weekly cost** = cost per occurrence × times per week
- **Yearly cost** = weekly cost × 52
- **Time cost** = minutes per occurrence × times per week, converted to hours/days per year
- **Investment projection** uses the future value of a recurring weekly contribution,
  compounded weekly at your chosen annual rate — i.e. "what if this money went into
  an index fund instead of a coffee cup."

## Notes on persistence
Streamlit Community Cloud apps don't have a database by default, and session state
resets between visits/devices. Use the **Export CSV** / **Load CSV** buttons in the
sidebar to save your habits and bring them back next time.

## Ideas to extend
- Add authentication + a real database (e.g. Supabase, SQLite) for true persistence
- Add a "goal" mode: "cut this habit in half — see the new yearly total"
- Add category budgets/limits with visual warnings
- Mobile-friendly quick-add widget for logging habits as they happen
