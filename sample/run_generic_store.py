from fabric.api import local


def create_new_store(bot_name, shopify_api_key, shopify_api_password, shopify_hostname, telegram_api_key):
    try:

        local('git clone https://github.com/VanHackathon/botStoreGenesis.git %s' % bot_name)
        local('python %s/samples/botStoreGenesis.py %s %s %s %s &' % (bot_name, shopify_api_key,
                                                                      shopify_api_password, shopify_hostname,
                                                                      telegram_api_key))
        return True
    except:
        return False


def kill_store(telegram_api_key):
    local('kill $(ps aux | grep [p]ython | grep %s)' % telegram_api_key)
    local('rm -rf %s' % telegram_api_key.split(':')[0])
