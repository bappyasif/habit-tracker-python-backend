import os
import resend
import dotenv

# Initialize Resend with your API key from environment variables
resend.api_key = os.getenv("RESEND_API_KEY")

def send_welcome_email(user_email: str, user_name: str):
    try:
        params: resend.Emails.SendParams = {
            "from": "HabitFlow <onboarding@resend.dev>", # Use your verified domain later in production
            "to": [user_email],
            "subject": "Welcome to HabitFlow! 🚀",
            "html": f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Hello {user_name},</h2>
                    <p>Welcome to <b>HabitFlow</b>! We are thrilled to help you track your habits, build consistency, and reach your goals.</p>
                    <p>You can now log in, set up your daily steps, and stay on top of your streaks.</p>
                    <br>
                    <p>Best regards,</p>
                    <p><b>The HabitFlow Team</b></p>
                </div>
            """
        }

        email = resend.Emails.send(params)
        print(f"Email sent successfully to {user_email}: {email}")
        return email
    except Exception as e:
        print(f"Failed to send email to {user_email}: {e}")
        return None


def send_habit_completion_email(user_email: str, user_name: str):
    try:
        params: resend.Emails.SendParams = {
            "from": "HabitFlow <onboarding@resend.dev>",
            "to": [user_email],
            "subject": "All steps completed for today! 🔥",
            "html": f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Amazing job, {user_name}!</h2>
                    <p>You have officially completed all your habit steps for today. Keep up the great momentum and protect your streak!</p>
                    <br>
                    <p>Keep crushing it,</p>
                    <p><b>The HabitFlow Team</b></p>
                </div>
            """
        }

        email = resend.Emails.send(params)
        print(f"Milestone email sent to {user_email}: {email}")
        return email
    except Exception as e:
        print(f"Failed to send milestone email: {e}")
        return None
    
def send_habit_deleted_email(user_email: str, user_name: str):
    try:
        params: resend.Emails.SendParams = {
            "from": "HabitFlow <onboarding@resend.dev>",
            "to": [user_email],
            "subject": "Habit deleted successfully! 🎉",
            "html": f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Good job, {user_name}!</h2>
                    <p>Your habit has been successfully deleted. You can always add it back later if you change your mind.</p>  
                    <br>
                    <p>Keep crushing it,</p>
                    <p><b>The HabitFlow Team</b></p>
                </div>
            """
        }

        email = resend.Emails.send(params)
        print(f"Milestone email sent to {user_email}: {email}")
        return email
    except Exception as e:
        print(f"Failed to send milestone email: {e}")
        return None