from django.contrib import admin
from .models import all_listings, Bid, Comment
# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction', 'text', 'created_at') 
    search_fields = ('user__username', 'auction__title', 'text') 
    list_filter = ('created_at', 'auction')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction', 'amount', 'creation_time')  
    search_fields = ('user__username', 'auction__title')  
    list_filter = ('creation_time', 'auction')  

@admin.register(all_listings)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'startingbid', 'currentprice', 'category', 'active', 'creation_time')  
    search_fields = ('title', 'category') 
    list_filter = ('category', 'creation_time', 'active')  
    prepopulated_fields = {"title": ("title",)}  

    # Inline for comments and bids related to listings
    class CommentInline(admin.TabularInline):
        model = Comment
        extra = 1  # Number of empty forms to display

    class BidInline(admin.TabularInline):
        model = Bid
        extra = 1  # Number of empty forms to display

    # Add inlines to ListingAdmin
    inlines = [CommentInline, BidInline]