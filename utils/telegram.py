import requests

# Replace these with your bot's token and chat/channel ID
API_TOKEN = "5859153132:AAHva7RSPGoN1XQ_DD1EcHwRaWrw-ozzpVk"
CHAT_ID = "-819945328"

def send_telegram_message(message: str):
    """
    Sends a message to the predefined Telegram chat or channel.

    :param message: The message to be sent.
    """
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'  # You can use HTML or Markdown formatting
    }
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# Example usage:
if __name__ == "__main__":
    send_telegram_message("Hello, this is a test message!")
