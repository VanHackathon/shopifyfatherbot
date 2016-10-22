import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
import time
import sys


class CreateShopBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.shopify_api_key = ''
        self.shopify_api_password = ''
        self.shopify_hostname = ''
        self.telegram_api_key = ''

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        print msg
        if chat_type == 'private' and content_type == 'text':
            text = msg['text']
            if text == '/create' or text == '/start':   #user may be restarting flow
                self.clear_attributes()
                text = 'Great! Please send me your Shopify API key'
            elif self.shopify_api_key == '':
                self.shopify_api_key = text
                text = 'Great! Now send me your Shopify API password'
            elif self.shopify_api_password == '':
                self.shopify_api_password = text
                text='Great! Now send me your Shopify hostname'
            elif self.shopify_hostname == '':
                self.shopify_hostname = text
                text='Great! Now send me your Telegram bot key'
            elif self.telegram_api_key == '':
                self.telegram_api_key = text
                text='Done! Let me create your bot for you, give me a minute...'

            if msg != None and msg != '':
                bot.sendMessage(chat_id=chat_id, text=text)

    def clear_attributes(self):
        self.shopify_api_key = ''
        self.shopify_api_password = ''
        self.shopify_hostname = ''
        self.telegram_api_key = ''


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, CreateShopBot, timeout=sys.maxint),
])

bot.message_loop()

print 'Listening...'
while True:
    time.sleep(10)
