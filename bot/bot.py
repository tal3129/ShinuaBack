import datetime
import os
from uuid import uuid4

from backend.db_handler import DBHandler, get_number_of_pickups_by_date
from backend.db_structs import ProductStatus
from backend.db_structs import Product, Pickup 
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from backend.db_structs import ProductStatus

# Firebase credentials and app initialization

CHOOSE_PICKUP_TYPE = "האם אתה רוצה להתחיל איסוף חדש או להמשיך איסוף קיים?"
CHOOSE_NEW_PICKUP = "התחל איסוף חדש"
CHOOSE_OLD_PICKUP = "המשך איסוף קיים"
CHOOSE_ADD_ITEM = "הוסף מוצר חדש"
CHOOSE_FINISH_ADD_ITEMS = "סיים הוספת מוצרים"
CANCEL_PICKUP = "יצירת איסוף חדש בוטלה"
ITEM_ADDED_SUCCESSFULLY = "מוצר חדש נוסף! מה תרצה לעשות עכשיו?"
ITEM_DESCRIPTION = "האם יש מידע נוסף שתרצה לשמור על המוצר הזה? (תכניס מידע נוסף או תרשום דלג)"
ITEM_AMOUNT = "הכנס כמות פריטים מהמוצר הזה (בבקשה הכנס מספר)"
ITEM_NAME = "מה השם של המוצר הזה?"
PICKUP_SAVED = "מידע על איסוף חדש נשמר. תודה רבה!"
NO_ITEMS_ADDED = "לא נוספו מוצרים."
ITEM_PICTURE = "בבקשה תשלח תמונה של המוצר."
CHOOSE_PICKUP_TO_CONTINUE = 'איזה איסוף תרצה להמשיך?'
GET_COMPANY_NAME_FROM_USER = "מה השם של החברה?"
GET_ADDRESS_FROM_USER = 'מה השם של הכתובת ממנה אוספים?'
GET_NEW_ITEMS_FROM_USER = 'מעולה! אתה יכול להתחיל להוסיף עכשיו מוצרים לאיסוף. מה תרצה לעשות?'
OLD_PICKUPS_AMOUNT_TO_GET = 3
TELEGRAM_BOT_TOKEN = "5600448819:AAG2L0Z2k7BEIU3qP6MTY3gswW3GWoIFrWM"
firestore_db = DBHandler()

DEFAULT_PRODUCT_DICT = {'description': '', 'image_url_list': [], 'reserved': 0, 'origin': '', 'status': 0, 'amount': 0,
                        'name': ''}
DEFAULT_PICKUP_DICT = {'name': '', 'address': '', 'date': datetime.datetime.now(), 'products': set()}
# Conversation states
START_PICKUP, CONTINUE_PICKUP, ADD_COMPANY_NAME, ADD_ADDRESS, ADD_ITEMS, ADD_ITEM_PHOTO, ADD_ITEM_NAME, ADD_ITEM_AMOUNT, ADD_ITEM_INFO = range(
    9)


async def start_pickup(update, context):
    keyboard = [[KeyboardButton(CHOOSE_NEW_PICKUP), KeyboardButton(CHOOSE_OLD_PICKUP)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder=CHOOSE_PICKUP_TYPE)
    await update.message.reply_text(CHOOSE_PICKUP_TYPE, reply_markup=reply_markup)
    return START_PICKUP


async def started_new_pickup(update, context):
    context.user_data["pickup"] = Pickup(did="0", **(DEFAULT_PICKUP_DICT))
    await update.message.reply_text(GET_COMPANY_NAME_FROM_USER)
    return ADD_COMPANY_NAME


def get_old_pickups(amount_of_pickups):
    return get_number_of_pickups_by_date(firestore_db, amount_of_pickups)

def create_pickups_dict(old_pickups):
    pickups = {}
    for pickup in old_pickups["Pickups"]:
        pickups["{} {}".format(pickup["name"],str(pickup["date"]).split(" ")[0])] = pickup
    return pickups

def create_continue_pickup_buttons(old_pickups):
    keyboard_buttons = []
    for pickup_name in old_pickups.keys():
         keyboard_buttons.append([KeyboardButton(pickup_name)])
    return keyboard_buttons


async def select_old_pickup(update, context):
    old_pickups = get_old_pickups(OLD_PICKUPS_AMOUNT_TO_GET)
    old_pickups_dict = create_pickups_dict(old_pickups)
    keyboard = create_continue_pickup_buttons(old_pickups_dict)
    context.user_data["pickups"] = old_pickups_dict
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder=CHOOSE_PICKUP_TO_CONTINUE)
    await update.message.reply_text(CHOOSE_PICKUP_TO_CONTINUE, reply_markup=reply_markup)
    return CONTINUE_PICKUP


