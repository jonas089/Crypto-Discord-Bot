import discord
import os
import requests
from dotenv import load_dotenv
from lxml import html
import pickle
import json
coingecko_base_url = 'https://api.coingecko.com/api/v3'
client = discord.Client()
load_dotenv()

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
        await message.channel.send('[BASIC]' + '\n' + '1. $register | to join this bot, required to execute any commands.' + '\n' + '2. $print AMOUNT | add a specific AMOUNT of USDT (tether) to your balance, you can print negative values, but can not have less than 0 USDT. The %age gains take your printing in consideration so print as much as you want, it wont affect your performance and stats :).' + '\n' + '3. $price TOKEN | get price of a TOKEN.' + '\n' + '4. $balance TOKEN | get balance of a specific TOKEN.' + '\n' + '5. $hodling | get all balances that are not 0 (your entire portfolio).' + '\n' + '6. $buy TOKEN AMOUNT | buy a specific TOKEN for a specifict AMOUNT of USDT (tether), check your tether balance using the command "$balance tether."'+ '\n' + '7. $sell TOKEN AMOUNT, sell a specific AMOUNT of a specific TOKEN at the current market price of the given token (you will receive USDT / tether). You can sell your entire hodling by simply using $sell TOKEN all' + '\n' + '8. $reset | resets all balances and stats to 0, allowing for a fresh start.' + '\n' + '[ADVANCED]' + '\n' + '1. $connect COINSTATS_URL | allows you to connect your actual coinstats.app account (by setting up a direct link to your coinstats.app portfolio).' + '\n' + '2. $csbalance | returns the current balance of your linked coinstats.app portfolio (direct link), only works in case you have properly set up your portfolio using the $connect command.' + '\n' + '[ADMIN ONLY]' + '\n' + '1. $update KEY VALUE | adds a new key to the database and sets VALUE as default value for all users in the database. This command is admin-only, because the risk of loosing data is very high.' + '\n' + '2. $upgrade | automatically search for new tokens on coingecko and add them to the bot.')

    elif message.content.startswith('$hodling'):
        total_balance = 0.0
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
                            await message.channel.send(key + ': ' + str(data[d]['balance'][key]) + ' | (' + cut(str(data[d]['balance'][key] * price)) + '$)')
                            total_balance += data[d]['balance'][key] * price
            printed = get_printed(message.author.id)
            profit = total_balance - printed

            percentage_change = 100 * (total_balance - printed) / printed
            await message.channel.send('overall: ' + cut(str(total_balance)) + '$')
            await message.channel.send('You printed: ' + str(printed) + ' USDT' + '\n' + 'PNL: ' + cutx(str(profit), 3) + '$' + '\n' + 'Percentage gains: ' + cutx(str(percentage_change), 3) + '%')
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
        for d in range(0, len(data)):
            if data[d]['id'] == message.author.id:
                coinstats_url = data[d]['coinstats_url']
        if coinstats_url[0:4] == 'http':
            page = requests.get(coinstats_url)
            page_content = html.fromstring(page.content)
        else:
            await message.channel.send('Invalid coinstats url, did you $connect your account yet? If not, please do that first. Example: $connect https://coinstats... ')
        csbalance = page_content.xpath(cs_balance_xpath)[0]
        await message.channel.send('Your linked coinstats portfolio is worth: ' + str(csbalance))
    elif message.content.startswith('$reset'):
        reset(message.author.id)
        await message.channel.send("All of your balances were reset to 0. Enjoy a fresh start :)")

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

client.run(os.getenv('DISCORD_TOKEN'))
