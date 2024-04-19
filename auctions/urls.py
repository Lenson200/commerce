from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    
    path('create', views.create_new, name='create_new'),
    path("adding",views.adding,name='adding'),
    path("listings/<int:id>",views.listings,name='listings'),
    path("update_bid/<int:id>", views.update_bid, name='update_bid'), 
    path("watchlist", views.watchlist, name="watchlist"),
    path('watch/<int:id>', views.add_watch, name='add_watch'),
    path("unwatch/<int:id>", views.unwatch, name="unwatch"),
    path("comments/<int:id>", views.add_comment, name="add_comment")
]
