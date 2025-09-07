from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Product, CartItem
import json

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})

def cart_detail(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    cart_items = CartItem.objects.filter(session_key=session_key)
    total = sum(item.get_total_price() for item in cart_items)
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@csrf_exempt
@require_POST
def cart_add(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        session_key=session_key,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    cart_count = CartItem.objects.filter(session_key=session_key).count()
    
    return JsonResponse({
        'success': True,
        'cart_count': cart_count,
        'message': f'{product.name} added to cart!'
    })

@csrf_exempt
@require_POST
def cart_remove(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')
    
    session_key = request.session.session_key
    if session_key:
        CartItem.objects.filter(id=item_id, session_key=session_key).delete()
    
    return JsonResponse({'success': True})

def get_cart_count(request):
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'count': 0})
    
    count = CartItem.objects.filter(session_key=session_key).count()
    return JsonResponse({'count': count})