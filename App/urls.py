from django.urls import path
from . import views 
# from django.conf.urls import url

urlpatterns = [
    
    path('',views.homepage,name = "homepage"),
    path('register/', views.register,name='register' ),
    path('registercharity/', views.registercharity,name='registercharity' ),
    path('login/', views.user_login, name='login'),
    path('checkLogin/', views.checkLogin, name = "checkLogin"),
    path('checkSignup/', views.checkSignup,name = 'checkSignup'),
    path('logout/', views.user_logout,name = 'logout'),
    path('donation/', views.donations,name = 'donation'),
    path('createEvent/', views.createEvent,name = 'createEvent'),
    path('eventView/<int:pk>', views.eventView,name = 'eventView'),
    path('donate/', views.donate,name = 'donate'),
    path('tracking/<int:pk>', views.tracking,name = 'tracking'),
    path('blog/', views.blog,name = 'blog'),
    path('charityDonation/<int:pk>', views.charityDonation,name = 'charityDonation'),
    path('sendDonation/', views.sendDonation,name = 'sendDonation'),
    path('createBlog/', views.createBlog,name = 'createBlog'),
    path('addFeed/', views.addFeed,name = 'addFeed'),
    
]