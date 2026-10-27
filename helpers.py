import pandas as pd
import sqlite3
# No longer need 'random'
# import random 

def get_user_insights(user_id):
    """Analyzes a user's mood data to provide a personalized insight."""

    try:
        conn = sqlite3.connect('thrive.db')
        
        query = "SELECT mood, logged_at FROM moods WHERE user_id = ?"
        df_moods = pd.read_sql_query(query, conn, params=(user_id,))

        conn.close()

        # If not enough data, return a simple string.
        if len(df_moods) < 3:
            return "Log your mood for a few more days to unlock your first insight! 📝"

        # --- Create a dictionary to hold all insights ---
        insights = {}

        # --- Insight 1: Most Common Mood ---
        most_common_mood = df_moods['mood'].mode()[0]
        common_mood_messages = {
            'happy': "Lately, your most frequent mood has been 'happy' 😊. Keep shining!",
            'calm': "Lately, your most frequent mood has been 'calm' 😌. It's great you're finding moments of peace.",
            'tired': "Lately, your most frequent mood has been 'tired' 😴. Please remember to rest and recharge your batteries.",
            'anxious': "Lately, your most frequent mood has been 'anxious' 😟. Be gentle with yourself and remember to breathe.",
            'sad': "Lately, your most frequent mood has been 'sad' 😢. Sending you extra strength. Remember that it's okay to not be okay."
        }
        insights['common'] = common_mood_messages.get(most_common_mood, "You've logged a variety of moods!")


        # --- Insight 2: Comment on the *Last* Logged Mood ---
        last_mood = df_moods.iloc[-1]['mood'] # .iloc[-1] gets the very last row
        last_mood_messages = {
            'happy': "You were feeling 'happy' 😊 on your last log. That's wonderful to see!",
            'calm': "You were feeling 'calm' 😌 last time you checked in. Hoping you can carry that peace into today.",
            'tired': "You were feeling 'tired' 😴 on your last log. Make sure to prioritize rest and be kind to your body today.",
            'anxious': "You were feeling 'anxious' 😟 last time. Remember, your feelings are valid. Take a deep breath—you've got this.",
            'sad': "You were feeling 'sad' 😢 on your last log. Just a reminder that you're not alone and this feeling will pass."
        }
        insights['last'] = last_mood_messages.get(last_mood, "You checked in recently.")


        # --- Insight 3: Total Moods Logged ---
        total_logs = len(df_moods)
        insights['total'] = f"You've checked in with your feelings {total_logs} times. That's a great step in self-awareness! 🌟"


        # --- Finally: Return the whole dictionary ---
        return insights

    except Exception as e:
        print(f"--- ERROR IN get_user_insights ---: {e}")
        return "Could not generate an insight at this time." # Return a string for errors too