async def continued_old_pickup(update, context):
    context.user_data["pickup"] = Pickup(**(context.user_data["pickups"][update.message.text]))
    context.user_data["products"] = [] 
    keyboard = [[KeyboardButton(CHOOSE_ADD_ITEM), KeyboardButton(CHOOSE_FINISH_ADD_ITEMS)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder=GET_NEW_ITEMS_FROM_USER)
    await update.message.reply_text(GET_NEW_ITEMS_FROM_USER, reply_markup=reply_markup)
    return ADD_ITEMS


async def add_company_name(update, context):
    context.user_data["pickup"].name = update.message.text
    context.user_data["pickup"].date = datetime.datetime.now()
    await update.message.reply_text(GET_ADDRESS_FROM_USER)
    return ADD_ADDRESS


async def add_address(update, context):
    context.user_data["pickup"].address = update.message.text
    context.user_data["products"] = []
    keyboard = [[KeyboardButton(CHOOSE_ADD_ITEM), KeyboardButton(CHOOSE_FINISH_ADD_ITEMS)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder=GET_NEW_ITEMS_FROM_USER)
    await update.message.reply_text(GET_NEW_ITEMS_FROM_USER, reply_markup=reply_markup)
    return ADD_ITEMS


async def add_items(update, context):
    query = update.callback_query
    if query:
        query.answer()
    if update.message.text == CHOOSE_ADD_ITEM:
        context.user_data["products"].append(Product(did="0",**(DEFAULT_PRODUCT_DICT)))
        context.user_data["products"][-1].status = ProductStatus.COLLECTION
        context.user_data["products"][-1].reserved = 0
        context.user_data["products"][-1].origin = ""
        context.user_data["pickup"].products.add(context.user_data["products"][-1].did)
        await update.message.reply_text(ITEM_PICTURE)
        return ADD_ITEM_PHOTO
    elif update.message.text == CHOOSE_FINISH_ADD_ITEMS:
        if not context.user_data["products"]:
            await update.message.reply_text(NO_ITEMS_ADDED)
            return ConversationHandler.END
        else:
            context.user_data["pickup"].add_to_db(firestore_db)
            await update.message.reply_text(PICKUP_SAVED)
            return ConversationHandler.END


async def add_item_photo(update, context):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    file_id = str(uuid4())
    file_path = f'{file_id}.jpg'
    await photo_file.download_to_drive(file_path)
    remote_path = str(context.user_data["pickup"].did) + "/" + file_path
    image_url = firestore_db.upload_an_image(remote_path, file_path)
    os.remove(file_path)
    context.user_data['products'][-1].image_url_list.append(image_url)
    await update.message.reply_text(
        ITEM_NAME
    )
    return ADD_ITEM_NAME


async def add_item_name(update, context):
    context.user_data['products'][-1].name = update.message.text
    await update.message.reply_text(ITEM_AMOUNT)
    return ADD_ITEM_AMOUNT


async def add_item_amount(update, context):
    context.user_data['products'][-1].amount = update.message.text
    await update.message.reply_text(ITEM_DESCRIPTION)
    return ADD_ITEM_INFO


async def add_item_info(update, context):
    context.user_data['products'][-1].description = update.message.text
    keyboard = [[KeyboardButton(CHOOSE_ADD_ITEM), KeyboardButton(CHOOSE_FINISH_ADD_ITEMS)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.user_data["products"][-1].add_to_db(firestore_db)
    await update.message.reply_text(ITEM_ADDED_SUCCESSFULLY, reply_markup=reply_markup)
    return ADD_ITEMS


async def cancel(update, context):
    await update.message.reply_text(CANCEL_PICKUP)
    return ConversationHandler.END


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # Create a ConversationHandler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('התחל', start_pickup)],
        states={
            START_PICKUP: [MessageHandler(filters.Regex('^' + CHOOSE_NEW_PICKUP + '$'), started_new_pickup),
                        MessageHandler(filters.Regex('^' + CHOOSE_OLD_PICKUP + '$'), select_old_pickup)],
            CONTINUE_PICKUP: [MessageHandler(filters.TEXT, continued_old_pickup)],
            ADD_COMPANY_NAME: [MessageHandler(filters.TEXT, add_company_name)],
            ADD_ADDRESS: [MessageHandler(filters.TEXT, add_address)],
            ADD_ITEMS: [MessageHandler(filters.Regex("^(" + CHOOSE_ADD_ITEM + "|" + CHOOSE_FINISH_ADD_ITEMS + ")$"), add_items)],
            ADD_ITEM_PHOTO: [MessageHandler(filters.PHOTO, add_item_photo)],
            ADD_ITEM_NAME: [MessageHandler(filters.TEXT, add_item_name)],
            ADD_ITEM_AMOUNT: [MessageHandler(filters.Regex('^\d+$'), add_item_amount)],
            ADD_ITEM_INFO: [MessageHandler(filters.TEXT, add_item_info)]
        },
        fallbacks=[CommandHandler('ביטול', cancel)]
    )

    # Start the Bot
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
