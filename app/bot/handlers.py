import os 
import subprocess
from telebot import types
from bot.config import BOT_PASSWORD, EXCEL_DIR

user_states = {}

def register_handkers(bot):
    @bot.message_handler(commands=['start', 'help'])  #Respond to request
    def start_command(message):
        """
        Respond to the /start and /help commands.
        """
        user_states[message.chat.id] = {"is_auth": False}
        bot.send_message(message.chat.id, 'Hello! This is a private bot. To continue, complete /authorize command for authorization.')

    @bot.message_handler(commands=['authorize'])
    def authorize_command(message):
        """
        Authorize the user.
        """
        bot.send_message(message.chat.id, 'Enter the password to continue.')
        bot.register_next_step_handler(message, process_password)
    
    def process_password(message):
        """
        Process the password entered by the user.
        """
        if message.text == BOT_PASSWORD:
            user_states[message.chat.id]["is_auth"] = True
            bot.send_message(message.chat.id, 'Authorization successful. Enter the start date in the format YYYY-MM-DD.')
            bot.register_next_step_handler(message, process_start_date)
        else:
            bot.send_message(message.chat.id, 'Incorrect password. Try again.')
            bot.register_next_step_handler(message, process_password)

    def process_start_date(message):
        """
        Process the start date entered by the user.
        """
        if not user_states.get(message.chat.id, {}).get("is_auth"):
            bot.send_message(message.chat.id, 'You are not authorized. Please complete the /authorize command for authorization.')
            return
        
        user_states[message.chat.id]["start_date"] = message.text
        bot.send_message(message.chat.id, 'Enter the end date in the format YYYY-MM-DD')
        bot.register_next_step_handler(message, process_end_date)
    
    def process_end_date(message):
        """
        Process the end date entered by the user.
        """
        if not user_states.get(message.chat.id, {}).get("is_auth"):
            bot.send_message(message.chat.id, 'You are not authorized. Please complete the /authorize command for authorization.')
            return
        
        user_states[message.chat.id]["end_date"] = message.text
        bot.send_message(message.chat.id, 'The file is being created. Please wait...')
        generate_excel_file(message.chat.id)

    def generate_excel_file(message):
        """
        Generate an Excel file with the specified data.
        """
        start_date = user_states[message.chat.id]["start_date"]
        end_date = user_states[message.chat.id]["end_date"]
        file_path = os.path.join(EXCEL_DIR, f'tasks-{start_date}-{end_date}.xlsx')

        if not os.path.exists(file_path):
            subprocess.run(["python", "parse.py", f"--start={start_date}", f"--end={end_date}"])
        else:
            bot.send_message(message.chat.id, 'The file has already been created. Enter /get_excel to download the file.')
        
        user_states[message.chat.id]["file_path"] = file_path
        bot.send_message(message.chat.id, 'The file has been created. Enter /get_excel to download the file.')

    @bot.message_handler(commands=['get_excel'])
    def get_excel_command(message):
        """
        Send the Excel file to the user.
        """
        file_path = user_states.get(message.chat.id, {}).get("file_path")
        if file_path and os.path.exists(file_path):
            bot.send_document(message.chat.id, types.InputFile(file_path))
        else:
            bot.send_message(message.chat.id, 'The file was not found.')
            
