from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.db.models import Max
from django.views import View
from django.contrib import messages

from .models import User, AuctionListening, Bid, Category
from .forms import NewAuctionForm, BidForm, CommentForm

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
    favoured = request.user in auction.favoured.all()

    print(request.method)

    try:
        top_bid = auction.bid_set.all().order_by("-amount")[0]
    except:
        top_bid = None

    if request.method == "POST":
        # new bid was submitted
        if 'bid' in request.POST:
            bid_form = BidForm(request.POST, auction=auction)
            if bid_form.is_valid() and request.user.is_authenticated:
                temp = bid_form.save(commit=False)
                temp.user = request.user
                temp.auction = auction
                temp.save()
                auction.current_price = temp.amount
                auction.save()
                return redirect(auction_view, pk=auction.pk)

        # new comment was submitted
        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid() and request.user.is_authenticated:
                temp = comment_form.save(commit=False)
                temp.user = request.user
                temp.auction = auction
                temp.save()
                return redirect(auction_view, pk=auction.pk)

    else:
        minimum_bid = auction.current_price + Decimal(0.01).quantize(Decimal('1.00'))
        bid_form = BidForm(initial={"amount": minimum_bid}, auction=auction)
        comment_form = CommentForm()

    return render(request, "auctions/auction_view.html", {
        "auction": auction,
        "bid_form": bid_form,
        "favoured": favoured,
        "top_bid": top_bid,
        "comment_form": comment_form,
        "comments": auction.comments.all()
    })


def favourite_post(request, pk):
    # check if that auction is favoured by user or not
    if request.user.is_authenticated:
        auction = AuctionListening.objects.get(pk=pk)
        if request.user in auction.favoured.all():
            # User already favoured, unfavourite auction
            auction.favoured.remove(request.user)
        else:
            # add auction to favourites
            auction.favoured.add(request.user)
    return HttpResponseRedirect(reverse("auction_view", args=[pk]))


def end_auction(request, pk):
    auction = AuctionListening.objects.get(pk=pk)
    if request.user.is_authenticated and auction.user == request.user:
        # user is authenticated, and owner of that auction
        auction.active = False
        auction.save()

    return HttpResponseRedirect(reverse("auction_view", args=[pk]))


@login_required
def bookmarks(request):
    bkmrk = request.user.user_favoured.all()
    return render(request, "auctions/bookmarks.html",
                  {"bookmarks": bkmrk}
                  )


class CategoriesView(ListView):
    template_name = "auctions/categories.html"
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CategoryListings(ListView):
    template_name = "auctions/category_listings.html"
    model = AuctionListening

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.kwargs["slug"].title()
        return context

    def get_queryset(self):
        return AuctionListening.objects.filter(category__slug=self.kwargs["slug"], active=True)