import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from db_handler import db_handler, get_number_of_pickups_by_date
from db_structs import Product, Pickup, COLLECTION
from uuid import uuid4
import os
import datetime

# Firebase credentials and app initialization
CHOOSE_PICKUP_TYPE = 'Do you want to start a new pickup or continue an old one?'
CHOOSE_NEW_PICKUP = "New pickup"
CHOOSE_OLD_PICKUP = "Continue pickup"
CHOOSE_ADD_ITEM = "Add new item"
CHOOSE_FINISH_ADD_ITEMS = "Finish adding items"
CANCEL_PICKUP = "Pickup creation cancelled."
ITEM_ADDED_SUCCESSFULLY = "Item added! What would you like to do next?"
ITEM_DESCRIPTION = "Any additional information about this item? (Please enter a text or skip)"
ITEM_AMOUNT = "What is the amount of this item? (Please enter a number)"
ITEM_NAME = "What is the name of this item?"
PICKUP_SAVED = "Pickup information saved. Thank you!"
NO_ITEMS_ADDED = "No items added."
ITEM_PICTURE = "Please send me a photo of the item."
CHOOSE_PICKUP_TO_CONTINUE = 'Which pickup would you like to continue?'
GET_COMPANY_NAME_FROM_USER = "What is the name of the company?"
GET_ADDRESS_FROM_USER = 'What is the pickup address?'
GET_NEW_ITEMS_FROM_USER = 'Great! Now you can start adding items to the pickup. What would you like to do?'
OLD_PICKUPS_AMOUNT_TO_GET = 3
TELEGRAM_BOT_TOKEN = "6281123162:AAEm29V4M8K8PU0M27zw61OR32lFtlKByGE"
firestore_db = db_handler()

DEFAULT_PRODUCT_DICT = {'description': '', 'image_url_list': [], 'reserved': 0, 'origin': '', 'status': 0, 'amount': 0, 'name': ''}
DEFAULT_PICKUP_DICT = {'name':'', 'address':'', 'date': datetime.datetime.now(), 'products':set()}
# Conversation states
START_PICKUP, CONTINUE_PICKUP, ADD_COMPANY_NAME, ADD_ADDRESS, ADD_ITEMS, ADD_ITEM_PHOTO, ADD_ITEM_NAME, ADD_ITEM_AMOUNT, ADD_ITEM_INFO = range(9)

async def start_pickup(update, context):
    keyboard = [[KeyboardButton(CHOOSE_NEW_PICKUP), KeyboardButton(CHOOSE_OLD_PICKUP)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder=CHOOSE_PICKUP_TYPE)
    await update.message.reply_text(CHOOSE_PICKUP_TYPE, reply_markup=reply_markup)
    return START_PICKUP

async def started_new_pickup(update, context):
    context.user_data["pickup"] = Pickup(did="0",**(DEFAULT_PICKUP_DICT))
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
        context.user_data["products"][-1].status = COLLECTION
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
   