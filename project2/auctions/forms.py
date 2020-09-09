from django import forms
from auctions.models import AuctionListening


class NewAuctionForm(forms.ModelForm):
    class Meta:
        model = AuctionListening
        fields = ['title', 'description', 'category', 'image_url', 'starting_bid']