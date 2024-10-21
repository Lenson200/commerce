from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import ListingForm,CommentForm
from django.shortcuts import redirect
from .models import User,all_listings,Bid,WatchList,Comment

def index(request):
    listing_list = all_listings.objects.all()
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
                return redirect('index')  # Default redirect if next URL is not provided
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
    

@login_required(login_url='login')
def create_new(request):
    form=ListingForm()
    if request.method=='POST':
        form=ListingForm(request.POST)
    return render(request,"auctions/create.html",{'form':form})

@login_required(login_url='login')
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

def update_bid(request, id):
    auction = get_object_or_404(all_listings, id=id)
    if request.method == 'POST':
        amount = request.POST.get('bid') 
        if amount:
            try:
                amount = int(amount)
            except ValueError:
                messages.error(request, 'Bid amount must be greater than current bid amount. Please try again with different amount.')
                return redirect(reverse('listings', args=[id]))  # Redirect to the bidding page
            current_price = auction.currentprice
            starting_bid = auction.startingbid
            
            # Get the previous bid amount if it exists
            previous_bid_amount = None
            previous_bids = Bid.objects.filter(auction=auction).order_by('-creation_time')
            if previous_bids.exists():
                previous_bid = previous_bids.first()
                previous_bid_amount = previous_bid.amount
            
            try:
                # Ensure the bid is valid
                if previous_bid_amount is None or amount > previous_bid_amount:
                    if amount >= current_price or (starting_bid and amount >= starting_bid):
                        bid, created = Bid.objects.get_or_create(user=request.user, auction=auction)
                        bid.amount = amount
                        bid.save() 
                        auction.bid_counter += 1
                        auction.save()
                        return HttpResponseRedirect(reverse('index'))
                    else:
                        raise ValidationError('Bid must be greater than  the current price or starting bid')
                else:
                    raise ValidationError('Bid must be greater than the previous bid amount')
            except ValidationError as e:
                messages.error(request, str(e) + 'Please try again with different amount')
                return redirect(reverse('listings', args=[id]))
        else:
            messages.error(request, 'Bid amount is required. Please try again with different amount')
            return redirect(reverse('listings', args=[id]))  # Redirect to the bidding page

    return redirect('index')

@login_required(login_url='login')
def watchlist(request):
    
    try:
        watchlist = WatchList.objects.get(user=request.user)
        watchlist_items = watchlist.watchlist_items.all()
        current_price=all_listings.currentprice
    except WatchList.DoesNotExist:
        watchlist_items = []

    return render(request, "auctions/watchlist.html", {"watchlist": watchlist_items})
  
@login_required(login_url='login')
def add_watch(request, id):
    auction = get_object_or_404(all_listings, id=id)
    watchlist, created = WatchList.objects.get_or_create(user=request.user)   
    if auction in watchlist.watchlist_items.all():
        return HttpResponseRedirect(reverse('index'))
    watchlist.watchlist_items.add(auction)
    watchlist.watchlist_counter += 1
    watchlist.save()  
    return HttpResponseRedirect(reverse('index')) 

@login_required(login_url='login')
def unwatch(request, id):
    auction = get_object_or_404(all_listings, id=id)
    watchlist = WatchList.objects.filter(user=request.user).first()
    if watchlist:
        watchlist.watchlist_items.remove(auction)
        watchlist.watchlist_counter -= 1
        watchlist.save()
    if '/unwatch/' in request:
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('watchlist'))
    
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

    # Attach the latest bid to each listing
    for listing in listings:
        # Get the latest bid for the current listing
        latest_bid = Bid.objects.filter(auction=listing).order_by('-creation_time').first()
        listing.latest_bid = latest_bid  # Attach the latest bid to the listing
    
    return render(request, 'auctions/category_detail.html', {
        'category': category,
        'listings': listings
    })