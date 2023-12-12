import telebot
import wikipedia
import sqlite3
from database import Database
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

wikipedia.set_lang("ru")

class Bot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.db = None

    def start(self, message):
        self.bot.reply_to(message, "Добро пожаловать! Этот бот позволяет создавать и взаимодействовать с заметками,"
                                   " а также осуществлять поиск в Википедии. Для регистрации введите /register")

    def register(self, message):
        user_id = message.from_user.id
        self.db = Database(user_id)
        self.db.create_table()
        self.bot.reply_to(message, "Регистрация прошла успешно!")

    def add_note(self, message):
        if self.db is None:
            self.bot.send_message(message.chat.id, "Вы должны зарегистрироваться с помощью команды /register")
        else:
            try:
                note_text = message.text.split('/addnote ')[1]
                self.db.add_note(note_text)
                self.bot.send_message(message.chat.id, "Заметка сохранена!")
            except IndexError:
                self.bot.send_message(message.chat.id, "Необходимо ввести заметку после команды /addnote")

    def get_user_notes(self, message):
        if self.db is None:
            self.bot.send_message(message.chat.id, "Вы должны зарегистрироваться с помощью команды /register")
        else:
            notes = self.db.get_notes()
            if len(notes) > 0:
                for i, note in enumerate(notes, 1):
                    self.bot.send_message(message.chat.id, f"{i}. {note[0]}")
            else:
                self.bot.send_message(message.chat.id, "У вас нет заметок")

    def delete_note(self, message):
        if self.db is None:
            self.bot.send_message(message.chat.id, "Вы должны зарегистрироваться с помощью команды /register")
        else:
            try:
                note_id = int(message.text.split('/deletenote ')[1])
                conn = sqlite3.connect(f'notes_{self.db.user_id}.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("SELECT note FROM notes")
                notes = cursor.fetchall()
                if note_id < 1 or note_id > len(notes):
                    self.bot.send_message(message.chat.id, "Неправильный идентификатор заметки")
                else:
                    note_to_delete = notes[note_id - 1][0]
                    cursor.execute("DELETE FROM notes WHERE note=?", (note_to_delete,))
                    conn.commit()
                    conn.close()
                    self.bot.send_message(message.chat.id, "Заметка удалена!")
            except IndexError:
                self.bot.send_message(message.chat.id, "Необходимо ввести порядковый номер заметки после команды /deletenote")
            except ValueError:
                self.bot.send_message(message.chat.id, "Идентификатор должен быть числом")

    def search(self, message):
        try:
            search_term = message.text.split('/search ')[1]
            self.bot.send_message(message.chat.id, wikipedia.summary(search_term, sentences=90))
        except IndexError:
            self.bot.send_message(message.chat.id, "Необходимо ввести поисковый запрос после команды /search")
        except wikipedia.DisambiguationError as e:
            self.bot.send_message(message.chat.id, "Найдено несколько возможных статей. Уточните запрос.")
            for option in e.options:
                self.bot.send_message(message.chat.id, option)
        except wikipedia.PageError:
            self.bot.send_message(message.chat.id, "Статья не найдена")

    def run(self):
        self.bot.polling()


bot = Bot(os.getenv('TOKEN'))
bot.bot.message_handler(commands=['start'])(bot.start)
bot.bot.message_handler(commands=['register'])(bot.register)
bot.bot.message_handler(commands=['addnote'])(bot.add_note)
bot.bot.message_handler(commands=['notes'])(bot.get_user_notes)
bot.bot.message_handler(commands=['deletenote'])(bot.delete_note)
bot.bot.message_handler(commands=['search'])(bot.search)

bot.run()