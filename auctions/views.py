from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Watchlist, Bids, Comments

class CreateListingForm(forms.Form):
    create_title = forms.CharField(label="Item Title", max_length=50)
    create_description = forms.CharField(label="Item Description", max_length=1000, widget=forms.Textarea)
    create_size = forms.CharField(label="Item Size (Number or Letters)", max_length=10, required=False)
    create_price = forms.IntegerField(label="Starting Price in USD ($)", max_value=32767, min_value=0)
    choose_gender = forms.ChoiceField(label="Select Gender", choices=Listing.GENDER_CHOICES, required=False)
    choose_category = forms.ChoiceField(label="Choose Clothing Category", choices=Listing.CATEGORY_CHOICES, required=False)
    create_picture = forms.URLField(label="Link to a Photo", max_length=500, initial="https://images.unsplash.com/photo-1517502166878-35c93a0072f0?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=934&q=80", required=False)

class CreateCommentForm(forms.Form):
    create_comment = forms.CharField(label="Post a Comment", max_length=500, widget=forms.Textarea)

def index(request):
    return render(request, "auctions/index.html", {
        "active_items": Listing.objects.filter(active=True),
        "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
        "total_items": len(Listing.objects.filter(user_id=request.user.id)),
        "genders": Listing.GENDER_CHOICES,
        "categories": Listing.CATEGORY_CHOICES
    })

