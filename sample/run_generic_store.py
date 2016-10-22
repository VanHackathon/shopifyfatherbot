from fabric.api import local
import os


def create_new_store(bot_name, shopify_api_key, shopify_api_password, shopify_hostname, telegram_api_key):
    try:
        local('git clone https://github.com/VanHackathon/botStoreGenesis.git /home/ubuntu/%s' % bot_name)
        local('python %s/samples/botStoreGenesis.py %s %s %s %s &' % (bot_name, shopify_api_key,
                                                                      shopify_api_password, shopify_hostname,
                                                                      telegram_api_key))
        return True
    except:
        return False


def exist_bot(bot_name):
    return os.path.exists('/home/ubuntu/%s' % bot_name)
