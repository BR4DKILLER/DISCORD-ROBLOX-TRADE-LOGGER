
# SCRIPT INFO

Version = 1
GithubVersion = 1

# MODULES

import subprocess
import time

import sys
import os

from PIL import Image, ImageDraw, ImageFont

try:
    from __settings__ import *
    import requests
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    os.system('cls')

try:
    from __settings__ import *
    import requests
except:
    print('There was an error loading the required modules, possible causes below:')
    print('1. Missing a opensource module, downloaded directly from the repository')
    print('2. Pip failed to find/install the required module')
    print('3. Your version of python does not support the module required')
    print(' ')
    print('You can now close the program, press any key to exit.')
    os.system('pause')
    sys.exit()

# VERSION AUTHENTICATION

try:
    GithubVersion = requests.get('https://raw.githubusercontent.com/BR4DKILLER/DISCORD-ROBLOX-TRADE-LOGGER/main/Version.txt')
    if GithubVersion.status_code != 200:
        raise('Version Response Returned {code}'.format(code=str(GithubVersion.status_code)))
    else:
        if GithubVersion > Version:
            print('Your version is out of date, features may be unstable or buggy.')
            print('Download the new version here: https://github.com/BR4DKILLER/DISCORD-ROBLOX-TRADE-LOGGER')
            print('You may also press any button to continue with your current version.')
            os.system('pause')
            pass
except Exception as DebugError:
    print('Error Getting Current Version: {d}'.format(d=str(DebugError)))
    print('Program was paused so that you can read this, press any key to continue the program.')
    print('WARNING: The program may be unstable or buggy if outdated, please ensure your version is up to date.')
    os.system('pause')
    pass

# SETTINGS

Settings_File = '__data__.json'
Settings = {'roblox_cookie': '', 'delay': 10, 'inboundwebhook': '', 'outboundwebhook': ''}

# VARIABLES

item_data = {}
CheckedTrades = {}

# FUNCTIONS

def ValidCookie(Cookie):
    data = requests.get('https://users.roblox.com/v1/users/authenticated', headers = {'cookie': '.ROBLOSECURITY=' + str(Cookie)}).json()
    try:
        error = data['errors']
        return False, 'Invalid'
    except:
        return True, 'Valid'

def ValidHook(Webhook):
    try:
        data = requests.get(Webhook)
    except:
        return False, 'Invalid'
    try:
        data = data.json()['token']
        return True, 'Valid'
    except:
        return False, 'Invalid'

def UpdateRolimonsValues():
    global item_data
    Response = requests.get('https://api.rolimons.com/items/v1/itemdetails')
    try:
        Response_JSON = Response.json()
        if Response.status_code != 200:
            return False, 'Update Value Response Returned {code}'.format(code=Response.status_code)
        else:
            if Response_JSON['success'] == True:
                item_data = Response_JSON['items']
                return True, 'Success, Updated!'
            return False, 'Something weird happened... This should not error!'
    except Exception as err:
        return False, 'Update Value Function Returned An Error: {error}'.format(error=str(err))

def CreateEmbed(Data):
    Example = {
        "content": None,
        "embeds": [
            {
            "title": "Sent by {username} (@{display_name})",
            "description": "[Roblox Trades Hyperlink](https://www.roblox.com/trades)",
            "url": "{profile_url}",
            "color": Data['color'],
            "fields": [
                {
                "name": "You:",
                "value": "{items_give}"
                },
                {
                "name": "Them:",
                "value": "{items_recieve}"
                },
                {
                "name": "Profit Margin:",
                "value": "{profit}"
                },
                {
                "name": "Biggest Item:",
                "value": "{biggest}"
                }
            ],
            "author": {
                "name": "Trade Inbound - (ID: {id})"
            },
            "image": {
                "url": "{image}"
            }
            }
        ],
        "attachments": []
    }

    try:
        Example['embeds'][0]['title'] = Example['embeds'][0]['title'].format(username = Data['Username'], display_name = Data['DisplayName'])
        Example['embeds'][0]['url'] = Example['embeds'][0]['url'].format(profile_url = Data['ProfileURL'])

        Example['embeds'][0]['image']['url'] = Example['embeds'][0]['image']['url'].format(image = Data['BiggestUrl'])
        Example['embeds'][0]['author']['name'] = Example['embeds'][0]['author']['name'].format(id = Data['TradeID'])

        Example['embeds'][0]['fields'][0]['value'] = Example['embeds'][0]['fields'][0]['value'].format(items_give = Data['formatted_give'])
        Example['embeds'][0]['fields'][1]['value'] = Example['embeds'][0]['fields'][1]['value'].format(items_recieve = Data['formatted_recieve'])
        Example['embeds'][0]['fields'][2]['value'] = Example['embeds'][0]['fields'][2]['value'].format(profit = Data['Profit'])
        Example['embeds'][0]['fields'][3]['value'] = Example['embeds'][0]['fields'][3]['value'].format(biggest = Data['Biggest'])
    except Exception as DebugError:
        return False, 'Error while formatting embed JSON: {d}'.format(d=str(DebugError))

    return True, Example

