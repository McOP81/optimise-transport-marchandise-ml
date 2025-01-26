# -*- encoding: utf-8 -*-

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Truck, Delivery
from django.contrib import messages
from django.utils.timezone import now
from .forms import TruckForm,DeliveryForm
from datetime import datetime, date
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count, Min
from datetime import timedelta
from django.db.models.functions import ExtractMonth, ExtractWeekDay

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def manage_trucks(request):
    trucks = Truck.objects.all()
    return render(request, 'trucks/manage_trucks.html',{'trucks': trucks,'today': now().date(),'segment': 'manage_trucks'})

@login_required(login_url="/login/")
def delete_truck(request, truck_id):
    truck = get_object_or_404(Truck, id=truck_id)
    deliveries = Delivery.objects.filter(truck=truck)
    deliveries.delete()
    truck.delete()
    messages.success(request, "Le camion et les livraisons associées ont été supprimés avec succès !")
    return redirect('manage_trucks')

@login_required(login_url="/login/")
def add_truck(request):
    if request.method == "POST":
        name_truck = request.POST.get('name_truck')
        registration_number = request.POST.get('registration_number')
        model = request.POST.get('model')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        tonnage = request.POST.get('tonnage')
        insurance_date = request.POST.get('insurance_date')
        gray_card_date = request.POST.get('gray_card_date')
        if Truck.objects.filter(name_truck=name_truck).exists():
            messages.error(request, "Il existe déjà un camion portant ce nom.")
            return redirect('add_truck')
        if Truck.objects.filter(registration_number=registration_number).exists():
            messages.error(request, "Un camion portant ce numéro d'immatriculation existe déjà.")
            return redirect('add_truck')
        truck = Truck(
            name_truck=name_truck,
            registration_number=registration_number,
            model=model,
            location=location,
            phone=phone,
            tonnage=tonnage,
            insurance_date=insurance_date,
            gray_card_date=gray_card_date
        )
        truck.save()
        messages.success(request, "Le camion a été ajouté avec succès !")
        return redirect('add_truck')
    return render(request, 'trucks/add_truck.html', {'segment': 'add_truck'})

@login_required(login_url="/login/")
def edit_truck(request, truck_id):
    truck = get_object_or_404(Truck, id=truck_id)
    
    if request.method == "POST":
        form = TruckForm(request.POST, instance=truck)
        
        if form.is_valid():
            name_truck = form.cleaned_data['name_truck']
            registration_number = form.cleaned_data['registration_number']
            
            if Truck.objects.filter(name_truck=name_truck).exclude(id=truck.id).exists():
                form.add_error('name_truck', "Il existe déjà un camion portant ce nom.")
                messages.error(request, "Il existe déjà un camion portant ce nom.")
            
            if Truck.objects.filter(registration_number=registration_number).exclude(id=truck.id).exists():
                form.add_error('registration_number', "Un camion portant ce numéro d'immatriculation existe déjà.")
                messages.error(request, "Un camion portant ce numéro d'immatriculation existe déjà.")
            
            if not form.errors:
                form.save()
                messages.success(request, "Le camion a été mis à jour avec succès !")
                return redirect('manage_trucks')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = TruckForm(instance=truck)
    
    return render(request, 'trucks/edit_truck.html', {
        'form': form,
        'truck': truck,
    })

@login_required(login_url="/login/")
def deliveryadd(request):
    trucks = Truck.objects.all()
    return render(request, 'home/deliveryadd.html',{'trucks': trucks,'segment': 'deliveryadd'})