def landing_page(request):
    return render(request, "auctions/landing.html", {
        "genders": Listing.GENDER_CHOICES,
        "categories": Listing.CATEGORY_CHOICES
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "error_message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "username": username,
                "email": email,
                "password": password,
                "passwords_unmatched": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "username": username,
                "email": email,
                "password": password,
                "confirmation": confirmation,
                "user_taken": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing_page(request, itemid):
    # Handle four different forms submissions
    if request.method == "POST":
        # User adds listing to Watchlist
        if "watch" in request.POST:
            # If entry for listing and user exists, then update existing entry
            try:
                watchlist = Watchlist.objects.get(user_id=request.user.id, listing_id=itemid)
                watchlist.active = True
                watchlist.save(update_fields=["active"])
                return HttpResponseRedirect(reverse("listing", args=(itemid,)))
            # If no entry for listing and user, then create new entry
            except:
                watchlist = Watchlist(user_id=request.user.id, listing_id=itemid, active=True)
                watchlist.save()
                return HttpResponseRedirect(reverse("listing", args=(itemid,)))
        # User removes listing from Watchlist
        if "unwatch" in request.POST:
            watchlist = Watchlist.objects.get(user_id=request.user.id, listing_id=itemid)
            watchlist.active = False
            watchlist.save(update_fields=["active"])
            return HttpResponseRedirect(reverse("listing", args=(itemid,)))
        # Buyer bids on auction
        if "bid" in request.POST:
            listing = Listing.objects.get(pk=itemid)
            price = listing.price
            bid = int(request.POST.get("amount"))
            try:
                highest = Bids(user_id=request.user.id, listing_id=itemid).last()
            except:
                highest = 0
            if bid < price and bid < highest:
                return render(request, "auctions/listing.html", {
                    "error_message": "Bidding price must be greater than current price"
                })
            else:
                bids = Bids(user_id=request.user.id, listing_id=itemid, offer=bid)
                bids.save()
                highestbid = Listing.objects.get(pk=itemid)
                highestbid.highestbid = bid
                highestbid.save(update_fields=["highestbid"])
                return HttpResponseRedirect(reverse("listing", args=(itemid,)))
        # Seller closes an auction
        if "close" in request.POST:
            listing = Listing.objects.get(pk=itemid)
            listing.active = False
            listing.save(update_fields=["active"])
            return HttpResponseRedirect(reverse("inventory"))
        # User posts comment
        if "comment" in request.POST:
            input = CreateCommentForm(request.POST)
            if input.is_valid():
                comment = Comments(user=request.user, comment=(input.cleaned_data["create_comment"]), timestamp=timezone.now(), listing=Listing(pk=itemid))
                comment.save()
                return HttpResponseRedirect(reverse("listing", args=(itemid,)))
            else:
                return render(request, "auctions/listing.html", {
                    "comment_form": input,
                    "error_message": "Sorry, the form was not valid"
                })
    else:
        try:
            watching = Watchlist.objects.get(user_id=request.user.id, listing_id=itemid)
        except:
            watching = None
        try:
            bids = Bids.objects.filter(listing_id=itemid)
        except:
            bids = None
        try:
            listing = Listing.objects.get(pk=itemid)
            winner = Bids.objects.filter(listing_id=itemid).last()
        except:
            winner = None
        return render(request, "auctions/listing.html", {
            "listing": Listing.objects.get(pk=itemid),
            "watching": watching,
            "total_bids": len(bids),
            "bid": bids,
            "winner": winner,
            "comments": Comments.objects.filter(listing_id=itemid),
            "comment_form": CreateCommentForm(),
            "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
            "total_items": len(Listing.objects.filter(user_id=request.user.id)),
            "genders": Listing.GENDER_CHOICES,
            "categories": Listing.CATEGORY_CHOICES
        })

@login_required
def create_page(request):
    if request.method == "POST":
        input = CreateListingForm(request.POST)
        if input.is_valid():
            title = (input.cleaned_data["create_title"])
            description = (input.cleaned_data["create_description"])
            size = (input.cleaned_data["create_size"])
            price = (input.cleaned_data["create_price"])
            highestbid = (input.cleaned_data["create_price"])
            gender = (input.cleaned_data["choose_gender"])
            category = (input.cleaned_data["choose_category"])
            picture = (input.cleaned_data["create_picture"])
            user = request.user
            l = Listing(user=user, title=title, description=description, size=size, price=price, highestbid=highestbid, gender=gender, category=category, photo_url=picture, timestamp=timezone.now())
            l.save()
            return HttpResponseRedirect(reverse("inventory"))
        else:
            return render(request, "auctions/create.html", {
                "create_form": input,
                "error_message": "Sorry, the form was not valid"
            })
    else:
        return render(request, "auctions/create.html", {
            "create_form": CreateListingForm(),
            "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
            "total_items": len(Listing.objects.filter(user_id=request.user.id)),
            "genders": Listing.GENDER_CHOICES,
            "categories": Listing.CATEGORY_CHOICES
        })

@login_required
def bids_page(request):
    return render(request, "auctions/bids.html", {
        "bids": Bids.objects.filter(user_id=request.user.id),
        "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
        "total_items": len(Listing.objects.filter(user_id=request.user.id)),
        "genders": Listing.GENDER_CHOICES,
        "categories": Listing.CATEGORY_CHOICES
    })

@login_required
def inventory_page(request):
    return render(request, "auctions/inventory.html", {
        "inventory": Listing.objects.filter(user=request.user),
        "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
        "total_items": len(Listing.objects.filter(user_id=request.user.id)),
        "genders": Listing.GENDER_CHOICES,
        "categories": Listing.CATEGORY_CHOICES
    })
    
@login_required
def watchlist_page(request):
    try:
        watchlist = Watchlist.objects.filter(user_id=request.user.id).values_list("listing_id")
        watching = Listing.objects.filter(id__in = watchlist)
    except:
        watching = 0
    return render(request, "auctions/watchlist.html", {
        "watching": watching,
        "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
        "total_items": len(Listing.objects.filter(user_id=request.user.id)),
        "genders": Listing.GENDER_CHOICES,
        "categories": Listing.CATEGORY_CHOICES
    })

def category_page(request, selection):
    try:
        category = Listing.objects.filter(category=selection, active=True)
    except:
        category = None
    try:
        gender = Listing.objects.filter(gender=selection, active=True)
    except:
        gender = None
    return render(request, "auctions/category.html", {
        "selection": selection,
        "category": category,
        "gender": gender,
        "watchlist": len(Watchlist.objects.filter(user_id=request.user.id)),
        "total_items": len(Listing.objects.filter(user_id=request.user.id)),
        "genders": Listing.GENDER_CHOICES,
        "categories": Listing.CATEGORY_CHOICES
        })