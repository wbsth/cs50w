from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views import View
from django.contrib import messages

from .models import User, AuctionListening
from .forms import NewAuctionForm, BidForm

from decimal import Decimal


class IndexListView(ListView):
    model = AuctionListening
    template_name = "auctions/index.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
                "message": "Invalid username and/or password."
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


@login_required
def new_auction(request):
    if request.method == "POST":
        form = NewAuctionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = NewAuctionForm()

    return render(request, "auctions/new_auction.html", {
        "form": form
    })


def auction_view(request, pk):
    auction = get_object_or_404(AuctionListening, pk=pk)
    if request.method == "POST":
        bid_form = BidForm(request.POST, auction=auction)
        if bid_form.is_valid() and request.user.is_authenticated:
            temp = bid_form.save(commit=False)
            temp.user = request.user
            temp.auction = auction
            temp.save()
            auction.current_price = temp.amount
            auction.save()
    else:
        minimum_bid = auction.current_price + Decimal(0.01).quantize(Decimal('1.00'))
        bid_form = BidForm(initial={
            "amount": minimum_bid
        },
            auction=auction)

    return render(request, "auctions/auction_view.html", {
        "auction": auction,
        "bid_form": bid_form
    })
