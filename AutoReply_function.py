from telethon import TelegramClient , events
import time
from re import search
from os import mkdir , path
from colorama import Fore,Style

def session_creator():
    print("Welcome to the Session Creator")
    print("-"*30)
    print('''
    YOu need api_id and api_hash for creating session get those from here 
    Api --> https://my.telegram.org/auth?to=apps
    Guide --> https://core.telegram.org/api/obtaining_api_id
        ''')

    def create_session(api_id , api_hash , phone , password ):
        #check db folder exists
        if path.exists('db') == False:
            mkdir('db')
                                #set session file name to phone number
        client = TelegramClient('db/' + phone , api_id, api_hash)
        client.start('+' +phone, password)

    chance = 5

    while chance :
        try :
            print('{0} Chance remain !!'.format(chance))
            username = input('Enter your username : ')
            api_id = input('Enter your api_id : ')
            api_hash = input('Enter your api_hash : ')
            phone = input('Enter your phone number with country code (Ex:11231231234) : ')
            password = input('Enter your telegram password (if you havent press enter) : ')
            create_session(api_id , api_hash , phone , password)

            #write username and phone for search in db
            with open('db/userdb.txt' , 'a') as file :
                text = username + ' --> ' + phone + '\n'
                file.write(text)

            #write these data to db for use later
            file_name = 'db/' + str(phone) + '.txt'
            with open(file_name,'w' , encoding='utf-8') as f:
                f.write(api_id + '\n')
                f.write(api_hash + '\n')
                f.write('+' + phone + '\n')
                f.write(password + '\n')
                f.write(phone)

            break
        except KeyboardInterrupt :
            print('\nExiting...')
            time.sleep(1)
            print('.')
            time.sleep(1)
            print('.')
            time.sleep(1)
            print('.')
            break
        
        except BaseException as e :
            print(e)

            if chance == 1 :
                print('Chance is over')
                break
            chance -= 1

message = "the big chief is offline now I bring your message to him thank you !!"

def start_auto_reply():
    person = input('Enter your username please : ')
    msg = input('Your message for reply when you are offline (Type d for default):')
    
    with open('db/{0}.txt'.format(read_db(person))) as file :
        get_info = file.read()
        info_list = get_info.split('\n')
    if msg == 'd' :
        msg = message
        
    try :
        Auto_reply(info_list[0], info_list[1] , info_list[2] , info_list[3] , info_list[4] , msg , person)
    except BaseException as e:
        print(e)
        
def Auto_reply(api_id , api_hash , phone , password , session_file , message , person):

    client = TelegramClient('db/' + session_file, api_id, api_hash, sequential_updates=True)
    messages = []

    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):

        if event.is_private:  # only auto-reply to private chats
            from_ = await event.client.get_entity(event.from_id)  # this lookup will be cached by telethon
            if not from_.bot:  # don't auto-reply to bots

                print(event.message)
                msg = time.asctime(), event.message.message  
                msg = tuple_to_list(msg)

                sender = await event.get_sender()
                msg.append(sender.username)
                msg.append(sender.first_name)
                msg.append(sender.last_name)
                msg.append(sender.phone)

                print(msg)
                messages.append(msg)
                time.sleep(1)  # pause for 1 second to rate-limit automatic replies
                await event.respond(message)

    print(time.asctime(), '-', 'Auto-replying...')
    client.start(phone, password)
    client.run_until_disconnected()
    print('Auto Reply has been Stopped!')
    write_messages(messages , person)
    
# first msg is tuple we have to change it to list
def tuple_to_list(mytuple):
    new = []
    for i in mytuple:
        new.append(i)
    return new

def write_messages(messages , person):
    pattern = ['Time' , 'Message' , 'Username' , 'FirstName' , 'LastName' , 'PhoneNumber']
    
    #check log folder exists
    if path.exists('log') == False:
        mkdir('log')
    
    #write messages in file for log
    with open('log/msg-log-{0}.txt'.format(person),'a',encoding='utf-8') as file :
        now = time.asctime() + '\n' + '-' *20 + '\n'
        file.write(now)
        counter = 1
        for i in messages :
            x = zip(pattern , i)
            file.write(str(counter ))
            file.write('\n')

            for p,m in x :
                if m == None :
                    m = 'None'
                msg = p + ' --> ' + m
                file.write(msg)
                file.write('\n')

            file.write('\n')
            counter += 1

        file.write('\n')
        print('Messages has been saved !')

def read_db(username):
    with open(r"db/userdb.txt" , 'r') as f:
        users = f.readlines()
        for j in users : 
            result = search(r'{0}'.format(username) , j)   
            if result != None:
                res = j.split(' ')
                res = res[2].strip('\n') #remove \n end of the phone numbers
                return res
        print("Not Found")
        
#! end of functions

print(Fore.CYAN + 'Welcome to the AutoReply')
print('This bot sends messages to who people sent you message when youre offline!' + Style.RESET_ALL)
while True:
    acc_status = input('Do you have a account ? (y/n) (q for quit):')
        
    if acc_status == 'n' :
        session_creator()
    elif acc_status == 'y' :
        start_auto_reply()
    elif acc_status == 'q':
        break
    else:
        print('Try again')