def FormatItems(Items, Robux):
    ItemList = []
    ItemData = {"name": "", "value": 0, "id": 0, "totalvalue": 0}
    for Item in Items:
        asset_id = str(Item['assetId'])
        item_value = 0
        if item_data[asset_id][3] <= 0:
            item_value = item_data[asset_id][2]
        else:
            item_value = item_data[asset_id][3]
        
        ItemData['totalvalue'] += item_value
        if item_value > ItemData['value']:
            ItemData['value'] = item_value
            ItemData['name'] = Item['name']
            ItemData['id'] = Item['assetId']

        ItemList.append('{name} ({value})'.format(name = Item['name'], value = '{:,}'.format(item_value)))
    
    if Robux != 0:
        ItemList.append('{amount} Robux'.format(amount=str(Robux)))

    try:
        String = '**' + str('\n'.join(ItemList)) + '**'
        return True, String, ItemData
    except Exception as DebugError:
        return False, 'Error while formatting items & robux: {d}'.format(d=str(DebugError)), ItemData
    

def GetInboundTrades():
    Response = requests.get('https://trades.roblox.com/v1/trades/inbound?limit=100',cookies = {".ROBLOSECURITY": Settings['roblox_cookie']})
    Inbound = []
    try:
        Response_JSON = Response.json()
        if Response.status_code != 200:
            return False, 'Inbound Trade Response Returned {code}'.format(code=Response.status_code)
        else:
            Trade_Data = Response_JSON['data']
            for Trade in Trade_Data:
                TradeID = Trade['id']
                User = Trade['user']

                Inbound.append({
                  "Username": User['name'],
                  "DisplayName": User['displayName'],
                  "ProfileURL": "https://wwww.roblox.com/users/{user_id}/profile".format(user_id=User['id']),
                  "TradeID": TradeID
                })
            return True, Inbound
    except Exception as DebugError:
        return False, 'Error while retrieving inbound trade JSON: {d}'.format(d=str(DebugError))

def GetOutboundTrades():
    Response = requests.get('https://trades.roblox.com/v1/trades/outbound?limit=100',cookies = {".ROBLOSECURITY": Settings['roblox_cookie']})
    Outbound = []
    try:
        Response_JSON = Response.json()
        if Response.status_code != 200:
            return False, 'Outbound Trade Response Returned {code}'.format(code=Response.status_code)
        else:
            Trade_Data = Response_JSON['data']
            for Trade in Trade_Data:
                TradeID = Trade['id']
                User = Trade['user']

                Outbound.append({
                  "Username": User['name'],
                  "DisplayName": User['displayName'],
                  "ProfileURL": "https://wwww.roblox.com/users/{user_id}/profile".format(user_id=User['id']),
                  "TradeID": TradeID
                })
            return True, Outbound
    except Exception as DebugError:
        return False, 'Error while retrieving outbound trade JSON: {d}'.format(d=str(DebugError))

