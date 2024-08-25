from django.shortcuts import render              #simplifies the process of rendering HTML templates with context data
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import userProfile,Event,Donation,Account,Blog,Track,Feedback
from web3 import Web3                          #web3 is a Python library used to interact with Ethereum nodes
import pandas as pd
import numpy as np
import re
import string
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling1D, Embedding, MultiHeadAttention, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
import tensorflow as tf
from django.core.files.storage import FileSystemStorage

ganache_url = "HTTP://127.0.0.1:7545"

from solcx import compile_standard, install_solc         # import the compile_standard and install_solc functions from the solcx module 
install_solc('0.8.0')                   # then call the install_solc function to install Solidity compiler version 0.8.0.

import json

accounts_list = [{"address":"0x716e37EBaB8A31507e48204ce12C73668d3ae609","private_key":"0x40fb77c57fa97cbf2272f0260734add6b417f7613f649ab971f7654566dcb40e"},{"address":"0xB57ad6BC98E1a84699cF8B6b6Fe807936Ae0C4a8","private_key":"0x612789267ca9a0a7b263e71f9c3435f2b11591bbe9f7e6838c37424364f3b747"},{"address":"0xE4a42E0E24c42febf087271517CcfAF969caEce3","private_key":"0x4a1c6c26042dadfb85f64e0cc10a5b371cbb39f138a2eb7002227a89cb85d4bd"}]
accounts_list_charity = [{"address":"0x5F394896AeCDf8b13bc7841CA376fFe2a45246fd","private_key":"0x639dbe3c15da76332ee5d7b846013511d3527bc7ecf5390c3d05cfe1620e3d06"},{"address":"0x8A74033E25A4588a3C24DDa7a4e0317825D2AAD1","private_key":"0xf734702508d42a6898f8014a22ac2a8ed499a66d70bcc7144ec37da4bf0f845d"},{"address":"0x97C85a7E1592C4Ed85A5F1335D2763fb688BF6Fb","private_key":"0x1809870717b02c32001d395bf9021815463dcb7c38443c2c5b258120f81a4568"}]

with open("donation.sol", "r") as file:
    contact_list_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)

with open("donation_code.json", "w") as file:
    json.dump(compiled_sol, file)          # dump() is used to write JSON data to a file-like object
address = "0xb9F21C013EA140c79d66Fe4D2B82813c9bB049aC"
private_key = "0xafe8675e8af7e4bd0c7380ead58f66b14d30eaa6c977f23b6505190c5489f3a8"


def homepage(request):
    positive = Feedback.objects.filter(sentiment = "positive").count()
    neutral = Feedback.objects.filter(sentiment = "neutral").count()
    negative = Feedback.objects.filter(sentiment = "negative").count()
    if request.user.is_authenticated:
        profile = userProfile.objects.filter(user = request.user).first() #If logged in, retrieves the user's profile from the database

    else:
        profile = ''        #If not logged in, sets the profile variable to an empty string
    blog = Blog.objects.all().order_by('-date')   #Orders the blog entries by their date in descending order.
    return render(request,'index.html',context = {"positive":positive,"negative":negative,"neutral":neutral,'profile':profile,"blogs":blog[:2],'feeds':Feedback.objects.all()})    # the index.html template can use it to render the page dynamically


message = 0
reg_error = 0

import random


def register(request):       #to handle user registration 
    if request.method == 'POST':   #indicates that the form on the registration page has been submitted
        user = User.objects.create(username = request.POST.get('username'),email=request.POST.get('email'))  #creates a new user object
        user.set_password(request.POST.get('password'))
        user.save()

        file = request.FILES.get('file')
        fss = FileSystemStorage()
        filename = fss.save(file.name,file)
        url = fss.url(filename)    #URL of the saved file is obtained
   
        user = User.objects.filter(username=request.POST.get('username')).first()   #It then creates a corresponding user profile object and associates it with the user
        
        profile = userProfile.objects.create(user=user)
        random_account = random.choice(accounts_list)
        print(random_account)
        profile.account_address = random_account['address']
        profile.private_key = random_account['private_key']
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.image = url
        profile.account_type = "Normal user"
        profile.save()


    return HttpResponseRedirect(reverse('homepage'))


