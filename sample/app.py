import copy
import run_generic_store
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import time
import sys


class Shop(object):
    def __init__(self):
        self.shopify_api_key = ''
        self.shopify_api_password = ''
        self.shopify_hostname = ''
        self.telegram_api_key = ''


class CreateShopBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.list_shops = []
        self.temp_bot = Shop()
        self.shop_names = []

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        print msg
        if chat_type == 'private' and content_type == 'text':
            text = msg['text']
            if text == '/create' or text == '/start':   #user may be restarting flow
                self.temp_bot = Shop()
                text = 'Great! Please send me your Shopify API key'
            elif text == '/delete':
                bot.sendMessage(chat_id=chat_id,
                                text='Which shop would you like to delete?',
                                reply_markup=self.get_shops_keyboard())
            elif text in self.shop_names:
                self.shop_names.remove(text)
                for shop in self.list_shops:
                    if shop.shopify_hostname == text:
                        self.list_shops.remove(shop)
                        break
                #TODO matar processo e apagar pasta
            elif self.shopify_api_key == '':
                self.temp_bot.shopify_api_key = text
                text = 'Great! Now send me your Shopify API password'
            elif self.temp_bot.shopify_api_password == '':
                self.shopify_api_password = text
                text = 'Great! Now send me your Shopify hostname'
            elif self.temp_bot.shopify_hostname == '':
                self.shopify_hostname = text
                text = 'Great! Now send me your Telegram bot key'
            elif self.telegram_api_key == '':
                self.temp_bot.telegram_api_key = text
                text = 'Done! Let me create your bot for you, give me a minute...'
                success = run_generic_store.create_new_store(bot_name=self.telegram_api_key.split(':')[0],
                                                             shopify_api_key=self.shopify_api_key,
                                                             shopify_api_password=self.shopify_api_password,
                                                             shopify_hostname=self.shopify_hostname,
                                                             telegram_api_key=self.telegram_api_key)
                if success:
                    self.list_shops.append(copy.copy(self.temp_bot))
                    self.shop_names.append(self.temp_bot.shopify_hostname)
                    self.temp_bot = Shop()
                    text = "Hoorray! You're new telegram store is online and running!"
                else:
                    text = "Ops, something went wrong. Please try again :("

            if text is not None:
                bot.sendMessage(chat_id=chat_id, text=text)

    def get_shops_keyboard(self):
        keyboard = []

        for shop in self.list_shops:
            keyboard.append([KeyboardButton(text=shop.shopify_hostname)])

        return ReplyKeyboardMarkup(inline_keyboard=keyboard)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, CreateShopBot, timeout=sys.maxint),
])

bot.message_loop()

print 'Listening...'
while True:
    time.sleep(10)
