from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class userProfile(models.Model):

    account_type = models.CharField(blank=True,max_length=5000) 
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    
    image = models.ImageField(upload_to='profile_pic',default='sherlock.jpg')
    phone = models.CharField(max_length=500,blank=True)
    address = models.CharField(max_length=5000,blank=True)
    account_address = models.CharField(max_length=50000)
    private_key = models.CharField(max_length=50000,default="")

    organization_name = models.CharField(max_length=50000,default = "",blank=True)
    organization_phone = models.IntegerField(default = 0,blank=True)
    organization_address = models.CharField(max_length=5000,default = "",blank=True)
    
    is_an_organization = models.BooleanField(default = False,blank=True)

    def __str__(self):
        return self.user.username + " profile"


class Event(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    
    image = models.ImageField(upload_to='events',default='sherlock.jpg')
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=5000)
    approved = models.BooleanField(default = False)
    title = models.CharField(max_length=5000)
    description = models.CharField(max_length=5000)
    hashtag = models.CharField(max_length=5000)
    goal = models.IntegerField(default = 0)
    raised = models.IntegerField(default = 0)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username + " Event"
    

class Donation(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    transaction_address = models.CharField(max_length=50000)
    date = models.DateTimeField(auto_now_add=True)
    to_user = models.CharField(max_length=5000,blank=True,default="")
    sent = models.BooleanField(default=False)
    toaddress =  models.CharField(max_length=5000,blank=True,default="") 
    fromaddress =  models.CharField(max_length=5000,blank=True,default="") 
    amount =  models.IntegerField(default = 0) 
    def __str__(self):
        return "Donation"
    
class Account(models.Model):

    username = models.CharField(max_length=50000)
    charityName = models.CharField(max_length=50000)
    transaction_address = models.CharField(max_length=50000)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    address = models.CharField(max_length=50000)
    
    def __str__(self):
        return "Account"
    

class Blog(models.Model):

    username = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=5000)
    description = models.CharField(max_length=5000)
    category = models.CharField(max_length=50000)
    image = models.ImageField(upload_to='blog',default='sherlock.jpg')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "Blog"
    
class Track(models.Model):
    from_user = models.CharField(max_length=5000,blank = True)
    to_user = models.CharField(max_length=5000,blank = True)
    donation = models.ForeignKey(Donation,on_delete=models.CASCADE)
    transaction_address = models.CharField(max_length=50000)

    def __str__(self):
        return "Tracking"
    

class Product(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=5000)
    description = models.CharField(max_length=5000)
    category = models.CharField(max_length=50000)
    image = models.ImageField(upload_to='products',default='sherlock.jpg')
    date = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(default=0)
    address = models.CharField(max_length=50000,default="")
    added_by_organization = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Blood(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    firstname = models.CharField(max_length=5000)
    lasname = models.CharField(max_length=5000)
    type = models.CharField(max_length=50000)
    date = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(default=0)
    address = models.CharField(max_length=50000,default="")
    gender = models.CharField(max_length=1500,default="")
    
    def __str__(self):
        return self.user.username + " form"
    

class Feedback(models.Model):
    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    
    sentiment = models.CharField(max_length=500)
    date= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + "'s feedback"  