def registercharity(request):          #to handle charity registration
    if request.method == 'POST':
        user = User.objects.create(username = request.POST.get('username'),email=request.POST.get('email'))
        user.set_password(request.POST.get('password'))
        user.save()

        file = request.FILES.get('file')          #handle the file upload associated with the registration
        fss = FileSystemStorage()
        filename = fss.save(file.name,file)
        url = fss.url(filename)
   
        user = User.objects.filter(username=request.POST.get('username')).first()
        
        profile = userProfile.objects.create(user=user)
        random_account = random.choice(accounts_list_charity)
        print(random_account)
        profile.account_address = random_account['address']
        profile.private_key = random_account['private_key']
        profile.organization_name = request.POST.get('username')
        profile.organization_phone = request.POST.get('phone')
        profile.organization_address = request.POST.get('address')
        profile.image = url
        profile.account_type = "Organization account"
        profile.save()


    return HttpResponseRedirect(reverse('homepage'))   


def checkLogin(request):                    #to handle user login attempts, authenticate users based on the provided credentials
    
    username = request.POST.get('username')             #These lines retrieve the username and password submitted through a POST request
    password = request.POST.get('password')

    user = authenticate(username = username,password = password)
    if user:
        print(username)
        return JsonResponse({"message":0})
            
    else:
        print("No user found")
        return JsonResponse({"message":1})

message = 0
reg_error = 0

def checkSignup(request):             #validate the availability of a username for user signup
    
    username = request.POST.get('username')
    password = request.POST.get('password')

    
    u = User.objects.filter(username = username).first()
    
    if u == None:
        message = 0
    else:
        message = 1
    
    return JsonResponse({"message":message})   

def user_login(request):
   
    if request.method == 'POST':
        username = request.POST.get('username')        # extract the values of username and password from the POST request
        password = request.POST.get('password')
        
        user = authenticate(username = username,password = password)
        if user:

            if user.is_active:
                login(request, user)
                print("login success!!!")
                return HttpResponseRedirect(reverse('homepage'))
        else:
            
            print("No such user")


    return HttpResponseRedirect(reverse('homepage'))
    
@login_required
def user_logout(request):

    logout(request)


    return HttpResponseRedirect(reverse('homepage'))


def donations(request):
    events = Event.objects.filter(approved = True)      #to fetch all Event objects where the approved field is set to True
    
    
    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)

    with open("donation_code.json", "w") as file:              
        json.dump(compiled_sol, file)
    #extract the bytecode and ABI from the compiled Solidity code stored in compiled_sol
    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))        #It connects to the local Ethereum node running at HTTP://127.0.0.1:7545
    events_all =[]         #initializes an empty list to store information about all events
    
    print("[+] Events : ",events)
    for event in events:
        # remaining =0
        sumAmt = 0
        donations = Donation.objects.filter(event = event)
        if donations:
            for donation in donations:
            
                
                
                sumAmt += int(donation.amount)
                print("[+] Sum amount : ",sumAmt)
                toGo = event.goal - sumAmt
                if toGo <= 0:
                    remaining = 0
                else:
                    remaining = toGo
        else:
            remaining = event.goal - sumAmt
        
        #is to organize and encapsulate information about each event in a structured format
        eve = {'title':event.title,"description":event.description,"user":event.user,"date":event.date,'raised':sumAmt,"goal":event.goal,"pk":event.pk,"image":event.image,"toGo":remaining,"hashtag":event.hashtag}
        events_all.append(eve)
    profile = userProfile.objects.filter(user = request.user).first()

    # print(events_all)
    profile = userProfile.objects.filter(user = request.user).first()
    return render(request,'donation.html',{"events":events_all,"profile":profile})


