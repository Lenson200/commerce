from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import ListingForm,CommentForm
from django.shortcuts import redirect
from .models import User,all_listings,Bid,WatchList,Comment
def index(request):
    listing_list = all_listings.objects.all()  # Correct variable name
    for listing in listing_list:  # Use listing_list here, not listings
        # Attach the latest bid to each listing
        listing.latest_bid = Bid.objects.filter(auction=listing).order_by('-creation_time').first()
    return render(request, "auctions/index.html", {"listing_list": listing_list})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # Redirect the user to the next URL if it exists
            next_url = request.GET.get('next')
            if next_url:
                # Check if next_url is a valid path
                return redirect(next_url)
            else:
                return redirect('index')  
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
    
# renders the listing creation form 
@login_required(login_url='login')
def create_new(request):
    form = ListingForm()
    
    if request.method == 'POST':
        form = ListingForm(request.POST)  
        if form.is_valid():
            auction = all_listings(user=request.user, **form.cleaned_data)
            auction.save()
            return redirect('index')  

    return render(request, "auctions/create.html", {'form': form})

#allows user to save the listing
def adding(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)

        if form.is_valid():
            auction = all_listings(user=request.user, **form.cleaned_data)
            auction.imageurl = auction.imageurl or ""  # Default to empty string if no image URL
            auction.save()
            
            # Create the initial bid using the starting bid amount
            starting_bid = auction.startingbid
            if starting_bid:  # Ensure starting bid is valid before creating a Bid
                bid = Bid(amount=starting_bid, user=request.user, auction=auction)
                bid.save()
            
            print("Auction Image URL:", auction.imageurl)
            return HttpResponseRedirect(reverse('index'))
        else:
            # If the form is not valid, re-render the page with errors
            return render(request, "auctions/create.html", {
                'form': form,
                'error': form.errors
            })
    else:
        form = ListingForm()  # Initialize a new form if the request method is not POST

    return render(request, "auctions/create.html", {'form': form})

#renders all listings  that are active
def listings(request, id):
    current = get_object_or_404(all_listings, pk=id)
    bids = Bid.objects.filter(auction=current)
    comments = Comment.objects.filter(auction=current)    
    # Handle the case where there are multiple bids
    bid = None
    if bids.exists():
        bid = bids.latest('creation_time')
    
    print("here:" + current.imageurl)
    return render(request, 'auctions/alllisting.html', {
        'auction': current,
        'user': request.user,
        'bid': bid,
        'comments':comments
    })

@login_required
def update_bid(request, id):
    auction = get_object_or_404(all_listings, id=id)
    
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('bid'))
        except (TypeError, ValueError):
            messages.error(request, 'Bid amount must be a valid number.')
            return redirect(reverse('listings', args=[id]))

        current_price = auction.currentprice
        starting_bid = auction.startingbid
        previous_bid = Bid.objects.filter(auction=auction).order_by('-creation_time').first()
        previous_bid_amount = previous_bid.amount if previous_bid else None
        
        # Validate bid amount
        if (previous_bid_amount and amount <= previous_bid_amount) or (amount < current_price and amount < starting_bid):
            messages.error(request, 'Bid must be greater than the previous bid, current price, or starting bid.')
            return redirect(reverse('listings', args=[id]))

        # Save valid bid
        bid, created = Bid.objects.get_or_create(user=request.user, auction=auction)
        bid.amount = amount
        bid.save()
        auction.bid_counter += 1
        auction.save()
        return redirect('index')
    return redirect('index')

@login_required(login_url='login')
def watchlist(request):
    watchlist_items = WatchList.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist_items})

@login_required(login_url='login')
def add_watch(request, id):
    auction = get_object_or_404(all_listings, id=id)
    watchlist, created = WatchList.objects.get_or_create(user=request.user, listing=auction)
    if created:
        return HttpResponseRedirect(reverse('index'))  
    return HttpResponseRedirect(reverse('index'))  

@login_required(login_url='login')
def unwatch(request, id):
    auction = get_object_or_404(all_listings, id=id)
    watchlist = WatchList.objects.filter(user=request.user, listing=auction).first()
    if watchlist:
        watchlist.delete()
    
    return HttpResponseRedirect(reverse('index'))

# @login_required(login_url='login')
# def unwatch(request, id):
#     auction = get_object_or_404(all_listings, id=id)
#     watchlist = WatchList.objects.filter(user=request.user).first()

#     if watchlist and auction in watchlist.watchlist_items.all():
#         watchlist.watchlist_items.remove(auction)
#         watchlist.watchlist_counter -= 1
#         watchlist.save()
#     # This lines checks for request source and redirects accordingly
#     if '/unwatch/' in request.path:
#         return HttpResponseRedirect(reverse('index'))
#     else:
#         return HttpResponseRedirect(reverse('watchlist'))
    
    
def add_comment(request, id):
    if not request.user.is_authenticated:
        return render(request, 'auctions/login.html', {
            'message': 'Must be logged in to be able to add or see comments!'
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

        return HttpResponseRedirect(reverse('listings', kwargs={'id': id}))
    else:
        current = get_object_or_404(all_listings, pk=id)
        bids = Bid.objects.filter(auction=current)
        bid = None
        if bids.exists():
            bid = bids.latest('creation_time')
        comments = Comment.objects.filter(auction=current)
        return render(request, 'auctions/alllisting.html', {
            'form': form,
            'auction': current,
            'user': request.user,
            'bid': bid,
            'id': id,
            'comments':comments 

        })
    
@login_required(login_url='login')
def closing_bid(request,id):
    auction=get_object_or_404(all_listings, id=id)
    if request.user == auction.user:
        if auction.active:
            highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
            if highest_bid:
                auction.active = False
                auction.winner = highest_bid.user.username
                auction.save()
                messages.success(request, f"The auction has been successfully closed. The winner is {auction.winner}.")
            else:
                messages.error(request, "Cannot close the auction as there are no bids yet.")
        else:
            messages.warning(request, "The auction is already closed.")
    else:
        messages.error(request, "You are not authorized to close this auction.")
    return HttpResponseRedirect(reverse('index'))
    

def category_list(request):
    categories = all_listings.objects.values_list('category', flat=True).distinct()
    return render(request, 'auctions/categories.html', {'categories': categories})

def category_detail(request, category):
    listings = all_listings.objects.filter(category__iexact=category, active=True)
    for listing in listings:
        # Get the latest bid for the current listing
        latest_bid = Bid.objects.filter(auction=listing).order_by('-creation_time').first()
        listing.latest_bid = latest_bid  
    
    return render(request, 'auctions/category_detail.html', {
        'category': category,
        'listings': listings
    })