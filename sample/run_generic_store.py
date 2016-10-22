from fabric.api import local


def create_new_store(bot_name, shopify_api_key, shopify_api_password, shopify_hostname, telegram_api_key):
    try:
        local('git clone https://github.com/VanHackathon/botStoreGenesis.git %s' % bot_name)
        pid = local('python %s/samples/botStoreGenesis.py %s %s %s %s &' % (bot_name, shopify_api_key,
                                                                            shopify_api_password, shopify_hostname,
                                                                            telegram_api_key),
                    capture=True)
        return pid
    except:
        return False


def kill_store(pid, folder_name):
    local('kill %s' % pid)
    local('rm -rf %s' % folder_name)