def createEvent(request):
    user = User.objects.filter(username = request.user.username).first() #o retrieve a user object from the database based on the username of the user who is currently making the request.
    print(user)
    
    event = Event.objects.create(title = request.POST.get('title'),description = request.POST.get('description'),image = request.FILES['image'],phone = request.POST.get('phone'),address = request.POST.get('address'),user = user, goal = request.POST.get('goal'),hashtag = request.POST.get('hashtag'))
    
    

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]

    from web3 import Web3

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
    # Create the contract in Python
    ContactList = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the number of latest transaction
    nonce = w3.eth.getTransactionCount(address)

    #This code builds a transaction object for deploying the smart contract to the blockchain
    transaction = ContactList.constructor().buildTransaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )
    # It signs the transaction with a private key.
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")
    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"[+] Done! Contract deployed to {transaction_receipt.contractAddress}")
    block = Account.objects.create(username = request.POST.get('beneficiary'),transaction_address = str(transaction_receipt.contractAddress),event = event,charityName = request.user.username,address = request.POST.get('accAddress'))
    eventHost = userProfile.objects.filter(user = event.user).first()
    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    
    import datetime
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y at %I:%M %p")

    print("Current date and time:", formatted_time)
    #This code builds a transaction to add event details to the deployed smart contract.
    store_contact = contact_list.functions.addEventDetails(
        request.POST.get('beneficiary'),str(formatted_time),request.POST.get('accAddress'),request.POST.get('goal'),str(eventHost.account_address)
    ).buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

    # Sign the transaction with a private key
    sign_store_contact = w3.eth.account.sign_transaction(
        store_contact, private_key=private_key
    )
    
    return HttpResponseRedirect(reverse('homepage'))


def eventView(request,pk):
    event = Event.objects.filter(pk = pk).first()
    donations = Donation.objects.filter(event = event)
    donation = Donation.objects.filter(event = event).first()
    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)

    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0

    for donation in donations:
        
        
       
        sumAmt += int(donation.amount)
    toGo = event.goal - sumAmt
    if toGo <= 0:
        remaining = 0
    else:
        remaining = toGo
    eve = {'title':event.title,"description":event.description,"user":event.user,"date":event.date,'raised':sumAmt,"goal":event.goal,"pk":event.pk,"image":event.image,"toGo":remaining,"hashtag":event.hashtag}

    if(request.user.username ==  event.user.username):
        selfPost = 1
    else:
        selfPost = 0
    return render(request,'eventView.html',{"event":eve,"donation":donation,"selfPost":selfPost})


#for donation
web3 = Web3(Web3.HTTPProvider(ganache_url))

import requests

def convert_to_ether(amount_in_rupees, conversion_rate=276483):
   
    ethereum_amount = amount_in_rupees / conversion_rate
    return ethereum_amount






