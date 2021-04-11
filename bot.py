import discord
import os
import time
import requests
from dotenv import load_dotenv
from lxml import html
import pickle
import json
coingecko_base_url = 'https://api.coingecko.com/api/v3'
client = discord.Client()
load_dotenv()

flexible_plans={'bitcoin':1.2/100, 'tether':6/100, 'cardano':1.45/100, 'dogecoin':5/100, 'ethereum':0.88/100, 'chainlink':0.39/100, 'monero':1.83/100}

E1 = "Sorry, the token ID you entered is incorrect, you can get it by reading the coingecko URL of your desired coin. To do so, visit coingecko.com and select your desired coin. Example: https://www.coingecko.com/de/munze/bitcoin ( token ID: 'bitcoin' )"
cs_balance_xpath = '//*[@id="__next"]/main/div/div/div[1]/div[3]/span/text()'
def cut(string):
    res = ''
    loc = 1000000
    for l in range(0, len(string) - 1):
        if string[l] != '.' and string[l] != ',' and l != loc + 1:
            res += string[l]
        elif l == loc + 1:
            return res
        else:
            loc = l
    return res

def cutx(string, x):
    res = ''
    loc = 1000000
    for l in range(0, len(string) - 1):
        if string[l] != '.' and string[l] != ',' and l != loc + x:
            res += string[l]
        elif l == loc + x:
            return res
        else:
            res += string[l]
            loc = l
    return res

def get_data():
    with open('database.dat', 'rb') as database:
        data = pickle.load(database)
        return data

def gecko_ids():
    r = requests.get('https://api.coingecko.com/api/v3/coins/list')
    res = json.loads(r.text)
    valid = []
    for e in range(0, len(res) - 1):
        if '0-5x' not in res[e]['id'] and 'long' not in res[e]['id'] and 'short' not in res[e]['id']:
            valid.append(len(valid))
            valid[len(valid) - 1] = res[e]['id']
    return valid

def reset(user_id):
    data = {}
    data_backup = get_data()
    data['id'] = user_id
    data['balance'] = {}
    data['prints'] = 0
    symbols = gecko_ids()
    for i in range(0, len(symbols)):
        data['balance'][symbols[i]] = 0
    for d in range(0, len(data_backup)):
        if data_backup[d]['id'] == user_id:
            data_backup[d] = data
    with open('database.dat', 'wb') as database:
        pickle.dump(data_backup, database)
        database.close()

def set_key(user_id, key, value):
    data = get_data()
    for d in range(0, len(data)):
        if data[d]['id'] == user_id:
            data[d][key] = value
    with open('database.dat', 'wb') as database:
        pickle.dump(data, database)

def sign_up(user_id):
    data = get_data() #Genesis comment out
    if str(user_id) in str(data):
        return
    with open('database.dat', 'rb') as database: #Genesis comment out
        data = pickle.load(database) #Genesis comment out
    #data = [] #Genesis uncomment
    data.append(len(data))
    data[len(data) - 1] = {}
    data[len(data) - 1]['id'] = user_id
    data[len(data) - 1]['balance'] = {}
    data[len(data) - 1]['prints'] = 0
    symbols = gecko_ids()
    for i in range(0, len(symbols)):
        data[len(data) - 1]['balance'][symbols[i]] = 0
    with open('database.dat', 'wb') as database:
        pickle.dump(data, database)
        database.close()

def get_printed(user_id):
    data = get_data()
    for d in range(0, len(data)):
        if data[d]['id'] == user_id:
            return data[d]['prints']

