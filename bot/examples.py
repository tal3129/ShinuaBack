import telegram
import telegram.ext as ext
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import base64


TELEGRAM_BOT_TOKEN = "5906453386:AAHbAL8SZKoCDUih-PHOng2l_158pZl3eO4"
# Firebase setup
cred = credentials.Certificate(r'C:\Users\roees\OneDrive\Desktop\cfc\shinua-a57e9-firebase-adminsdk-cv3ln-910e0cc268.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://shinua-a57e9-default-rtdb.firebaseio.com/'
})
ref = db.reference('images') # create a reference to the 'images' node in your database

# Telegram bot setup
bot = telegram.Bot(TELEGRAM_BOT_TOKEN)

def handle_image(update, context):
    chat_id = update.message.chat_id
    file_id = update.message.photo[-1].file_id # get the ID of the last (highest quality) photo sent by the user
    file = context.bot.get_file(file_id)
    file.download('image.jpg') # download the image to the server
    with open('image.jpg', 'rb') as f:
        image_data = f.read() # read the image data as bytes
    ref.push().set({'image_data': base64.b64encode(image_data).decode('utf8'), 'chat_id': chat_id}) # upload the image data and chat ID to the database
    a = ref.get()
    print(a)
    update.message.reply_text('Thanks for the image! It has been uploaded to the database.')


# start the bot and listen for messages
update_queue = []
updater = ext.Updater(token=TELEGRAM_BOT_TOKEN)
updater.dispatcher.add_handler(ext.MessageHandler(ext.Filters.photo, handle_image))
updater.start_polling()
updater.idle()

