from django.shortcuts import render, redirect, get_object_or_404
#from kabi2026.models import admin
from kabi2026.models import *
from kabi2026.models import Wallet
from django.contrib import messages
from django.db.models import Sum
import json
from django.db.models import Max
from collections import Counter
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from .models import ProductReview
from django.db.models import Count, Avg, Q

def user_home(request):
    search = request.GET.get('search')
    category = request.GET.get('category')
    data = Items.objects.all()
    if search:
        if search.isdigit():
            data = data.filter(new_price__lte=int(search))
        else:
            data = data.filter(toy_name__icontains=search)
    if category:
        data = data.filter(category=category)
    return render(request, 'user_home.html', {'data': data,'search_value': search})


def user_login(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        password = request.POST.get("password")
        data = KYC.objects.filter(user_name=user_name, confirm_password=password).first()
        if data:
            request.session['user_id'] = data.id
            return redirect("user_home")
        else:
            messages.error(request, "Invalid login")
    return render(request, "user_login.html")

def logout_user(request):
    request.session.flush()
    response = redirect('http://127.0.0.1:8000/')
    response.delete_cookie('sessionid')
    return response
from functools import wraps
def admin_login_required(view_func):    
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            messages.error(request,"LOGIN MUST")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_login(request):
    if request.session.get('admin_id'):
        return redirect('admin_home')
    if request.method == "POST":
        admin_name = request.POST.get("admin_name")
        password = request.POST.get("password")        
        admin_user = Admin.objects.filter(admin_name=admin_name, password=password).first()
        
        if admin_user:
            request.session['admin_id'] = admin_user.id 
            request.session['admin_name'] = admin_user.admin_name
            return redirect('admin_home') 
        else:
            messages.error(request, "name or password is wrong")
            return render(request, 'admin_login.html')            
            
    return render(request, 'admin_login.html')


def admin_logout(request):
    if 'admin_id' in request.session:
        request.session.flush() 
        
    messages.success(request, "Successfully logged out!")
    return redirect('user_home')

def view_user_personal_by_user(request,id):
    data = KYC.objects.get(id=id)
    return render(request,'view_user_personal_by_user.html',{'data':data})

def update_user_personal(request,id):
    data = KYC.objects.get(id=id)
    if request.method == "POST":
        data.user_name = request.POST.get('user_name')
        data.address = request.POST.get('address')
        data.district = request.POST.get('district')
        data.state = request.POST.get('state')
        data.phone_number = request.POST.get('phone_number')
        data.save()
        return redirect('view_user_personal_by_user', id=data.id)

    return render(request,'update_user_personal_by_user.html',{'data':data})

@admin_login_required
def admin_page(request):
    if request.method == "POST":
        item = Items.objects.create(
            toy_name=request.POST["toy_name"],
            photo=request.FILES.getlist("photo")[0],   # first image main image
            order_qty=request.POST["qty"],
            old_price=request.POST["old_price"],
            new_price=request.POST["new_price"],
            offer=request.POST["offer"],
            discription=request.POST["discription"],
            category=request.POST["category"]
        )
        images = request.FILES.getlist("photo")

        # Save all images in ItemImages table
        for img in images:
            ItemImages.objects.create(
                item=item,
                image=img
            )
    return render(request, "admin_input_upload.html")

@admin_login_required
def admin_home(request):
    # 1. செயலில் உள்ள அரட்டைகளை எடுத்தல்
    active_chats = ChatMessage.objects.filter(sender='user').values('user_id', 'product_id').annotate(
        latest_msg=Max('created_at')
    ).order_by('-latest_msg')
    
    chat_data = []
    for chat in active_chats:
        try:
            product = Items.objects.get(id=chat['product_id'])
            user_identifier = f"User #{chat['user_id']}"
            chat_data.append({
                'product': product,
                'user_id': chat['user_id'],
                'user_name': user_identifier
            })
        except Items.DoesNotExist:
            continue

    # 2. அனைத்துப் பொருட்களையும் எடுத்தல் (Inventory)
    data = Items.objects.all()

    # 3. ORDERS அட்டவணையை அடிப்படையாகக் கொண்ட வரைபட மற்றும் கணக்கீட்டுத் தரவுகள்
    orders = Orders.objects.all().order_by("created_at")
    total_orders = orders.count()
    total_revenue = 0
    daily_sales = {}
    products = []

    for i in orders:
        try:
            price = int(i.price)
        except:
            price = 0

        total_revenue += price
        
        # வரைபடத்திற்கான தேதியை வடிவமைத்தல்
        day = i.created_at.strftime("%d-%m-%Y") if i.created_at else "Unknown"
        if day not in daily_sales:
            daily_sales[day] = 0
        daily_sales[day] += price

        if i.product_name:
            products.append(i.product_name)

    labels = list(daily_sales.keys())
    sales_data = list(daily_sales.values())

    most_sold = "No Orders"
    if products:
        most_sold = Counter(products).most_common(1)[0][0]

    # அனைத்துத் தரவுகளையும் ஒரே பக்கத்திற்கு அனுப்புதல்
    context = {
        'chat_data': chat_data, 
        'data': data,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "most_sold": most_sold,
        "labels": json.dumps(labels),
        "sales_data": json.dumps(sales_data),
    }

    return render(request, 'admin_home.html', context)

def view_item(request,id):
    data = Items.objects.get(id=id)
    images = ItemImages.objects.filter(item=data)
    return render(request,'view_item.html',{'data':data,'images':images})

def view_toys_by_category(request, category_name):
    data = Items.objects.filter(category=category_name)
    return render(request, 'user_home.html', {'data': data, 'category': category_name})

@admin_login_required
def view_toys_by_category_admin(request, category_name):
    data = Items.objects.filter(category=category_name)
    orders = Orders.objects.all().order_by("created_at")
    total_orders = orders.count()
    total_revenue = 0
    daily_sales = {}
    products = []

    for i in orders:
        try:
            price = int(i.price)
        except:
            price = 0

        total_revenue += price
        
        day = i.created_at.strftime("%d-%m-%Y") if i.created_at else "Unknown"
        if day not in daily_sales:
            daily_sales[day] = 0
        daily_sales[day] += price

        if i.product_name:
            products.append(i.product_name)

    labels = list(daily_sales.keys())
    sales_data = list(daily_sales.values())

    most_sold = "No Orders"
    if products:
        most_sold = Counter(products).most_common(1)[0][0]

    # 3. அரட்டைத் தரவுகள் (Chat Data)
    active_chats = ChatMessage.objects.filter(sender='user').values('user_id', 'product_id').annotate(
        latest_msg=Max('created_at')
    ).order_by('-latest_msg')
    
    chat_data = []
    for chat in active_chats:
        try:
            product = Items.objects.get(id=chat['product_id'])
            user_identifier = f"User #{chat['user_id']}"
            chat_data.append({
                'product': product,
                'user_id': chat['user_id'],
                'user_name': user_identifier
            })
        except Items.DoesNotExist:
            continue

    context = {
        'chat_data': chat_data, 
        'data': data, 
        'category': category_name,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "most_sold": most_sold,
        "labels": json.dumps(labels),
        "sales_data": json.dumps(sales_data),
    }
    return render(request, 'admin_home.html', context)

@admin_login_required
def view_item_by_admin(request,id):
    data = Items.objects.get(id=id)
    return render (request,'view_item_by_admin.html',{'data':data})

@admin_login_required
def view_users_by_admin(request):
    data = KYC.objects.all()
    return render (request,'users_list.html',{'data':data})

def order_input_get_from_user(request, id):
    if not request.session.get('user_id'):
        return redirect('user_login')

    user_id = request.session['user_id']
    data = get_object_or_404(Items, id=id)
    
    wallet = Wallet.objects.filter(user_id=user_id).first()
    wallet_balance = float(wallet.balance) if wallet else 0.0

    if request.method == "POST":
        qty = int(request.POST.get('quantity'))
        total = int(data.new_price) * qty

        return render(request, 'total_price_show_to_user.html', {
            'data': data,
            'qty': qty,
            'total': total,
            'wallet_balance': wallet_balance
        })
        
    return render(request, 'order_input_get_from_user.html', {'data': data})


def confirming_order(request, id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    if request.method == "POST":
        qty = request.POST.get('qty')
        total_bill = float(request.POST.get('total'))
        wallet = Wallet.objects.filter(user_id=user_id).first()

        if not wallet or float(wallet.balance) < total_bill:
            messages.error(request, "Insufficient Database Wallet Balance! Transaction Declined.")
            return redirect('wallet_system_for_user')
        wallet.balance = float(wallet.balance) - total_bill
        wallet.save()

        if id == 0:
            cart_items = Cart.objects.filter(user_id=user_id)
            combo_id = str(uuid.uuid4())[:8]

            for item in cart_items:
                try:
                    product = Items.objects.get(id=item.product_id)
                    total_price = int(product.new_price) * item.qty
                    Orders.objects.create(
                        product_name=product.toy_name, 
                        product_photo=product.photo,
                        order_quantity=product.order_qty,
                        user_quantity=str(item.qty),
                        price=str(total_price),
                        user_id=user_id,
                        status="Paid & Confirmed",
                        combo_id=combo_id
                    )
                except Items.DoesNotExist:
                    continue
            cart_items.delete()
        else:
            data = get_object_or_404(Items, id=id)
            Orders.objects.create(
                product_name=data.toy_name, 
                product_photo=data.photo,
                order_quantity=data.order_qty,
                user_quantity=qty,
                price=str(total_bill),
                user_id=user_id,
                status="Paid & Confirmed")
        messages.success(request, "Order placed successfully! Amount deducted from database wallet.")
    return redirect('user_order_view_by_user')
    
@admin_login_required
def orders_view_by_admin(request):
    data = Orders.objects.all().order_by('-id')    
    confirmed_count = Orders.objects.filter(status__contains="Confirmed").count()
    shipped_count = Orders.objects.filter(status__contains="Shipped").count()
    delivered_count = Orders.objects.filter(status__contains="Delivered").count()
    return render(request, 'orders_view_by_admin.html', {
        'data': data,
        'confirmed_count': confirmed_count,
        'shipped_count': shipped_count,
        'delivered_count': delivered_count})

@admin_login_required
def ordered_user_details(request, id):
    data = Orders.objects.get(id=id)
    user_data = KYC.objects.get(id=data.user_id)

    return render(request, 'ordered_user_details.html', {
        'data': data,
        'user_data': user_data
    })
def user_personal_information_type_by_user(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            KYC.objects.create(
                user_name = request.POST.get('user_name'),
                address = request.POST.get('address'),
                district = request.POST.get('district'),
                state = request.POST.get('state'),
                phone_number = request.POST.get('phone_number'),
                confirm_password=confirm_password)
        return redirect ('user_home')
    return render (request,'user_personal_information_type_by_user.html')

@admin_login_required
def update_items(request,id):
    data = get_object_or_404(Items,id=id)
    if request.method=="POST":    
            data.toy_name = request.POST.get('toy_name')
            data.order_qty = request.POST.get('order_qty')
            data.old_price = request.POST.get('old_price')
            data.new_price = request.POST.get('new_price')
            data.offer = request.POST.get('offer')
            data.discription = request.POST.get('discription')
            data.category = request.POST.get('category')
            if request.FILES.get('photo'):
                data.photo = request.FILES.get('photo')

            data.save()
            return redirect('admin_home')
    return render(request,'update_items.html',{'data':data})

@admin_login_required
def delete_item(request,id):
    data = get_object_or_404(Items,id=id)
    data.delete()
    return redirect ('admin_home')

def user_order_view_by_user(request):
    user_id = request.session.get('user_id')
    data = Orders.objects.filter(user_id=user_id).order_by('-id')
    return render(request,'user_order_view_by_user.html',{'data':data})

@admin_login_required
def update_order_status(request,id,status):
    data = get_object_or_404(Orders,id=id)
    if status not in data.status:
        data.status += "," + status
    if status == "Delivered":
        data.action_status = "delivered"
    data.save()
    return redirect('orders_view_by_admin')

def cancel_order(request, order_id):
    order = get_object_or_404(Orders, id=order_id, user_id=request.session['user_id'])
    if order.action_status != 'delivered':
        order.action_status = 'cancelled'
        order.save()
    return redirect('user_order_view_by_user')

def return_order(request, order_id):
    order = get_object_or_404(Orders, id=order_id, user_id=request.session['user_id'])
    if order.action_status == 'delivered':
        order.action_status = 'returned'
        order.save()
    return redirect('user_order_view_by_user')

@admin_login_required
def admin_dashboard(request):
    orders = Orders.objects.all().order_by("created_at")
    total_orders = orders.count()
    total_revenue = 0
    daily_sales = {}
    products = []
    for i in orders:
        try:
            price = int(i.price)
        except:
            price = 0

        total_revenue += price

        day = i.created_at.strftime("%d-%m-%Y")

        if day not in daily_sales:
            daily_sales[day] = 0

        daily_sales[day] += price

        products.append(i.product_name)

    labels = list(daily_sales.keys())
    sales_data = list(daily_sales.values())

    most_sold = "No Orders"

    if products:
        most_sold = Counter(products).most_common(1)[0][0]

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "most_sold": most_sold,
        "labels": json.dumps(labels),
        "sales_data": json.dumps(sales_data),}
    return render(request,"admin_dashboard.html",context)

def add_to_cart(request):
    if request.method == "POST":
        if not request.session.get("user_id"):
            return JsonResponse({"success": False, "message": "Please Login First"})

        data = json.loads(request.body)
        user_id = request.session["user_id"]
        product_id = data.get("product_id")

        cart_item = Cart.objects.filter(user_id=user_id, product_id=product_id).first()

        if cart_item:
            cart_item.qty += 1
            cart_item.save()
        else:
            Cart.objects.create(user_id=user_id, product_id=product_id, qty=1)

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})
def view_carts_by_user(request):
    if not request.session.get("user_id"):
        return redirect('user_login')

    user_id = request.session["user_id"]
    carts = Cart.objects.filter(user_id=user_id)
    cart_data = []
    total = 0

    for cart in carts:
        try:
            product = Items.objects.get(id=cart.product_id)
            subtotal = int(product.new_price) * cart.qty
            total += subtotal

            cart_data.append({
                "cart_id": cart.id,
                "product": product,
                "qty": cart.qty,
                "subtotal": subtotal
            })
        except Items.DoesNotExist:
            continue
    return render(request, "view_carts_by_user.html", {"cart_data": cart_data, "total": total})