def get_price(token_id):
    r = requests.get(coingecko_base_url + '/simple/price/?ids=' + token_id + '&vs_currencies=usd')
    res_json = json.loads(r.text)
    result = res_json[token_id]['usd']
    return result

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print(str(message.author.id))
    admin_id = '686188505038061588'
    print(message.channel.id)
    channel_ids = ['830115500058214461']
    if str(message.channel.id) not in channel_ids:
        return
    print(client.users)
    if message.author == client.user:
        return

    data = get_data() #Genesis comment out
    if message.content.startswith('$register'):
        sign_up(message.author.id)

    elif str(message.author.id) not in str(data):
        await message.channel.send('Please use $register first.')

    elif message.content.startswith('$help'):
        await message.channel.send('[BASIC]' + '\n' + '1. $register | to join this bot, required to execute any commands.' + '\n' + '2. $print AMOUNT | add a specific AMOUNT of USDT (tether) to your balance, you can print negative values, but can not have less than 0 USDT. The %age gains take your printing in consideration so print as much as you want, it wont affect your performance and stats :).' + '\n' + '3. $price TOKEN | get price of a TOKEN.' + '\n' + '4. $balance TOKEN | get balance of a specific TOKEN.' + '\n' + '5. $hodling | get all balances that are not 0 (your entire portfolio).' + '\n' + '6. $buy TOKEN AMOUNT | buy a specific TOKEN for a specifict AMOUNT of USDT (tether), check your tether balance using the command "$balance tether."'+ '\n' + '7. $sell TOKEN AMOUNT, sell a specific AMOUNT of a specific TOKEN at the current market price of the given token (you will receive USDT / tether). You can sell your entire hodling by simply using $sell TOKEN all' + '\n' + '8. $reset | resets all balances and stats to 0, allowing for a fresh start.' + '\n' + '9. $supported TOKEN | check weather a token is supported by the coingecko API V3 yet, if the TOKEN is unsupported, you sadly can not buy / sell it throught this bot.' + '\n' + '10. $market TOKEN | get advanced market data of a token, including 24hour change, all time high, alltime low and many more.' + '\n' + '[STAKING(FLEXIBLE)]' + '\n' + '1. $sterms | shows all flexible staking terms available.' + '\n' + '2. $slock TOKEN AMOUNT | deposit an AMOUNT of a TOKEN to the flexible staking term and start earning interest immediately. Interest is calculated every second. You can $sunlock whenever you want to.' + '\n' + '3. $sunlock TOKEN AMOUNT | withdraw an AMOUNT of a TOKEN from the flexible staking term. You can $sunlock TOKEN all, to unlock 100% of your allocation.' + '\n' + '4. $sterms | list all available flexible staking terms and their interest rates. If you lock a TOKEN into staking that has no plan, you earn 0% interest.' + '\n')

        await message.channel.send('[ADVANCED]' + '\n' + '1. $connect COINSTATS_URL | allows you to connect your actual coinstats.app account (by setting up a direct link to your coinstats.app portfolio).' + '\n' + '2. $csbalance | returns the current balance of your linked coinstats.app portfolio (direct link), only works in case you have properly set up your portfolio using the $connect command.' + '\n' + '[ADMIN ONLY]' + '\n' + '1. $update KEY VALUE | adds a new key to the database and sets VALUE as default value for all users in the database. This command is admin-only, because the risk of loosing data is very high.' + '\n' + '2. $upgrade | automatically search for new tokens on coingecko and add them to the bot.')

    elif message.content.startswith('$hodling') or message.content.startswith('$holding'):
        total_balance = 0.0
        hodlstr = '-' * 100 + '\n' + 'DEMO PORTFOLIO OF ' + str(message.author) + '\n' + '-' * 100 + '\n'
        try:
            data = get_data()
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    for key in data[d]['balance']:
                        if data[d]['balance'][key] > 0:
                            try:
                                price = get_price(key)
                            except Exception as Unlisted:
                                price = 0
                            hodlstr += key + ': ' + str(data[d]['balance'][key]) + ' | (' + cut(str(data[d]['balance'][key] * price)) + '$)' + '\n' + ' ' + '\n'
                            total_balance += data[d]['balance'][key] * price
            printed = get_printed(message.author.id)
            try:
                staking_balance = 0
                with open('staking.dat', 'rb') as stakingbase:
                    stakingdata = pickle.load(stakingbase)

                for s in range(0, len(stakingdata)):
                    if stakingdata[s]['id'] == message.author.id:
                        for key in stakingdata[s]['balance']:
                            if stakingdata[s]['balance'][key][0] != 0:
                                price = get_price(key)
                                staking_balance += stakingdata[s]['balance'][key][0] * price
                                if key in flexible_plans:
                                    interest = stakingdata[s]['balance'][key][0] * (flexible_plans[key]/365/24/60/60 * (time.time()-stakingdata[s]['balance'][key][1]))
                                staking_balance += interest * price
            except Exception as E:
                print(str(E))
                staking_balance = 0.00
            total_balance += staking_balance
            profit = total_balance - printed
            percentage_change = 100 * (total_balance - printed) / printed
            hodlstr += 'TOTAL (USDT): ' + cut(str(total_balance)) + '$' + '\n' + 'STAKING (USDT): ' + cut(str(staking_balance)) + '$' + '\n'
            hodlstr += 'You printed: ' + str(printed) + ' USDT' + '\n' + 'PNL: ' + cutx(str(profit), 3) + '$' + '\n' + 'Percentage gains: ' + cutx(str(percentage_change), 3) + '%'
            hodlstr += '\n' + '-' * 100 + '\n'
            await message.channel.send(hodlstr)
        except Exception as E:
            await message.channel.send('Unknown Error, this feature might be under maintanance. Or you just used $reset and your #Hodlings are 0.')

    elif message.content.startswith('$print '):
        amount = float(message.content[7:])
        data = get_data()
        for d in range(0, len(data)):
            if data[d]['id'] == message.author.id:
                data[d]['prints'] = data[d]['prints'] + amount
                old_usdt = data[d]['balance']['tether']
                new_usdt = old_usdt + amount
                data[d]['balance']['tether'] = new_usdt
        if new_usdt > 0:
            with open('database.dat', 'wb') as database:
                pickle.dump(data, database)
                database.close()
        else:
            await message.channel.send("Printing was canceled, you would have ended up with a negative USDT balance.")

    elif message.content.startswith('$balance '):
        token_id = message.content[9:]
        print(token_id)
        try:
            data = get_data()
            print(data)
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    balance = data[d]['balance'][token_id]
                    try:
                        price = float(get_price(token_id))
                    except Exception as Unlisted:
                        price = 0
                    dollar_value = balance * price
                    await message.channel.send("Balance of " + str(message.author) + '\n' + str(balance) + ' ' + token_id + ' | ' + '(' + '~' + cut(str(dollar_value)) + '$' + ')' )
        except Exception as NoBalance:
            print(str(NoBalance))
            await message.channel.send(E1)
            #await message.channel.send("Sorry, the token ID you entered is incorrect, or the token you specified is currently not supported by this bot, you can get it by reading the coingecko URL of your desired coin. To do so, visit coingecko.com and select your desired coin. Example: https://www.coingecko.com/de/munze/bitcoin ( token ID: 'bitcoin' ) List of supported Tokens: [USDT, SOON]")

    elif message.content.startswith('$price '):
        try:
            token_id = message.content[7:]
            token_price = get_price(token_id)
            await message.channel.send('1 ' + token_id + ' is currently worth ' + '\n' + str(token_price) + '$')
        except Exception as Invalid:
            await message.channel.send(E1)
        #await message.channel.send('Balance of User ' + str(message.author))

    elif message.content.startswith('$sell '):
        data = get_data()
        token_id = message.content.split()[1]
        amount = message.content.split()[2]
        if amount == 'all':
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    amount = float(data[d]['balance'][token_id])
        else:
            amount = float(message.content.split()[2])
        if amount <= 0:
            await message.channel.send("don't mess with me.")
            return
        try:
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    new_token_balance = data[d]['balance'][token_id] - amount
                    new_theta_balance = data[d]['balance']['tether'] + (amount * get_price(token_id))
                    data[d]['balance'][token_id] = new_token_balance
                    data[d]['balance']['tether'] = new_theta_balance
                    if data[d]['balance'][token_id] < 0:
                        await message.channel.send("sorry, you can not afford this trade. you don't have enough " + token_id + ' to sell ' + str(amount) + ' coins.')
                        return
            with open('database.dat', 'wb') as database:
                pickle.dump(data, database)
                database.close()
        except Exception as E:
            print(E)

    elif message.content.startswith('$buy '):
        data = get_data()
        token_id = message.content.split()[1]
        amount = float(message.content.split()[2])
        if amount <= 0:
            await message.channel.send("don't try me.")
            return
        try:
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    new_token_balance = data[d]['balance'][token_id] + (amount / get_price(token_id))
                    new_theta_balance = data[d]['balance']['tether'] - amount
                    data[d]['balance'][token_id] = new_token_balance
                    data[d]['balance']['tether'] = new_theta_balance
                    if data[d]['balance']['tether'] < 0:
                        await message.channel.send("sorry, you can not afford this trade. use $print x to add more Tether to your wallet")
                        return
            with open('database.dat', 'wb') as database:
                pickle.dump(data, database)
                database.close()
        except Exception as E:
            print(E)
    elif message.content.startswith('$connect'):
        coinstats_url = message.content.split()[1]
        set_key(message.author.id, 'coinstats_url', coinstats_url)
        data = get_data()
        for d in range(0, len(data)):
            if data[d]['id'] == message.author.id:
                print(data[d]['coinstats_url'])
                await message.channel.send('Your coinstats account was connected: ' + str(data[d]['coinstats_url']))

    elif message.content.startswith('$update') and str(message.author.id) == admin_id:
        try:
            key = message.content.split()[1]
            for d in range(0, len(data)):
                if key in data[d]:
                    await message.channel.send("Warning! Abort. It seems this key already exists, are you sure it hasn't been added yet?")
                    return
            default = message.content.split()[2]
            for d in range(0, len(data)):
                data[d][key] = default
            with open('database.dat', 'wb') as database:
                pickle.dump(data, database)
            print('Added key: ' + str(key) + ' with default value: ' + str(default))
        except Exception as E:
            print(str(E))
            await message.channel.send('Error! Update failed! Data might have been corrupted.')

    elif message.content.startswith('$csbalance'):
        coinstats_url = ''
        try:
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    coinstats_url = data[d]['coinstats_url']
            if coinstats_url[0:4] == 'http':
                page = requests.get(coinstats_url)
                page_content = html.fromstring(page.content)
            else:
                await message.channel.send('Invalid coinstats url, did you $connect your account yet? If not, please do that first. Example: $connect https://coinstats... ')
                return
        except Exception as E:
            await message.channel.send('Invalid coinstats url, did you $connect your account yet? If not, please do that first. Example: $connect https://coinstats... ')
            return
        csbalance = page_content.xpath(cs_balance_xpath)[0]
        await message.channel.send('Your linked coinstats portfolio is worth: ' + str(csbalance))

    elif message.content.startswith('$reset'):
        reset(message.author.id)
        await message.channel.send("All of your balances were reset to 0. Enjoy a fresh start :)")

    elif message.content.startswith('$market'):
        try:
            id = message.content.split()[1]
            endpoint = '/coins/markets?vs_currency=usd&ids=' + id + '&order=market_cap_desc&per_page=100&page=1&sparkline=false'
            r = requests.get(coingecko_base_url + endpoint)
            res_json = json.loads(r.text)
            result = res_json[0]
            await message.channel.send('ID: ' + id + '\n' + '-'*50 + '\n' + 'rank: #' + str(result['market_cap_rank']) + '\n' + '24h high: ' + str(result['high_24h']) + '$' + '\n' + '24h low: ' + str(result['low_24h']) + '$' + '\n' + 'total supply: ' + str(result['total_supply']) + ' ' + id + '\n' + '24h change: ' + str(result['price_change_24h']) + '$' + '\n' + '24h change %age: ' + str(result['price_change_percentage_24h']) + '%' + '\n' + 'all time high: ' + str(result['ath']) + '\n' + 'ath date: ' + str(result['ath_date']) + '\n' + 'from ath: ' + str(result['ath_change_percentage']) + '%' + '\n' + 'all time low: ' + str(result['atl']) + '$' + '\n' + 'atl date: ' + str(result['atl_date']) + '\n' + 'from atl: ' + str(result['atl_change_percentage']) + '%' + '\n' 'price: ' + str(result['current_price']) + '$' + '\n' + '-'*50)
        except Exception as E:
            print(str(E))
            await message.channel.send('Market data could not be resolved, is the token $supported ?')
    elif message.content.startswith('$upgrade') and str(message.author.id) == admin_id:
        try:
            data = get_data()
            current_ids = gecko_ids()
            token_ids = []
            for i in range(0, len(current_ids)):
                if str(current_ids[i]) not in str(data):
                    await message.channel.send("Found new token: " + str(current_ids[i]))
                    token_ids.append(len(token_ids))
                    token_ids[len(token_ids) - 1] = current_ids[i]
            if len(token_ids) == 0:
                await message.channel.send("Coingecko has not added any new tokens to it's API. The bot is up to date.")
                return
            for t in range(0, len(token_ids)):
                token_id = str(token_ids[t])
                for d in range(0, len(data)):
                    data[d]['balance'][token_id] = 0.0
            with open('database.dat', 'wb') as database:
                pickle.dump(data, database)
            for tok in range(0, len(token_ids)):
                await message.channel.send("New Token added to bot: " + str(token_ids[tok]))
        except Exception as E:
            await message.channel.send("Error fetching new Token(s): " + str(E))

    elif message.content.startswith('$supported'):
        id = message.content.split()[1]
        if id in gecko_ids():
            await message.channel.send(id + ' is supported.')
        else:
            await message.channel.send(id +  " is not supported yet. visit https://api.coingecko.com/api/v3/simple/price?ids=" + id + "&vs_currencies=usd" + '\n' + "if this request doesn't return '{}' in your browser, tell the admin to run $upgrade, because a value within the brackets would mean the coin got added to tha API and the database of the bot is outdated.")

    elif message.content.startswith('$sregister') and str(message.author.id) == admin_id:
            ids = gecko_ids()
            data = []
            data.append(len(data))
            data[len(data) - 1] = {}
            data[len(data) - 1]['id'] = message.author.id
            data[len(data) - 1]['balance'] = {}
            for i in range(0, len(ids)):
                data[len(data) - 1]['balance'][ids[i]] = [0, 0]
            with open('staking.dat', 'wb') as stakingbase:
                pickle.dump(data, stakingbase)
                stakingbase.close()

    elif message.content.startswith('$sregister'):
        ids = gecko_ids()
        with open('staking.dat', 'rb') as stakingbase:
            data = pickle.load(stakingbase)
        set = {}
        set['id'] = message.author.id
        set['balance'] = {}
        for i in range(0, len(ids)):
            set['balance'][ids[i]] = [0, 0]
        data.append(len(data))
        data[len(data) - 1] = set
        with open('staking.dat', 'wb') as stakingbase:
            pickle.dump(data, stakingbase)
            stakingbase.close()

    elif message.content.startswith('$sbalance'):
        try:
            annual = 0
            id = message.content.split()[1]
            with open('staking.dat', 'rb') as stakingbase:
                data = pickle.load(stakingbase)
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    staking_balance = data[d]['balance'][id][0]
                    if data[d]['balance'][id][1] != 0:
                        if id in flexible_plans:
                            annual = flexible_plans[id]
                            psec = annual / 365 / 24 / 60 / 60
                            staking_balance += staking_balance * psec * (int(time.time())-data[d]['balance'][id][1])
                    else:
                        try:
                            if id in flexible_plans:
                                annual = flexible_plans[id]
                        except Exception as E:
                            print(str(E))

            await message.channel.send('You have ' + str(staking_balance) + ' ' + id + ' in a flexible interest plan generating ' + str(annual * 100) + '% p.a.')

        except Exception as E:
            print(str(E))
            await message.channel.send('No entry found in database, please use $sregister first.')

    elif message.content.startswith('$sterms'):
        flexible = '[FLEXIBLE INTEREST PLANS]: ' + '\n'
        for key in flexible_plans:
            flexible += 'Token: ' + key + ' | Interest (p.a.): ' + str(flexible_plans[key]*100) + '%' + '\n'
        await message.channel.send(flexible)

    elif message.content.startswith('$slock'):
        id = message.content.split()[1]
        amount = message.content.split()[2]
        if float(amount) < 0:
            await message.channel.send("don't mess with me.")
            return
        data = get_data()
        for d in range(0, len(data)):
            if data[d]['id'] == message.author.id:
                if data[d]['balance'][id] < float(amount):
                    await message.channel.send("sorry, you can not afford this transaction. use $print x to add more Tether to your wallet and buy the desired token using $buy.")
                    return
                else:
                    data[d]['balance'][id] = data[d]['balance'][id] - float(amount)
        with open('database.dat', 'wb') as database:
            pickle.dump(data, database)
            database.close()

        with open('staking.dat', 'rb') as stakingbase:
            data = pickle.load(stakingbase)
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    if data[d]['balance'][id][0] > 0:
                        await message.channel.send('You already have tokens locked in this staking term. To re-charge this term, you need to withdraw first. You can use $sunlock TOKEN all.')
                        recovery = get_data()
                        for d in range(0, len(recovery)):
                            if recovery[d]['id'] == message.author.id:
                                recovery[d]['balance'][id] = recovery[d]['balance'][id] + float(amount)
                        with open('database.dat', 'wb') as database:
                            pickle.dump(recovery, database)
                            database.close()
                        return
                    data[d]['balance'][id][0] = float(data[d]['balance'][id][0]) + float(amount)
                    data[d]['balance'][id][1] = int(time.time())
        with open('staking.dat', 'wb') as stakingbase:
            pickle.dump(data, stakingbase)
            stakingbase.close()
        await message.channel.send('Successfully transferred ' + str(amount) + ' ' + id + ' to flexible staking term.')

    elif message.content.startswith('$sunlock'):
        try:
            id = message.content.split()[1]
            amount = message.content.split()[2]
            try:
                if float(amount) < 0:
                    await message.channel.send("don't mess with me.")
                    return
            except Exception as E:
                pass
            with open('staking.dat', 'rb') as stakingbase:
                data = pickle.load(stakingbase)
                for d in range(0, len(data)):
                    if data[d]['id'] == message.author.id:
                        staking_balance = data[d]['balance'][id][0]
                        if id in flexible_plans:
                            annual = flexible_plans[id]
                            psec = annual / 365 / 24 / 60 / 60
                            staking_balance += staking_balance * psec * (int(time.time())-data[d]['balance'][id][1])
                            try:
                                if staking_balance < float(amount):
                                    await message.channel.send("sorry, you can not afford this transaction. use $print x to add more Tether to your wallet and buy the desired token using $buy.")
                                    return
                            except Exception as E:
                                pass
                        if amount != 'all':
                            new_staking_balance = staking_balance - float(amount)
                            data[d]['balance'][id][0] = new_staking_balance
                        else:
                            amount = staking_balance
                            new_staking_balance = 0
                            data[d]['balance'][id][0] = new_staking_balance
                            data[d]['balance'][id][1] = 0
                        break
                with open('staking.dat', 'wb') as stakingbase:
                    pickle.dump(data, stakingbase)
                data = get_data()
                for d in range (0, len(data)):
                    if data[d]['id'] == message.author.id:
                        data[d]['balance'][id] = data[d]['balance'][id] + float(amount)
                with open('database.dat', 'wb') as database:
                    pickle.dump(data, database)
                    database.close()
                await message.channel.send("Successfully withdrew " + str(amount) + ' ' + id + ' from flexible staking term.')
        except Exception as E:
            await message.channel.send("Unresolved Error: " + str(E) + '\n' + 'Please check your input.')

    elif message.content.startswith('$shodling') or message.content.startswith('$sholding'):
        try:
            with open('staking.dat', 'rb') as stakingbase:
                data = pickle.load(stakingbase)
            for d in range(0, len(data)):
                if data[d]['id'] == message.author.id:
                    balance = 'STAKED HODLINGS (FLEXIBLE)' + '\n'
                    for key in data[d]['balance']:
                        staking_balance = data[d]['balance'][key][0]
                        if staking_balance != 0:
                            if key in flexible_plans:
                                annual = flexible_plans[key]
                                psec = annual / 365 / 24 / 60 / 60
                                staking_balance += staking_balance * psec * (int(time.time())-data[d]['balance'][key][1])
                            else:
                                annual = 0
                            balance += key + ': ' + str(staking_balance) + ' (' + str(annual * 100) + '% p.a.)' + '\n' + ' ' + '\n'
                            print(balance)
                    await message.channel.send(balance)
        except Exception as E:
                    await message.channel.send('Looks like you have no coins locked into staking. If this is a mistake, please contact the developer.')

    await message.add_reaction('<:CheckMark:830850554967097384>')



client.run(os.getenv('DISCORD_TOKEN'))
