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
        self.pid = None


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
            text_in = msg['text']
            text = ''
            if text_in == '/new_shop' or text_in == '/start':   #user may be restarting flow
                self.temp_bot = Shop()
                text = 'Great! Please send me your Shopify API key'
            elif text_in == '/delete':
                if len(self.list_shops) == 0:
                    text = "Ops, you don't have any shops! Try creating one with /new_shop"
                else:
                    bot.sendMessage(chat_id=chat_id,
                                    text='Which shop would you like to delete?',
                                    reply_markup=self.get_shops_keyboard())
            elif text_in in self.shop_names:
                self.shop_names.remove(text_in)
                for shop in self.list_shops:
                    if shop.shopify_hostname == text_in:
                        self.list_shops.remove(shop)
                        run_generic_store.kill_store(shop.telegram_api_key)
                        break
            elif self.temp_bot.shopify_api_key == '':
                self.temp_bot.shopify_api_key = text_in
                text = 'Great! Now send me your Shopify API password'
            elif self.temp_bot.shopify_api_password == '':
                self.temp_bot.shopify_api_password = text_in
                text = 'Great! Now send me your Shopify hostname'
            elif self.temp_bot.shopify_hostname == '':
                self.temp_bot.shopify_hostname = text_in
                text = 'Great! Now send me your Telegram bot key'
            elif self.temp_bot.telegram_api_key == '':
                self.temp_bot.telegram_api_key = text_in
                bot.sendMessage(chat_id=chat_id, text='Done! Let me create your bot for you, give me a minute...')
                result = run_generic_store.create_new_store(bot_name=self.temp_bot.telegram_api_key.split(':')[0],
                                                            shopify_api_key=self.temp_bot.shopify_api_key,
                                                            shopify_api_password=self.temp_bot.shopify_api_password,
                                                            shopify_hostname=self.temp_bot.shopify_hostname,
                                                            telegram_api_key=self.temp_bot.telegram_api_key)
                if result:
                    self.list_shops.append(copy.copy(self.temp_bot))
                    self.shop_names.append(self.temp_bot.shopify_hostname)
                    self.temp_bot = Shop()
                    text = "Hoorray! You're new telegram store is online and running!"
                else:
                    text = "Ops, something went wrong. Please try again :("

            if text != '':
                bot.sendMessage(chat_id=chat_id, text=text)

    def get_shops_keyboard(self):
        keyboard = []

        for shop in self.list_shops:
            keyboard.append([KeyboardButton(text=shop.shopify_hostname)])

        return ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, CreateShopBot, timeout=sys.maxint),
])

bot.message_loop()

print 'Listening...'
while True:
    time.sleep(10)
