from django.shortcuts import render,redirect
from django.views import View
from .models import Customer,Product,Cart,OrderPlaced
from django.contrib.auth.models import User
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductView(View):
    def get(self,request):
        totalitem = 0
        topwear = Product.objects.filter(category ='TW')
        bottomwear = Product.objects.filter(category ='BW')
        mobile = Product.objects.filter(category ='M')
        laptop = Product.objects.filter(category ='L')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html',{'topwear':topwear,
            'bottomwear':bottomwear,'mobile':mobile,'laptop':laptop,'totalitem':totalitem})

       
class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            
        return render(request, 'app/productdetail.html', {'prodoct': product, 'item_already_in_cart': item_already_in_cart,'totalitem':totalitem})
    
def Search(request):
    query = request.GET['query']
    if len(query) > 80:
        data = Product.objects.none()
    elif len(query) < 1:
        data = Product.objects.all()
        return redirect('/')
    else: 
        allDataTitle = Product.objects.filter(title__icontains=query)
        allDataCategory = Product.objects.filter(category__icontains=query)
        data = allDataTitle.union(allDataCategory)
    return render(request, 'app/search.html', {'data': data, 'query': query}) 

@login_required
def add_to_cart(request):
    user=request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user=request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        #print(cart_product)

        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'amount':amount,'totalitem':totalitem})
        else:
            return render(request, 'app/empty.html')
    

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                # totalamount = amount + shipping_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)
    

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                # totalamount = amount + shipping_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)

  
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
       
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
             

        data = {
            'amount': amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)


@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add':add, 'active':'btn-primary'})

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed':op})

def mobile(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        mobile = Product.objects.filter(category='M')
    elif data == 'Mi' or data =='Samsung' or data == 'Realme' or data == 'Vivo' or data == 'Pova':
        mobile = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'Below':
        mobile = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'Above':
        mobile = Product.objects.filter(category='M').filter(discounted_price__gt=10000)

    return render(request, 'app/mobile.html', {'mobile':mobile,'totalitem':totalitem})


def laptop(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        laptop = Product.objects.filter(category='L')
    elif data == 'Dell' or data =='HP' or data == 'Acer' or data == 'Asus' or data == 'IPad' or data == 'Msi':
        laptop = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'Below':
        laptop = Product.objects.filter(category='L').filter(discounted_price__lt=30000)
    elif data == 'Above':
        laptop = Product.objects.filter(category='L').filter(discounted_price__gt=30000)

    return render(request, 'app/laptop.html', {'laptop':laptop,'totalitem':totalitem})


def topwear(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        topwear = Product.objects.filter(category='TW')
    elif data == 'Lymio' or data =='Harpa' or data == 'Eta' or data == 'Denim' or data == 'KeriPerry' or data == 'Selvia' or data == 'Raymond':
        topwear = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'Below':
        topwear = Product.objects.filter(category='TW').filter(discounted_price__lt=500)
    elif data == 'Above':
        topwear = Product.objects.filter(category='TW').filter(discounted_price__gt=500)

    return render(request, 'app/topwear.html', {'topwear':topwear,'totalitem':totalitem})

def bottomwear(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        bottomwear = Product.objects.filter(category='BW')
    elif data == 'Spykar' or data == 'Symbol' or data == 'Biba' or data == 'Lee' or data == 'Klart' or data == 'DigitalShopee':
        bottomwear = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'Below':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__lt=500)
    elif data == 'Above':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__gt=500)

    return render(request, 'app/bottomwear.html', {'bottomwear':bottomwear,'totalitem':totalitem})


class CustomerRegistrationView(View):
    def get(self, request):
       form = CustomerRegistrationForm()
       return render(request, 'app/customerregistration.html',{'form':form})
    
    def post(self, request):
       form = CustomerRegistrationForm(request.POST)
       if form.is_valid():
          messages.success(request, 'Congratulations!! Registered Successfully')
          form.save()
       return render(request, 'app/customerregistration.html',{'form':form})
    
@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount=amount + shipping_amount
    return render(request, 'app/checkout.html', {'add':add, 'totalamount':totalamount, 'cart_items':cart_items})

@login_required
def payment_done(request):
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders",{'totalitem':totalitem})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
       form = CustomerProfileForm()
       return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            zipcode = form.cleaned_data['zipcode']
            state = form.cleaned_data['state']
            reg = Customer(user=usr, name=name, locality=locality, city=city, zipcode=zipcode, state=state)
            reg.save()
            messages.success(request, 'Conguratioulations!! Profile Upadated Successfully')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    


