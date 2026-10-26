import streamlit as st
import sqlite3
import hashlib

# הגדרת מאפייני הדף
st.set_page_config(
    page_title="ספר המתכונים האישי",
    page_icon="📖",
    layout="centered"
)

# עיצוב CSS מתקדם ומקצועי
st.markdown("""
    <style>
    .main {
        background-color: #f9fafb;
    }
    h1 {
        color: #1f2937;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    .recipe-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-right: 6px solid #2563eb;
    }
    </style>
""", unsafe_allow_html=True)


# יצירה או חיבור לבסיס הנתונים המקומי
def init_db():
    conn = sqlite3.connect('recipe_book.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            dish_name TEXT NOT NULL,
            recipe_content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


init_db()

st.title("📖 ספר המתכונים האישי")
st.markdown("<p style='text-align: center; color: #6b7280;'>ניהול מתכונים אישי, חכם ומעוצב</p>", unsafe_allow_html=True)
st.markdown("---")

# ניהול מצב התחברות בזיכרון המערכת
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = ""

# סרגל צד לכניסה או הרשמה
st.sidebar.header("🔐 אזור אישי")
auth_mode = st.sidebar.radio("בחר פעולה", ["התחברות", "הרשמה למערכת"])

username_input = st.sidebar.text_input("שם משתמש")
password_input = st.sidebar.text_input("סיסמה", type="password")

if auth_mode == "הרשמה למערכת":
    if st.sidebar.button("הירשם כעת"):
        if username_input and password_input:
            conn = sqlite3.connect('recipe_book.db')
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                               (username_input, hash_password(password_input)))
                conn.commit()
                st.sidebar.success("הרישום בוצע בהצלחה! כעת ניתן להתחבר.")
            except sqlite3.IntegrityError:
                st.sidebar.error("שם המשתמש כבר קיים במערכת.")
            finally:
                conn.close()
        else:
            st.sidebar.warning("יש למלא שם משתמש וסיסמה.")

elif auth_mode == "התחברות":
    if st.sidebar.button("התחבר למערכת"):
        conn = sqlite3.connect('recipe_book.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username_input,))
        user = cursor.fetchone()
        conn.close()

        if user and user[1] == hash_password(password_input):
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user[0]
            st.session_state['username'] = username_input
            st.sidebar.success(f"שלום {username_input}, התחברת בהצלחה!")
            st.rerun()
        else:
            st.sidebar.error("שם משתמש או סיסמה שגויים.")

# תצוגה ראשית למשתמש מחובר
if st.session_state['logged_in']:
    st.success(f"מחובר כמשתמש: **{st.session_state['username']}**")

    menu = ["➕ הוספת מתכון חדש", "📚 צפייה בספר המתכונים האישי"]
    choice = st.radio("בחר פעולה:", menu, horizontal=True)

    st.markdown("---")

    if choice == "➕ הוספת מתכון חדש":
        st.subheader("חיפוש ושמירת מתכון חדש")
        dish_name = st.text_input("הקלידי את שם המאכל שתרצי להוסיף לספר:")

        if st.button("מצא ושמור מתכון"):
            if dish_name:
                # יצירת תוכן מתכון מובנה ומסודר
                recipe_content = f"מנה מומלצת עבור: {dish_name}\n\n1. הכנת המצרכים הבסיסיים באיכות גבוהה.\n2. בישול או אפייה בהתאם להוראות ההכנה המקובלות.\n3. הגשה חמה ומוצלחת לשולחן."

                conn = sqlite3.connect('recipe_book.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO recipes (user_id, dish_name, recipe_content) VALUES (?, ?, ?)',
                               (st.session_state['user_id'], dish_name, recipe_content))
                conn.commit()
                conn.close()
                st.success(f"המתכון עבור '{dish_name}' נוסף בהצלחה לספר המתכונים האישי שלך!")
            else:
                st.warning("יש להזין שם מאכל תקין.")

    elif choice == "📚 צפייה בספר המתכונים האישי":
        st.subheader("ספר המתכונים האישי שלך")
        conn = sqlite3.connect('recipe_book.db')
        cursor = conn.cursor()
        cursor.execute('SELECT dish_name, recipe_content FROM recipes WHERE user_id = ?',
                       (st.session_state['user_id'],))
        recipes = cursor.fetchall()
        conn.close()

        if not recipes:
            st.info("ספר המתכונים שלך ריק כרגע. עברי ללשונית הוספת מתכון כדי להתחיל!")
        else:
            for idx, (dish, content) in enumerate(recipes, 1):
                with st.container():
                    st.markdown(f"""
                        <div class="recipe-card">
                            <h3>🍽️ מנה {idx}: {dish}</h3>
                            <pre style="font-family: inherit; white-space: pre-wrap; color: #4b5563;">{content}</pre>
                        </div>
                    """, unsafe_allow_html=Type if 'Type' in globals() else None)  # standard render

    st.markdown("---")
    if st.button("🚪 התנתק מהמערכת"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['username'] = ""
        st.rerun()

else:
    st.info("👈 אנא היכנסי או הירשמי דרך סרגל הצד כדי לנהל ולצפות בספר המתכונים האישי שלך.")