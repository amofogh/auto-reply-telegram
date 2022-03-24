from telethon import TelegramClient , events
from time import asctime , sleep
from os import mkdir , path
from colorama import Fore, Style
import sqlite3

class Auto_reply(object):
    
    def __init__(self ):
        '''
        run just class to lead to the menu
        '''
        self.connect_db()
        
        # login/signup menu
        chance = 3
        while chance :
            print(Fore.RED + '{0} chance remaining'.format(chance) + Style.RESET_ALL)
            acc_status = input('Do you have account ? (yes/no) (0 for something else) : ')
            if acc_status == 'yes': #Have session file
                self.get_username()
                break
            elif acc_status == 'no' :
                self.session_creator()
                break
            elif acc_status == '0':
                break
            else:
                if chance == 1 : #break the while after 3 chance
                    print('Chance is Over')
                    break
                chance -= 1
                print('yes or no Try again !!')
                
    def session_creator(self):  
        print(Fore.CYAN +"Welcome to the Session Creator")
        print("-"*30)
        print('''
You need api_id and api_hash for creating session get those from here 
Api --> https://my.telegram.org/auth?to=apps
Guide --> https://core.telegram.org/api/obtaining_api_id
            ''' + Style.RESET_ALL)
        chance = 3

        while chance :
            # get all info for login
            try :
                print(Fore.RED + '{0} Chance remaining !!'.format(chance) + Style.RESET_ALL)
                username = input('Enter your username or just a name if you havent : ')
                api_id = input('Enter your api_id : ')
                api_hash = input('Enter your api_hash : ') 
                phone = int(input('Enter your phone number (Ex:989121234545) : '))
                password = input('Enter your telegram password (if you havent press enter) : ')
                
                self.add_user(username, api_id, api_hash, phone , password)

                self.get_username()
                break
            except KeyboardInterrupt :
                print('Exiting...')
                sleep(1)
                break
            
            except BaseException as e :
                print(e)

                if chance == 1 :
                    print('Chance is over')
                    break
                chance -= 1

    def get_username(self): #checking username and
        print('Welcome to the Check Username')

        person = input('Enter your username or name please : ')
        
        #check username in database
        # (username ,api_id , api_hash , phone_number , password)
        # EX: ('las', 12345, 'asdeafe2', 935434193, None)
        self.data = self.read_db(person)
        if self.data == None:
            return 'User Not found'

        print('default message is : "the big chief is offline now I bring your message to him thank you !!"')
        msg = input('Your message for reply when you are offline (Type d for default):')
        if msg == 'd' : # Default message
            msg = "the big chief is offline now I bring your message to him thank you !!"
        self.message = msg
        self.auto_reply()
        
    def auto_reply(self):

        #check sessions folder exists
        self.__create_directory('sessions')
        
        client = TelegramClient('sessions/' + str(self.data[3]), self.data[1], self.data[2], sequential_updates=True)
        messages = []

        @client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):

            if event.is_private:  # only auto-reply to private chats
                from_ = await event.client.get_entity(event.from_id)  # this lookup will be cached by telethon
                if not from_.bot:  # don't auto-reply to bots

                    print(event.message)
                    msg = asctime(), event.message.message  
                    msg = self.tuple_to_list(msg) #convert tuple to list for append more info

                    sender = await event.get_sender()
                    msg.append(sender.username)
                    msg.append(sender.first_name)
                    msg.append(sender.last_name)
                    msg.append(sender.phone)

                    print(msg)
                    messages.append(msg)
                    sleep(1)  # pause for 1 second to rate-limit automatic replies
                    await event.respond(self.message)
        
        
        print(asctime(), '-', 'Auto-replying...')
        client.start(self.data[3], self.data[4])
        client.run_until_disconnected()
        print('Auto Reply has been Stopped!')
        #write the message with time             
        self.write_messages(messages)
    
    
    # first msg is tuple we have to change it to list
    def tuple_to_list(self,mytuple):
        new = []
        for i in mytuple:
            new.append(i)
        return new

    def write_messages(self , messages):
        pattern = ['Time' , 'Message' , 'Username' , 'FirstName' , 'LastName' , 'PhoneNumber']

        #check log folder exists
        self.__create_directory('log')

        #write messages in file for log
        with open('log/msg-log-{0}.txt'.format(self.data[0]),'a',encoding='utf-8') as file :
            now = asctime() + '\n' + '-' *20 + '\n'
            file.write(now)
            counter = 1
            for message in messages :
                x = zip(pattern , message)
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
    
    def __create_directory(self,dir_name):
        #check dir_name folder exists
        if path.exists(dir_name) == False:
            mkdir(dir_name)
    
    # write and read from database
    def connect_db(self):
        self._db = sqlite3.connect('telegram_users.db')
        self.cursor = self._db.cursor()
        
        #create table if not exists then connect to them and use telegram_users as main db
        self.create_db()
    
        self.cursor = self._db.cursor()
    
    def create_db(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS accounts (
                                username varchar(255) NOT NULL PRIMARY KEY ,
                                api_id BIGINT NOT NULL,
                                api_hash varchar(255) NOT NULL,
                                phone_number BIGINT NOT NULL UNIQUE,
                                password varchar(255)
                                );
        ''')
        
    def add_user(self , username , api_id:int , api_hash , phone_number:int , password = None):
        '''
        write phone_number without 0 on the first    
        '''
        # (username , api_id , api_hash , phone_number , password)
        sql = 'INSERT INTO accounts VALUES (? , ? , ? , ? , ? )'
        val = (username , api_id , api_hash , phone_number , password )
        
        self.cursor.execute(sql,val)
        self._db.commit()
        
        print(f"the {username} has been added to the database !!")
        
    def read_db(self , username):
        # sql = 'SELECT * FROM accounts WHERE username = {0}'.format(username)
        sql = f"SELECT * FROM accounts WHERE username ='{username}'"
        self.cursor.execute(sql)
        myresult = self.cursor.fetchall()
        #return the row we get from the database
        for x in myresult:
            return x

    def reset_db(self):
        sql = 'TRUNCATE TABLE accounts'
        self.cursor.execute(sql)
        print('The accounts table has been reseted !!')
    
    def delete_user(self , username):
        sql = f'DELETE FROM accounts WHERE username = {username}'
        self.cursor.execute(sql)
        self._db.commit()
    
    def update_user(self , username:dict , changes:dict , table_name='accounts'):
        '''
        changes var have to be dict EX --> {api_hash:qwe , api_id = 123}
        username var have to be dict too and key is for find the row with WHERE
        the keys in the username value have to be username or phone_number (exact word)
        '''
        #check the variables
        
        #loop for all changes in the dict
        for i in changes:
                
            sql = "UPDATE {0} SET {1} = '{2}' WHERE {3} = '{4}'".format(table_name,i,changes[i],'username',username)
            self.cursor.execute(sql)
            self._db.commit()
            print(f'The {username} user has been updated !!')

instanse = Auto_reply().update_user('am_ofogh', {'api_id': 111})