def donate(request):
    user = User.objects.filter(username = request.user.username).first()
    print(user)
    post = Event.objects.filter(pk = request.POST.get('pk')).first()
    acc = Account.objects.filter(event = post).first()
    print("acc ::::::::: ",acc)
    #for getting account address


    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]

    test = w3.eth.contract(address=acc.transaction_address, abi=abi)
    print(test.functions.getEventDetails().call())

    result = test.functions.getEventDetails().call()
    

    profile = userProfile.objects.filter(user = user).first()
    to_user = User.objects.filter(username = request.POST.get('username')).first()
    to_user_profile = userProfile.objects.filter(user = post.user).first()

    account_1 = profile.account_address
    account_2 = to_user_profile.account_address

    private_key = profile.private_key #private key stored in user profile

    nonce  = web3.eth.getTransactionCount(account_1)
    ethereum_amount = convert_to_ether(int(request.POST.get('amount')))
    print("Amount in Ethereum: ", ethereum_amount)

    tx = {
        'nonce':nonce,
        'to':account_2,
        'value':web3.toWei(ethereum_amount,'ether'),
        'gas':2000000, 
        'gasPrice':web3.toWei(50,'gwei')
    }


    print(web3.fromWei(web3.eth.get_balance(account_1),'ether'))

    signed_tx = web3.eth.account.signTransaction(tx,private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Transaction hash :::::::: ",tx_hash)


    user_donation = User.objects.filter(username = request.user.username).first()

    post = Event.objects.filter(pk = request.POST.get('pk')).first()
    upf = userProfile.objects.filter(user = user_donation).first()
    eventHost = userProfile.objects.filter(user = post.user).first()
    
    import datetime
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y at %I:%M %p")

  
    block = Donation.objects.create(user= user,transaction_address = str(tx_hash),event = post,to_user = post.user.username,toaddress = account_2,fromaddress = upf.account_address,amount = request.POST.get('amount'))

    
    return JsonResponse({"success":1})

def tracking(request,pk):
    event = Event.objects.filter(pk=pk).first()   #queries the Event model to retrieve an event object with the primary key (pk)
    donations = Donation.objects.filter(event = event,user = request.user) #queries the Donation model to retrieve donation objects associated with the retrieved event

    #for account address ------------------>>>>>>>>>>>>

    account = Account.objects.filter(event = event).first() #Account model to retrieve an account object associated with the event

    

    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)

    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0

    for donation in donations:
        
        
        
        
        amt_list = []
        try:
        
            #attempts to retrieve the user profile associated with the event's user
            userpro = userProfile.objects.filter(user = event.user).first()
            

            #donation_1 containing details of the donation, including the donor's username, recipient's username, amount, address, date, and associated image URL
            donation_1 = {'from_user':donation.user.username,"to_user":donation.to_user,"amount":int(donation.amount),"address":donation.toaddress,"date":donation.date,"image":userpro.image.url}
            acc = Account.objects.filter(event = donation.event).first()    
            if donation.sent:
                #donation_2 containing details of the donation, specifically for the recipient account, if the donation has been sent.
                donation_2 = {'from_user':donation.to_user,"to_user":acc.username,"address":acc.address,"date":donation.date,"amount":donation.amount}
            amt_list.append(donation_1)
            if donation.sent:
                amt_list.append(donation_2)
            amounts.append(amt_list)
        except:
            
            userpro = userProfile.objects.filter(user = event.user).first()
            donation_1 = {'from_user':donation.user.username,"to_user":donation.to_user,"amount":int(donation.amount),"address":donation.toaddress,"date":donation.date,"image":userpro.image.url}
            amt_list.append(donation_1)
            
            amounts.append(amt_list)

    print(amounts)
    
    return render(request,'tracking.html',{"amounts":amounts})


def blog(request):
    b = Blog.objects.all().order_by('-date')
    profile = userProfile.objects.filter(user = request.user).first()
    blogs = []
    for blog in b:
        user = userProfile.objects.filter(user = blog.username).first()
        bl = {"username":blog.username.username,"image":blog.image.url, "date":blog.date,"desc":blog.description,"profile":user.image.url,"title":blog.title}
        blogs.append(bl)
    return render(request,'blog.html',{"blogs":blogs,"profile":profile})



def charityDonation(request,pk):
    event = Event.objects.filter(pk=pk).first()
    donations = Donation.objects.filter(event = event)

    account = Account.objects.filter(event = event).first()

    

    bytecode1 = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi1 = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    for donation in donations:
        
        
        pic = userProfile.objects.filter(user = donation.user).first()
        amt = {'username':donation.user.username,"amount":donation.amount,"address":donation.fromaddress,"date":donation.date,"pk":donation.pk,"image":pic.image.url,"eventPk":event.pk,"sent":donation.sent}
        amounts.append(amt)
    print("[+] Amounts : -- ",amounts)
    return render(request,'charity.html',{"amounts":amounts})