@login_required(login_url="/login/")
def delivery_manage(request):
    deliveries = Delivery.objects.select_related('truck').all()
    formatted_deliveries = []
    for delivery in deliveries:
        duration_hours = None
        if delivery.arrival_date and delivery.departure_date:
            duration = delivery.arrival_date - delivery.departure_date
            duration_hours = int(duration.total_seconds() // 3600)
        formatted_delivery = {
            'id': delivery.id,
            'name_truck': delivery.truck.name_truck,
            'departure_city': delivery.departure_city,
            'departure_date': delivery.departure_date.strftime("%Y-%m-%d %H:%M"),
            'arrival_city': delivery.arrival_city,
            'arrival_date': delivery.arrival_date.strftime("%Y-%m-%d %H:%M"),
            'duration_hours': duration_hours,
            'phone_number': delivery.phone_number,
            'tonnage': delivery.tonnage,
            'loaded_trip': delivery.loaded_trip,
        }
        formatted_deliveries.append(formatted_delivery)
    return render(request, 'home/deliverymanage.html', {'deliveries': formatted_deliveries, 'segment': 'delivery_manage'})

@login_required(login_url="/login/")
def delete_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    delivery.delete()
    messages.success(request, 'La livraison a été effacée avec succès.')
    return redirect('delivery_manage')

@login_required(login_url="/login/")
def deliveryadd(request):
    trucks = Truck.objects.all()
    if request.method == "POST":
        name_truck_id = request.POST.get('name_truck')
        locationstart = request.POST.get('locationstart')
        locationend = request.POST.get('locationend')
        datestart_str = request.POST.get('datestart')
        dateend_str = request.POST.get('dateend')
        phone = request.POST.get('phone')
        tonnage = request.POST.get('tonnage')
        loaded_trip = request.POST.get('loaded_trip') == "on"
        if not (name_truck_id and locationstart and locationend and datestart_str and dateend_str):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('deliveryadd')
        if datestart_str > dateend_str:
            messages.error(request, "La date de départ doit être antérieure ou égale à la date d'arrivée.")
            return redirect('deliveryadd')
        truck = get_object_or_404(Truck, id=name_truck_id)
        if int(tonnage) > truck.tonnage:
            messages.error(request, "Le tonnage de la livraison doit être inférieur ou égal au tonnage du camion.")
            return redirect('deliveryadd')
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        last_id = Delivery.objects.count() + 1
        custom_id = f"RF{last_id}{timestamp}"
        delivery = Delivery(
            id=custom_id,
            departure_city=locationstart,
            arrival_city=locationend,
            departure_date=datestart_str,
            arrival_date=dateend_str,
            phone_number=phone,
            tonnage=tonnage,
            loaded_trip=loaded_trip,
            truck=truck
        )
        delivery.save()
        messages.success(request, "La livraison a été ajoutée avec succès !")
        return redirect('deliveryadd')
    return render(request, 'home/deliveryadd.html', {'trucks': trucks, 'segment': 'deliveryadd'})

@login_required(login_url="/login/")
def deliveryedit(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    if request.method == "POST":
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            if not form.errors:
                form.save()
                messages.success(request, "La livraison a été mise à jour avec succès !")
                return redirect('delivery_manage')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = DeliveryForm(instance=delivery)
    return render(request, 'home/deliveryedit.html', {
        'form': form,
        'delivery': delivery,
    })
    
def get_occupied_dates(request, truck_id):
    try:
        departure_city = request.GET.get('departure_city')
        arrival_city = request.GET.get('arrival_city')
        if not departure_city or not arrival_city:
            return JsonResponse({'error': 'La ville de départ et la ville arrivée sont obligatoires.'}, status=400)
        deliveries = Delivery.objects.filter(
            truck_id=truck_id,
            departure_city=departure_city,
            arrival_city=arrival_city
        )
        occupied_ranges = []
        for delivery in deliveries:
            duration = delivery.arrival_date - delivery.departure_date
            start_block = delivery.departure_date
            end_block = delivery.arrival_date + duration
            occupied_ranges.append({
                'start': start_block.strftime('%Y-%m-%d %H:%M'),
                'end': end_block.strftime('%Y-%m-%d %H:%M'),
                'duration':str(duration)
            })
        return JsonResponse(occupied_ranges, safe=False)
    except Exception as e:
        print(f"Erreur dans get_occupied_dates: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
    
@login_required(login_url="/login/")
def map_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    departure_city = delivery.departure_city
    arrival_city = delivery.arrival_city
    return render(request, 'home/map.html', {
        'delivery': delivery,
        'departure_city': departure_city,
        'arrival_city': arrival_city,
    })

@login_required(login_url="/login/")
def delayadd(request):
    deliveries = Delivery.objects.filter(delay__isnull=True)
    return render(request, 'delay/delayadd.html', {'deliveries': deliveries, 'segment': 'delayadd'})

@login_required(login_url="/login/")
def delayadd(request):
    if request.method == "POST":
        delivery_id = request.POST.get('id_Deliveries')
        delay = request.POST.get('delay')
        if not delivery_id or not delay:
            messages.error(request, "Veuillez remplir tous les champs requis.")
            return redirect('delayadd')
        delivery = get_object_or_404(Delivery, id=delivery_id)
        delivery.delay = delay
        delivery.save()
        messages.success(request, "Le retard a été ajouté avec succès.")
        return redirect('delayadd')
    deliveries = Delivery.objects.filter(delay__isnull=True)
    return render(request, 'delay/delayadd.html', {'deliveries': deliveries, 'segment': 'delayadd'})

@login_required(login_url="/login/")
def get_delivery_details(request, delivery_id):
    try:
        delivery = Delivery.objects.get(id=delivery_id)
        data = {
            'departure_city': delivery.departure_city,
            'arrival_city': delivery.arrival_city,
            'departure_date': delivery.departure_date.strftime('%Y-%m-%dT%H:%M'),
            'arrival_date': delivery.arrival_date.strftime('%Y-%m-%dT%H:%M'),
            'tonnage': delivery.tonnage,
        }
        return JsonResponse(data)
    except Delivery.DoesNotExist:
        return JsonResponse({'error': 'Livraison introuvable'}, status=404)

@login_required(login_url="/login/")
def delaymanage(request):
    deliveries = Delivery.objects.filter(delay__isnull=False)
    formatted_deliveries = []
    for delivery in deliveries:
        duration_hours = None
        if delivery.arrival_date and delivery.departure_date:
            duration = delivery.arrival_date - delivery.departure_date
            duration_hours = int(duration.total_seconds() // 3600)
        formatted_delivery = {
            'id': delivery.id,
            'name_truck': delivery.truck.name_truck,
            'departure_city': delivery.departure_city,
            'departure_date': delivery.departure_date.strftime("%Y-%m-%d %H:%M"),
            'arrival_city': delivery.arrival_city,
            'arrival_date': delivery.arrival_date.strftime("%Y-%m-%d %H:%M"),
            'duration_hours': duration_hours,
            'tonnage': delivery.tonnage,
            'delay': delivery.delay,
        }
        formatted_deliveries.append(formatted_delivery)
    return render(request, 'delay/delaymanage.html', {'deliveries': formatted_deliveries, 'segment': 'delaymanage'})

@login_required(login_url="/login/")
def delaydelete(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    delivery.delay = None
    delivery.save()
    messages.success(request, 'Le retard a été supprimé avec succès.')
    return redirect('delaymanage')

@login_required(login_url="/login/")
def managedeliverynow(request):
    today = timezone.now().date()
    deliveries = Delivery.objects.filter(departure_date__date=today) | Delivery.objects.filter(arrival_date__date=today)   
    formatted_deliveries = []
    for delivery in deliveries:
        duration_hours = None
        if delivery.arrival_date and delivery.departure_date:
            duration = delivery.arrival_date - delivery.departure_date
            duration_hours = int(duration.total_seconds() // 3600)
        formatted_delivery = {
            'id': delivery.id,
            'name_truck': delivery.truck.name_truck,
            'departure_city': delivery.departure_city,
            'departure_date': delivery.departure_date.strftime("%Y-%m-%d %H:%M"),
            'arrival_city': delivery.arrival_city,
            'arrival_date': delivery.arrival_date.strftime("%Y-%m-%d %H:%M"),
            'duration_hours': duration_hours,
            'tonnage': delivery.tonnage,
            'delay': delivery.delay,
            'phone_number': delivery.phone_number,
            'tonnage': delivery.tonnage,
            'loaded_trip': delivery.loaded_trip,
            'arrival_delivery' : delivery.arrival_delivery,
        }
        formatted_deliveries.append(formatted_delivery)
    return render(request, 'home/managedeliverynow.html', {'deliveries': formatted_deliveries, 'segment': 'managedeliverynow'})

@login_required(login_url="/login/")
def index(request):
    total_trucks = Truck.objects.count()
    now = timezone.now()
    deliveries_this_month = Delivery.objects.filter(
        departure_date__year=now.year,
        departure_date__month=now.month,
        arrival_delivery=1 
    ).count()
    deliveries_this_month_loaded = Delivery.objects.filter(
        departure_date__year=now.year,
        departure_date__month=now.month,
        loaded_trip=True
    ).count()
    unique_departure_cities = Delivery.objects.values('departure_city').distinct().count()
    unique_arrival_cities = Delivery.objects.values('arrival_city').distinct().count()
    max_unique_cities = max(unique_departure_cities, unique_arrival_cities)
    deliveries_by_month = Delivery.objects.filter(
        departure_date__year=now.year
    ).annotate(
        month=ExtractMonth('departure_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    monthly_deliveries = [0] * 12
    for entry in deliveries_by_month:
        monthly_deliveries[entry['month'] - 1] = entry['count']
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    deliveries_by_day = Delivery.objects.filter(
        departure_date__date__gte=start_of_week.date(),
        departure_date__date__lte=end_of_week.date()
    ).annotate(
        day=ExtractWeekDay('departure_date')
    ).values('day').annotate(
        count=Count('id'),
        date=Min('departure_date__date')
    ).order_by('day')
    daily_deliveries = [0] * 7
    daily_labels = [''] * 7
    day_mapping = {
        1: 'Dim', 2: 'Lun', 3: 'Mar', 4: 'Mer', 5: 'Jeu', 6: 'Ven', 7: 'Sam'
    }
    adjusted_day_index = {
        2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 1: 6
    }
    for entry in deliveries_by_day:
        day_of_week = entry['day']
        day_index = adjusted_day_index[day_of_week]
        daily_deliveries[day_index] = entry['count']
        daily_labels[day_index] = f"{day_mapping[day_of_week]} ({entry['date'].strftime('%d/%m')})"
    delays_by_day = {day: 0 for day in ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']}
    deliveries_this_week = Delivery.objects.filter(
        departure_date__date__gte=start_of_week.date(),
        departure_date__date__lte=end_of_week.date()
    )
    for delivery in deliveries_this_week:
        if delivery.delay:
            try:
                delay_hours = int(delivery.delay.split()[0])
                day_of_week = delivery.departure_date.strftime('%a')
                day_key = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mer', 'Thu': 'Jeu', 'Fri': 'Ven', 'Sat': 'Sam', 'Sun': 'Dim'}[day_of_week]
                delays_by_day[day_key] += delay_hours
            except (ValueError, IndexError):
                continue
    days_of_week = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    delays_data = [delays_by_day[day] for day in days_of_week]
    today = date.today()
    expired_trucks = Truck.objects.filter(
        Q(gray_card_date__lte=today) | Q(insurance_date__lte=today)
    )
    context = {
        'total_trucks': total_trucks,
        'deliveries_this_month': deliveries_this_month,
        'deliveries_this_month_loaded': deliveries_this_month_loaded,
        'max_unique_cities': max_unique_cities,
        'delays_data': delays_data,
        'monthly_deliveries': monthly_deliveries,
        'daily_deliveries': daily_deliveries,
        'daily_labels': daily_labels,
        'expired_trucks': expired_trucks,
    }
    return render(request, 'home/index.html', context)

@login_required(login_url="/login/")
def deliverynow_1(request):
    today = timezone.now().date()
    deliveries = Delivery.objects.filter(arrival_date__date=today)   
    formatted_deliveries = []
    for delivery in deliveries:
        duration_hours = None
        if delivery.arrival_date and delivery.departure_date:
            duration = delivery.arrival_date - delivery.departure_date
            duration_hours = int(duration.total_seconds() // 3600)
        formatted_delivery = {
            'id': delivery.id,
            'name_truck': delivery.truck.name_truck,
            'departure_city': delivery.departure_city,
            'departure_date': delivery.departure_date.strftime("%Y-%m-%d %H:%M"),
            'arrival_city': delivery.arrival_city,
            'arrival_date': delivery.arrival_date.strftime("%Y-%m-%d %H:%M"),
            'duration_hours': duration_hours,
            'tonnage': delivery.tonnage,
            'delay': delivery.delay,
            'phone_number': delivery.phone_number,
            'tonnage': delivery.tonnage,
            'loaded_trip': delivery.loaded_trip,
            'arrival_delivery' : delivery.arrival_delivery,
        }
        formatted_deliveries.append(formatted_delivery)
    return render(request, 'home/deliverynow_1.html', {'deliveries': formatted_deliveries, 'segment': 'deliverynow_1'})

@login_required(login_url="/login/")
def deliveryaccept(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    delivery.arrival_delivery = 1
    delivery.save()
    messages.success(request, 'Le statut de livraison a été mis à jour avec succès (expédié).')
    return redirect('deliverynow_1')

@login_required(login_url="/login/")
def deliveryrefuse(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    delivery.arrival_delivery = 0
    delivery.save()
    messages.success(request, 'Le statut de livraison a été mis à jour avec succès (non expédié).')
    return redirect('deliverynow_1')