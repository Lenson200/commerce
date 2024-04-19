from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render,get_object_or_404

from django.urls import reverse
from .forms import ListingForm,CommentForm

from .models import User,all_listings,Bid,WatchList,Comment



def index(request):
    listing_list = all_listings.objects.all()
    return render(request, "auctions/index.html", {"listing_list": listing_list})

from django.shortcuts import redirect

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # Redirect the user to the next URL if it exists
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')  # Redirect to index if next URL is not provided
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "next": request.GET.get("next"),
            })
    else:
        return render(request, "auctions/login.html", {"next": request.GET.get("next")})


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
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

@login_required(login_url='auctions/login.html')
def create_new(request):
    form=ListingForm()
    if request.method=='POST':
        form=ListingForm(request.POST)
    return render(request,"auctions/create.html",{'form':form})

@login_required(login_url='auctions/login.html')
def adding(request):
    form=ListingForm(request.POST)
    if form.is_valid():
        auction=all_listings(user=request.user,**form.cleaned_data)
        if not auction.imageurl:
            auction.imageurl=""
        auction.save()
        startingbid=auction.startingbid
        bid=Bid(amount=startingbid,user=request.user,auction=auction)
        bid.save()
        print("auction:"+auction.imageurl)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request,"auctions/create.html",{
            'form':form,
            'error':form.errors
        })
    

def listings(request, id):
    current = get_object_or_404(all_listings, pk=id)
    bids = Bid.objects.filter(auction=current)
    
    # Handle the case where there are multiple bids
    bid = None
    if bids.exists():
        bid = bids.latest('creation_time')
    
    print("here:" + current.imageurl)
    return render(request, 'auctions/alllisting.html', {
        'auction': current,
        'user': request.user,
        'bid': bid
    })

def update_bid(request, id):
    auction = get_object_or_404(all_listings, id=id)
    
    if request.method == 'POST':
        amount = request.POST.get('bid')
        
        if amount:
            amount = int(amount)
            current_price = auction.currentprice
            starting_bid = auction.startingbid
            
            # Get the previous bid amount if it exists
            previous_bid_amount = None
            previous_bids = Bid.objects.filter(auction=auction).order_by('-creation_time')
            if previous_bids.exists():
                previous_bid = previous_bids.first()
                previous_bid_amount = previous_bid.amount
            # Handling the case where there are no previous bids
            if previous_bid_amount is None or amount > previous_bid_amount:
                if amount > current_price or (starting_bid and amount >= starting_bid):
                    bid, created = Bid.objects.get_or_create(user=request.user, auction=auction)
                    bid.amount = amount
                    bid.save() 
                    auction.bid_counter += 1
                    auction.save()
                    return HttpResponseRedirect(reverse('index'))
                else:
                    raise ValidationError('Bid must be greater than the previous bid amount')
            else:
                raise ValidationError('Bid must be greater than or equal to the current price or starting bid')
        else:
            raise ValidationError('Bid amount is required')
    else:
        return HttpResponseRedirect(reverse('index'))

@login_required(login_url='auctions/login.html')
def watchlist(request):
    # Fetch the watchlist items for the current user
    try:
        watchlist = WatchList.objects.get(user=request.user)
        watchlist_items = watchlist.watchlist_items.all()
        current_price=all_listings.currentprice
        # print("Watchlist items:", watchlist_items) 
    except WatchList.DoesNotExist:
        watchlist_items = []

    return render(request, "auctions/watchlist.html", {"watchlist": watchlist_items})
  
@login_required(login_url='auctions/login.html')
def add_watch(request, id):
    auction = get_object_or_404(all_listings, id=id)
    watchlist, created = WatchList.objects.get_or_create(user=request.user)   
    if auction in watchlist.watchlist_items.all():
        return HttpResponseRedirect(reverse('index'))
    watchlist.watchlist_items.add(auction)
    watchlist.watchlist_counter += 1
    watchlist.save()  
    return HttpResponseRedirect(reverse('index')) 

@login_required(login_url='auctions/login.html')
def unwatch(request, id):
    auction = get_object_or_404(all_listings, id=id)
    watchlist = WatchList.objects.filter(user=request.user).first()
    if watchlist:
        watchlist.watchlist_items.remove(auction)
        watchlist.watchlist_counter -= 1
        watchlist.save()
    if '/unwatch/' in request.path:
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('watchlist'))
    
def add_comment(request, id):
    if not request.user.is_authenticated:
        return render(request, 'auctions/login.html', {
            'message': 'Must be logged in to be able to comment!'
        })

    form = CommentForm(request.POST)
    if form.is_valid():
        f = form.cleaned_data
        comment = Comment(
            user=request.user,
            auction=get_object_or_404(all_listings, pk=id),
            **f
        )
        comment.save()
        # Redirect to the details page of the auction (listings page)
        return HttpResponseRedirect(reverse('listings', kwargs={'id': id}))
    else:
        # Render the form with errors
        current = get_object_or_404(all_listings, pk=id)
        bids = Bid.objects.filter(auction=current)
        bid = None
        if bids.exists():
            bid = bids.latest('creation_time')
        return render(request, 'auctions/alllisting.html', {
            'form': form,
            'auction': current,
            'user': request.user,
            'bid': bid,
            'id': id
        })
# def closing_bid(request,id):
#     auction=get_object_or_404(all_listings, id=id)
#     auction.active,auction.winner = False, request.user.username
#     auction.save()
#     return HttpResponseRedirect(reverse('index'))