def getDonationDetails(address):
    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
# print(compiled_sol)
    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    
        
    test = w3.eth.contract(address= address, abi=abi)
    result = test.functions.getDonationDetails().call()

    return result


def sendDonation(request):
    

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["DonationTracking"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["DonationTracking"]["metadata"])["output"]["abi"]

    from web3 import Web3


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337

    ContactList = w3.eth.contract(abi=abi, bytecode=bytecode)
    address = "0xb9F21C013EA140c79d66Fe4D2B82813c9bB049aC"
    private_key = "0xafe8675e8af7e4bd0c7380ead58f66b14d30eaa6c977f23b6505190c5489f3a8"
    nonce = w3.eth.getTransactionCount(address)

    
    donation = Donation.objects.filter(pk = request.POST.get('pk')).first()
    
    
    track = Track.objects.create(from_user = request.user.username,to_user = donation.to_user,transaction_address = str("transaction_receipt.contractAddress"),donation = donation)
    import datetime
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y at %I:%M %p")

    

    donation.sent = True 
    donation.save()
    

   #--------------For donating amount -----------------------


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]
    
    event = Event.objects.filter(pk = request.POST.get("event-pk")).first()
    acc = Account.objects.filter(event = event).first()

    test = w3.eth.contract(address=acc.transaction_address, abi=abi)
    print(test.functions.getEventDetails().call())

    result = test.functions.getEventDetails().call()
    # print("result of account ::::::::::: ",result[0][2])
    user = User.objects.filter(username = request.user.username).first()
    profile = userProfile.objects.filter(user = user).first()
    

    account_1 = profile.account_address
   

    private_key = profile.private_key #private key srored in user profile

    nonce  = web3.eth.getTransactionCount(account_1)
    ethereum_amount = convert_to_ether(int(request.POST.get('amount')))
    print("Amount in Ethereum: ", ethereum_amount)

    tx = {
        'nonce':nonce,
        'to':acc.address,
        'value':web3.toWei(ethereum_amount,'ether'),
        'gas':2000000, 
        'gasPrice':web3.toWei(50,'gwei')
    }


    print(web3.fromWei(web3.eth.get_balance(account_1),'ether'))

    signed_tx = web3.eth.account.signTransaction(tx,private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Transaction hash ::::::::  ------ ----- ----- ",tx_hash)

   
    


    return JsonResponse({"result":1})

def createBlog(request):

    blog = Blog.objects.create(title = request.POST.get('title'),description = request.POST.get('desc'),username = request.user,category = request.POST.get('category'),image = request.FILES['image'])

    return HttpResponseRedirect(reverse('blog'))
def preprocess_text(text):
    if isinstance(text, str):
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    elif isinstance(text, float):  
        text = str(text)  
    return text


loaded_model = tf.keras.models.load_model("sentiment_model.h5")
label_encoder = LabelEncoder()

label_encoder.classes_ = np.load('label_encoder_classes.npy', allow_pickle=True)

# Load tokenizer
tokenizer = Tokenizer()
tokenizer.word_index = np.load("tokenizer_word_index.npy", allow_pickle=True).item()



def addFeed(request):
    input_text = request.POST.get('comment')
    preprocessed_text = preprocess_text(input_text)
    model = tf.keras.models.load_model("sentiment_model.h5")

    input_sequence = tokenizer.texts_to_sequences([preprocessed_text])
    max_length = 100  
    input_sequence_padded = pad_sequences(input_sequence, maxlen=max_length, padding='post')

    
    prediction = model.predict(input_sequence_padded)

    
    predicted_label = np.argmax(prediction)

    
    predicted_sentiment = label_encoder.inverse_transform([predicted_label])[0]
    Feedback.objects.create(user = request.user,comment = request.POST.get('comment'),sentiment = predicted_sentiment)

    return HttpResponseRedirect(reverse('homepage'))