def increase_qty(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    cart.qty += 1
    cart.save()
    return redirect('view_carts_by_user')

def decrease_qty(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    if cart.qty > 1:
        cart.qty -= 1
        cart.save()
    return redirect('view_carts_by_user')

def remove_cart(request, cart_id):
    Cart.objects.filter(
        id=cart_id
    ).delete()
    return redirect('view_carts_by_user')

def copy_item_to_orders(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(Items, id=item_id)
        
        new_cart_item = Cart(
            user_id=request.session.get('user_id'),
            product_id=item.id,                     
            qty=1
        )
        new_cart_item.save()
        return redirect('view_carts_by_user')
    
def cart_checkout(request):
    if not request.session.get("user_id"):
        return redirect('user_login')
    user_id = request.session["user_id"]
    cart_items = Cart.objects.filter(user_id=user_id)
    if not cart_items:
        return redirect('view_carts_by_user')   
    total = 0
    total_qty = 0
    for item in cart_items:
        try:
            product = Items.objects.get(id=item.product_id)
            total += int(product.new_price) * item.qty
            total_qty += item.qty
        except Items.DoesNotExist:
            continue
        wallet_balance = 0.00  
    combo_data = {
        'id': 0, 
        'toy_name': 'Combo Order'
    }
    return render(request, 'total_price_show_to_user.html', {
        'data': combo_data,
        'qty': total_qty,
        'total': total,
        'wallet_balance': wallet_balance, 
        'is_cart': True 
    })

def view_orders_by_combo_id(request, combo_id):
    orders = Orders.objects.filter(combo_id=combo_id)
    return render(request, "view_orders_by_combo_id.html", {"orders": orders})

def cancel_order_by_combo_id(request, combo_id):
    Orders.objects.filter(combo_id=combo_id, user_id=request.session.get('user_id')).update(action_status='cancelled')
    return redirect('user_order_view_by_user')

def return_order_by_combo_id(request, combo_id):
    Orders.objects.filter(combo_id=combo_id, user_id=request.session.get('user_id'), action_status='delivered').update(action_status='returned')
    return redirect('user_order_view_by_user')


def wallet_system_for_user(request):
    if not request.session.get("user_id"):
        return redirect('user_login')

    user_id = request.session["user_id"]
    wallet = Wallet.objects.filter(user_id=user_id).first()

    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        action = request.POST.get("action")  # 'deposit' அல்லது 'withdraw'

        if action == "deposit":
            if wallet:
                wallet.balance = float(wallet.balance) + amount
                wallet.save()
            else:
                Wallet.objects.create(user_id=user_id, balance=amount)
            messages.success(request, f"₹{amount:.2f} successfully added to your wallet!")
                
        elif action == "withdraw":
            if wallet and float(wallet.balance) >= amount:
                wallet.balance = float(wallet.balance) - amount
                wallet.save()
                messages.success(request, f"₹{amount:.2f} successfully withdrawn from your wallet!")
            else:
                messages.error(request, "Transaction Declined: Insufficient Balance in Wallet!")

        return redirect('wallet_system_for_user')

    return render(request, 'wallet_system_for_user.html', {"wallet": wallet})

@admin_login_required
def admin_chat_list(request):
    active_chats = ChatMessage.objects.filter(sender='user').values('user_id', 'product_id').annotate(
        latest_msg=Max('created_at')
    ).order_by('-latest_msg')
    chat_data = []
    for chat in active_chats:
        try:
            product = Items.objects.get(id=chat['product_id'])
            user_identifier = f"User #{chat['user_id']}"
            
            chat_data.append({
                'product': product,
                'user_id': chat['user_id'],
                'user_name': user_identifier
            })
        except Items.DoesNotExist:
            continue
    return render(request, 'admin_chat_lists.html', {'chat_data': chat_data})

@admin_login_required
def admin_reply(request, product_id, user_id):
    product = Items.objects.get(id=product_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(user_id=user_id,product_id=product_id,sender='admin',message=message)
            return redirect('admin_reply', product_id=product_id, user_id=user_id)
    chats = ChatMessage.objects.filter(user_id=user_id,product_id=product_id).order_by('created_at')
    return render(request, 'conversation_admin.html', {'chats': chats,'product': product,'user_id': user_id})

def user_chat_lists(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    active_chats = ChatMessage.objects.filter(user_id=user_id).values('product_id').annotate(
        latest_msg=Max('created_at')
    ).order_by('-latest_msg')
    chat_data = []
    for chat in active_chats:
        try:
            product = Items.objects.get(id=chat['product_id'])
            chat_data.append({
                'product': product,
                'product_id': chat['product_id']
            })
        except Items.DoesNotExist:
            continue
            
    return render(request, 'user_chat_lists.html', {'chat_data': chat_data})

def conversation_user(request, product_id, user_id):
    product = Items.objects.get(id=product_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(
                user_id=user_id,
                product_id=product_id,
                sender='user',
                message=message
            )
            return redirect('conversation_user', product_id=product_id, user_id=user_id)
    chats = ChatMessage.objects.filter(
        user_id=user_id,
        product_id=product_id
    ).order_by('created_at')

    return render(request, 'conversation_user.html', {
        'chats': chats,
        'product': product,
        'user_id': user_id
    })

def submit_product_rating(request, order_id):
    order = get_object_or_404(Orders, id=order_id)    
    if order.action_status != 'delivered':
        return redirect('user_order_view_by_user')
    if request.method == 'POST':
        rating_value = request.POST.get('rating')  
        review_msg = request.POST.get('review_text') 
        user_account = get_object_or_404(KYC, id=request.session.get('user_id'))
        ProductReview.objects.create(
            order=order,
            user=user_account,
            rating=int(rating_value),
            review_text=review_msg
        )
        return redirect('user_order_view_by_user')
    return render(request, 'submit_product_rating.html', {'order': order})

@admin_login_required
def admin_reviews_list(request):
    top_reviewed_data = ProductReview.objects.values(
        'order__product_name', 
        'order__product_photo'
    ).annotate(
        high_review_count=Count('id', filter=Q(rating__gt=3)),
        average_rating=Avg('rating'),
        total_orders=Count('order')
    ).filter(high_review_count__gt=0).order_by('-total_orders', '-high_review_count')[:4]
    reviews = ProductReview.objects.all().order_by('-created_at')    
    context = {'top_products': top_reviewed_data,'reviews': reviews}
    return render(request, 'admin_reviews_list.html', context)

@admin_login_required
def admin_returned_products_view(request):
    returned_items = Orders.objects.filter(action_status='returned').values('product_name', 'product_photo').annotate(
        total_returned_orders=Count('id'),
        total_returned_qty=Sum(models.functions.Cast('order_quantity', output_field=models.IntegerField()))
    ).order_by('-total_returned_qty')
    detailed_returns = Orders.objects.filter(action_status='returned').order_by('-id')

    context = {
        'returned_items': returned_items,
        'detailed_returns': detailed_returns}
    return render(request, 'returned_items_lists.html', context)
    