def GetTradeData(Data):
    Trade_URL = 'https://trades.roblox.com/v1/trades/{id}'.format(id=Data['TradeID']) 
    Response = requests.get(Trade_URL, cookies ={".ROBLOSECURITY": Settings['roblox_cookie']})
    try:
        Response_JSON = Response.json()
        if Response.status_code != 200:
            return False, 'Trade Info Response Returned {code}'.format(code=Response.status_code)
        else:
            Success, GiveFormat, GiveData = FormatItems(Response_JSON['offers'][0]['userAssets'], Response_JSON['offers'][0]['robux'])
            if not Success:
                return False, GiveFormat

            Success, RecieveFormat, RecieveData = FormatItems(Response_JSON['offers'][1]['userAssets'], Response_JSON['offers'][1]['robux'])
            if not Success:
                return False, RecieveFormat

            if GiveData['value'] > RecieveData['value']:
                Data['Biggest'] = GiveData['name'] + ' **(YOU)**'
                ThumbnailAPI = 'https://thumbnails.roblox.com/v1/assets?assetIds={id}'.format(id=GiveData['id'])
            else:
                Data['Biggest'] = RecieveData['name'] + ' **(THEM)**'
                ThumbnailAPI = 'https://thumbnails.roblox.com/v1/assets?assetIds={id}'.format(id=RecieveData['id'])

            try:
                API_Params = '&returnPolicy=PlaceHolder&size=150x150&format=Png&isCircular=false'
                Thumbnail = requests.get(ThumbnailAPI + API_Params).json()['data'][0]['imageUrl']
                Data['BiggestUrl'] = Thumbnail
            except:
                Data['BiggestUrl'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Placeholder_view_vector.svg/991px-Placeholder_view_vector.svg.png'

            TotalProfit = RecieveData['totalvalue'] - GiveData['totalvalue']

            if TotalProfit > 0:
                Data['color'] = 2752256 # Good
            else:
                Data['color'] = 16711680 # Bad

            Data['Profit'] = '{:,}'.format(TotalProfit)
            Data['formatted_give'] = GiveFormat
            Data['formatted_recieve'] = RecieveFormat

            return True, Data
    except Exception as DebugError:
        return False, 'Error while retrieving Trade Data JSON: {d}'.format(d=str(DebugError))
    pass

def Main():
    Success, Response = UpdateRolimonsValues()
    if not Success:
        print('Failed to update Rolimons values, some may be inaccurate until next loop iteration.')
    
    WriteSettings('__trades__.json', CheckedTrades)

    Success, InboundTrades = GetInboundTrades()
    if not Success:
        return False, 'Error while retrieving inbound trades from function: {d}'.format(d=InboundTrades)
    else:
        for Trade in InboundTrades:
            try:
                ID = str(Trade['TradeID'])
                Checked = CheckedTrades[ID]
                if Checked:
                    print('{id} Was already checked, skipping...'.format(id=Trade['TradeID']))
                    continue
            except:
                CheckedTrades[ID] = True
                pass
                            
            Success, TradeData = GetTradeData(Trade)
            if Success:
                Success, Embed = CreateEmbed(TradeData)
                if not Success:
                    print('Error while curating the embed data for webhook: {error}'.format(error=Embed))
                else:
                    requests.post(Settings['inboundwebhook'],headers={"Content-Type":"Application/JSON"},json=Embed)
            else:
                print('Error while getting Trade Data for Trade {id}: {error}'.format(id=Trade['TradeID'],error=TradeData))

    

# AUTHENTICATION VALIDATION

if not DoesFileExist('__trades__.json'):
    WriteSettings('__trades__.json', CheckedTrades)
else:
    Success, Return = ReturnSettings('__trades__.json')
    if not Success:
        print('Something went wrong loading')
    else:
        print('Success, loaded checked trades dictionary!')
        CheckedTrades = Return

if not DoesFileExist(Settings_File):
    cookie = input('Please enter your roblox cookie, this is required: ')
    while True:
        Success, Message = ValidCookie(cookie)
        if Success == False:
            print('cookie invalid')
            cookie = input('Please enter your roblox cookie, this is required: ')
        else:
            break
    Settings['roblox_cookie'] = cookie

    delay = input('Please enter your desired delay in seconds (5-60): ')
    while True:
        try:
            i = int(delay)
            if (i > 60 or 5 > i):
                delay = input('Please enter your desired delay in seconds (5-60): ')
            else:
                delay = int(i)
                break
        except:
            delay = input('Please enter your desired delay in seconds (5-60): ')
    Settings['delay'] = delay

    iwebhook = input('Please enter your inbound webhook: ')
    while True:
        Success, Message = ValidHook(iwebhook)
        if Success == False:
            print('inbound webhook invalid')
            iwebhook = input('Please enter your inbound webhook: ')
        else:
            break
    Settings['inboundwebhook'] = iwebhook

    owebhook = input('Please enter your outbound webhook: ')
    while True:
        Success, Message = ValidHook(owebhook)
        if Success == False:
            print('outbound webhook invalid')
            iwebhook = input('Please enter your outbound webhook: ')
        else:
            break
    Settings['outboundwebhook'] = owebhook

    WriteSettings(Settings_File, Settings)
else:
    Success, Return = ReturnSettings(Settings_File)
    if not Success:
        print('Something went wrong getting your settings, please enter new settings.')
        cookie = input('Please enter your roblox cookie, this is required: ')
        while True:
            Success, Message = ValidCookie(cookie)
            if Success == False:
                print('cookie invalid')
                cookie = input('Please enter your roblox cookie, this is required: ')
            else:
                break
        Settings['roblox_cookie'] = cookie

        delay = input('Please enter your desired delay in seconds (5-60): ')
        while True:
            try:
                i = int(delay)
                if (i > 60 or 5 > i):
                    delay = input('Please enter your desired delay in seconds (5-60): ')
                else:
                    delay = int(i)
                    break
            except:
                delay = input('Please enter your desired delay in seconds (5-60): ')
        Settings['delay'] = delay

        iwebhook = input('Please enter your inbound webhook: ')
        while True:
            Success, Message = ValidHook(iwebhook)
            if Success == False:
                print('inbound webhook invalid')
                iwebhook = input('Please enter your inbound webhook: ')
            else:
                break
        Settings['inboundwebhook'] = iwebhook

        owebhook = input('Please enter your outbound webhook: ')
        while True:
            Success, Message = ValidHook(owebhook)
            if Success == False:
                print('outbound webhook invalid')
                iwebhook = input('Please enter your outbound webhook: ')
            else:
                break
        Settings['outboundwebhook'] = owebhook

        WriteSettings(Settings_File, Settings)
    else:
        Settings = Return

Valid, Message = ValidCookie(Settings['roblox_cookie'])

if not Valid:
    print('Your saved cookie is invalid, please input a new cookie')
    cookie = input('Please enter your roblox cookie, this is required: ')
    while True:
        Success, Message = ValidCookie(cookie)
        if Success == False:
            print('cookie invalid')
            cookie = input('Please enter your roblox cookie, this is required: ')
        else:
            break    
    Settings['roblox_cookie'] = cookie
    WriteSettings(Settings_File, Settings)
    os.system('cls')

Valid, Message = ValidHook(Settings['inboundwebhook'])

if not Valid:
    print('Your saved inbound webhook is invalid, please input a new webhook')
    iwebhook = input('Please enter your inbound webhook: ')
    while True:
        Success, Message = ValidHook(iwebhook)
        if Success == False:
            print('inbound webhook invalid')
            iwebhook = input('Please enter your inbound webhook: ')
        else:
            break
    Settings['inboundwebhook'] = iwebhook    
    WriteSettings(Settings_File, Settings)
    os.system('cls')

Valid, Message = ValidHook(Settings['outboundwebhook'])

if not Valid:
    print('Your saved inbound webhook is invalid, please input a new webhook')
    owebhook = input('Please enter your outbound webhook: ')
    while True:
        Success, Message = ValidHook(owebhook)
        if Success == False:
            print('outbound webhook invalid')
            owebhook = input('Please enter your outbound webhook: ')
        else:
            break
    Settings['outboundwebhook'] = owebhook    
    WriteSettings(Settings_File, Settings)
    os.system('cls')

if __name__ == '__main__':
    while True:
        os.system('cls')
        print(r'''
          _______  _____             _____   ______   _       ____    _____   _____  ______  _____  
         |__   __||  __ \     /\    |  __ \ |  ____| | |     / __ \  / ____| / ____||  ____||  __ \ 
            | |   | |__) |   /  \   | |  | || |__    | |    | |  | || |  __ | |  __ | |__   | |__) |
            | |   |  _  /   / /\ \  | |  | ||  __|   | |    | |  | || | |_ || | |_ ||  __|  |  _  / 
            | |   | | \ \  / ____ \ | |__| || |____  | |____| |__| || |__| || |__| || |____ | | \ \ 
            |_|   |_|  \_\/_/    \_\|_____/ |______| |______|\____/  \_____| \_____||______||_|  \_\

            Running every {delay} seconds, logging your trades!
            Created by BR4DKILLER on ROBLOX! (https://www.roblox.com/users/3657107776/profile)
            Version: {version}                                                                                
        '''.format(delay=str(Settings['delay'])))
        try:
            Main()
        except Exception as CriticalError:
            print('There was a Critical Error during the execution of the MAIN Function!')
            print('Error:', str(CriticalError))
        except KeyboardInterrupt as Interrupt:
            print('Closing the program, thanks for using! Press any key to close.')
            os.system('pause')
            sys.exit()
        
        try:
            time.sleep(Settings['delay'])
        except KeyboardInterrupt as Interrupt:
            print('Closing the program, thanks for using! Press any key to close.')
            os.system('pause')
            sys.exit()
