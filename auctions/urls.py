from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("landing", views.landing_page, name="landing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:itemid>", views.listing_page, name="listing"),
    path("category/<str:selection>", views.category_page, name="category"),
    path("add-listing", views.create_page, name="create"),
    path("my-listings", views.inventory_page, name="inventory"),
    path("my-bids", views.bids_page, name="bids"),
    path("my-watchlist", views.watchlist_page, name="watchlist")
]