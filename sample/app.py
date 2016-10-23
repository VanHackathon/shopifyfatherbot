import copy
from os import path
import run_generic_store
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide
import time
import shopify
import sys
import re


class Shop(object):
    def __init__(self):
        self.shopify_api_key = ''
        self.shopify_api_password = ''
        self.shopify_hostname = ''
        self.telegram_api_key = ''
        self.state = States.IDLE


class States:
    IDLE, WAITING_SHOP_API, WAITING_SHOP_PASS, WAITING_HOSTNAME, WAITING_TELEGRAM_API, DELETING = xrange(6)


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
            if text_in == '/cancel':
                text = 'Action canceled'
                self.temp_bot = Shop()
            elif text_in == '/remove':
                self.temp_bot = Shop()
                if len(self.list_shops) == 0:
                    text = "Ops, you don't have any shops! Try creating one with /new_shop"
                else:
                    self.temp_bot = Shop()
                    self.temp_bot.state = States.DELETING
                    bot.sendMessage(chat_id=chat_id,
                                    text='Which shop would you like to remove?',
                                    reply_markup=self.get_shops_keyboard())
            elif text_in == '/new_shop' or text_in == '/start':
                self.temp_bot = Shop()
                self.temp_bot.state = States.WAITING_SHOP_API
                text = "Let's build a new Shopify bot shop! Yay!\n" \
                       "Please send me your Shopify API key"
            elif text_in == '/help':
                self.temp_bot = Shop()
                text = "Greetings! I'm Shopify Father Bot, I take care of your Shopify telegram Shop.\n\n" \
                       "How does it work? Just type /new_shop and follow the instructions.\n" \
                       "What exactly do I do you may ask? Well, I take already existing stores from Shopify and " \
                       "create chatbot stores with zero effort! That means you'll have a Telegram Shopify shop in " \
                       "less than one minute!\n\n" \
                       "Try it out!\n\n" \
                       "I was made for the 2nd VanHackathon by @xitz0r @brucostam and @PabloMontenegro"
            elif text_in[0] == '/':
                self.temp_bot.state = Shop()
                text = "Sorry, I don't know that command :(\n" \
                       "Please check /help"
            elif self.temp_bot.state == States.WAITING_SHOP_API:
                self.temp_bot.shopify_api_key = text_in
                self.temp_bot.state = States.WAITING_SHOP_PASS
                text = 'Good, now please send me your Shopify API password'
            elif self.temp_bot.state == States.WAITING_SHOP_PASS:
                self.temp_bot.shopify_api_password = text_in
                self.temp_bot.state = States.WAITING_HOSTNAME
                text = 'Ok, now send me your Shopify hostname'
            elif self.temp_bot.state == States.WAITING_HOSTNAME:
                shop_url = 'https://%s:%s@%s.myshopify.com/admin' %\
                           (self.temp_bot.telegram_api_key, self.temp_bot.shopify_api_password, text_in)

#               checking if api key, api password and hostname are valid
                shopify.ShopifyResource.set_site(shop_url)
                try:
                    shopify.Shop.current()
                    self.temp_bot.shopify_hostname = text_in
                    self.temp_bot.state = States.WAITING_TELEGRAM_API
                    text = 'Lastly, send me your Telegram bot token or simply forward me the @BotFather token message'
                except:
                    text = 'Ops! Something went wrong. Please check your Shopify API key, API password,' \
                           'hostname and try again!'
                    self.temp_bot = Shop()  #cleaning up
            elif self.temp_bot.state == States.WAITING_TELEGRAM_API:
                temp = re.search(r'[0-9]{1,}:\w*', text_in) # look for a telegram API pattern TODO use this pattern to validate api key
                if temp:
                    text_in = text_in[temp.start(): temp.end()]

#                   checking if bot is already running
                    if path.isdir(text_in.split(':')[0]):
                        self.temp_bot = Shop()
                        text = "Ops! It looks like that bot is already in use. Please remove it before adding it again"
                    else:
                        try:
#                           checking if bot works
                            bot_checking = telepot.Bot(text_in)
                            new_bot = bot_checking.getMe()

                            self.temp_bot.telegram_api_key = text_in

                            bot.sendMessage(chat_id=chat_id,
                                            text='Ok, now let me do some magic and your Shopify store bot,\
                                            give me a second...',
                                            reply_markup=ReplyKeyboardHide())
                            result = run_generic_store.create_new_store(
                                bot_name=self.temp_bot.telegram_api_key.split(':')[0],
                                shopify_api_key=self.temp_bot.shopify_api_key,
                                shopify_api_password=self.temp_bot.shopify_api_password,
                                shopify_hostname=self.temp_bot.shopify_hostname,
                                telegram_api_key=self.temp_bot.telegram_api_key)
                            if result:
                                self.list_shops.append(copy.copy(self.temp_bot))
                                self.shop_names.append(self.temp_bot.shopify_hostname)
                                text = "Hoorray! You're new telegram store is online and running!" \
                                       "Check it at @%s" % new_bot['username']
                            else:
                                text = "Ops, something went wrong. Please try again :("
                        except:
                            text = "Ops! That doesn't look like a valid telegram token :("
                else:
                    text = "Ops! That doesn't look like a valid telegram token :("

                self.temp_bot = Shop()
            elif self.temp_bot.state == States.DELETING:
                if text_in in self.shop_names:
                    self.shop_names.remove(text_in)
                    for shop in self.list_shops:
                        if shop.shopify_hostname == text_in:
                            self.list_shops.remove(shop)
                            run_generic_store.kill_store(shop.telegram_api_key)
                            text = '%s successfully removed' & text_in
                            break
                else:
                    text = "Sorry, but that shop does't exist!"

                self.temp_bot = Shop()
            else:
                text = "Sorry, I did't understand :(\nPlease check /help"

            if text != '':
                bot.sendMessage(chat_id=chat_id, text=text, reply_markup=ReplyKeyboardHide())

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
