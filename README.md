# Thrive
#### Video Demo:  <https://youtu.be/1LnJAKYIYuk>

---

## Description
Thrive is my CS50 final project that reimagines the simple productivity app. It's a mindful web application designed to help users, especially students, manage not just their daily tasks but also their mental well-being. In a world of high-pressure "hustle culture," Thrive offers a gentle, cozy, and non-judgmental space to be productive, reflect on your feelings, and find a moment of calm.

The app is built on the idea that productivity and mental health are linked. It combines a day-focused task manager with a data-driven mood journal and mindfulness tools, all wrapped in a unique, cozy-pixel aesthetic.

---

## Key Features
* **Secure Authentication:** Full registration and login system with password hashing and session management.
* **Data-Driven Insight Dashboard:** The homepage features a dynamic "Insights" block powered by the **pandas** library. After logging 3 or more moods, it provides users with three key data points:
    1.  Their most common (modal) mood.
    2.  A personalized message based on their most recently logged mood.
    3.  An encouraging count of their total mood logs.
* **Gentle Task Manager:** Users can add daily goals to a "To-Do" list. When a task is completed:
    * A rewarding pop-up appears with a random cat photo and a motivational quote.
    * The task is moved to a "Completed" list that **only shows tasks from today**, preventing clutter and promoting a fresh start each day.
* **Integrated Mood Journal:** On the "Log My Mood" page, users can select an emoji for their current mood and optionally write a private journal entry.
* **Reflection Viewer:** On the same "Log My Mood" page, users can review all their past journal entries in a clean, dropdown accordion list. They have full control to **delete** any past reflection.
* **Calm Zone:** A dedicated page with an interactive breathing animation (with start and stop controls) to help users pause and find a moment of calm.
* **Custom Cozy-Pixel Aesthetic:** The app uses `nes.css` as a base but heavily overrides it with custom CSS to create a unique feel:
    * A soft, pastel color palette.
    * The 'Quicksand' font for a cozy, rounded feel.
    * Custom "cartoon" headings with text-shadow outlines.
    * Animated floating star background.
    * Dynamic, blurred image backgrounds for the login and home pages.

---

## Technical Breakdown & File Structure

Thrive is a web application built with Python and Flask.

### Backend (`app.py`)
`app.py` is the core of the application, running the Flask server and managing all routes and backend logic.
* **Database:** Uses `sqlite3` to connect to the `thrive.db` database.
* **Authentication:**
    * `@login_required`: A decorator that protects all main pages, redirecting unauthenticated users to the login page.
    * `/register`: Handles user registration, hashes passwords using `generate_password_hash`, and saves new users to the database.
    * `/login`: Manages user login, verifies credentials with `check_password_hash`, and creates a user session.
    * `/logout`: Clears the session.
* **Core Routes:**
    * `/` (Home): Fetches tasks and calls `get_user_insights()` from `helpers.py` to get the data for the dashboard.
    * `/planner`: Handles `GET` requests to display the planner page and `POST` requests to add new tasks. The SQL query is specifically designed to fetch all 'todo' tasks and only 'done' tasks from the current day.
    * `/mood`: A dual-purpose route. On `POST`, it saves a new mood and (optional) note to the database. On `GET`, it fetches all past journal entries from the database to display in the "Past Reflections" list.
    * `/calm`: A simple route that renders the breathing exercise page.
* **API-style Routes:**
    * `/update_task/<int:task_id>`: A `POST` route that updates a task's status from 'todo' to 'done'.
    * `/delete_reflection/<int:entry_id>`: A `POST` route that securely deletes a journal entry from the `moods` table based on its unique ID and the logged-in user's ID.

### Data Science (`helpers.py`)
This file contains the data analysis logic for the insight dashboard.
* `get_user_insights(user_id)`:
    * Connects to `thrive.db`.
    * Uses `pandas.read_sql_query` to load the user's mood history into a DataFrame.
    * If the user has fewer than 3 logs, it returns a simple string.
    * If the user has enough data, it performs analysis:
        * `df_moods['mood'].mode()[0]` finds the most common mood.
        * `df_moods.iloc[-1]['mood']` finds the most recent mood.
        * `len(df_moods)` counts the total logs.
    * It then returns a Python dictionary containing all three formatted insight strings.

### Database (`schema.sql`)
The blueprint for the SQLite database. It defines three tables:
1.  `users`: Stores `id`, `username`, and password `hash`.
2.  `tasks`: Stores `id`, `user_id` (foreign key), `content`, `status` ('todo' or 'done'), and `created_at` timestamp.
3.  `moods`: Stores `id`, `user_id` (foreign key), `mood` (e.g., 'happy'), `note` (the text journal), and `logged_at` timestamp.

### Frontend (`templates/` & `static/`)
The frontend is built with HTML, CSS, and vanilla JavaScript, using Jinja for templating.

* `layout.html`: The master template.
    * Imports all Google Fonts and CSS files.
    * Contains two dynamic blocks: `{% block body_class %}` (which allows pages like `login.html` to have a different background) and `{% block animations %}` (where scripts for stars and pop-ups are placed).
* `login.html` & `register.html`:
    * Set the `body_class` to `login-page` to get the special background.
    * Use the `.center-container` and `.app-title` classes for a clean, centered layout.
* `index.html`: Renders the dashboard. It uses a Jinja `{% if insight is mapping %}` check to safely unpack and display the three insights from the `insight` dictionary.
* `planner.html`: The most complex frontend page.
    * It includes the `<dialog>` element for the cat pop-up.
    * The `<script>` is placed in the `animations` block and waits for `DOMContentLoaded`.
    * It uses `querySelectorAll` to find all "Done!" buttons and attach `submit` event listeners.
    * Inside the listener, `event.preventDefault()` stops the form from submitting normally. It then picks a random cat, updates the `<img>` and `<p>` tags, and shows the pop-up with `rewardDialog.showModal()`.
    * When the pop-up is closed, a *new* event listener submits the original form, marking the task as complete.
* `mood.html`:
    * Contains the form to log a new mood.
    * Below the form, it uses a Jinja `{% for %}` loop to render the "Past Reflections" list.
    * Each entry is a `<details>` and `<summary>` HTML tag, creating a natural dropdown.
    * Inside each dropdown is a mini-form that `POST`s to `/delete_reflection/{{ entry.id }}`.
* `static/style.css`: This is the heart of the app's unique design.
    * **Design Choice:** I chose `nes.css` as a base for its pixel-art buttons and containers but wanted a softer, more modern and cozy feel.
    * **Fonts:** I overrode the default pixel font with 'Quicksand' to make the app feel more rounded and friendly.
    * **Colors:** I defined a full pastel color palette (`--primary-color`, etc.) and used it to override all of `nes.css`'s default bright colors.
    * **Headings:** I created the `.page-heading` class with a `text-shadow` to create a bold, 2D "cartoon" outline that fits the cozy-pixel theme.
    * **Backgrounds:** The `body.login-page` and `body.home-page` rules use `background-image` along with `backdrop-filter: blur()` to create a soft, layered, and beautiful background effect.
    * **Animations:** The file contains the `@keyframes float` and `.star` rules for the floating star animation.