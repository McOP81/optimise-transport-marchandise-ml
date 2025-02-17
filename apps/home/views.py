# -*- encoding: utf-8 -*-

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Truck, Delivery, Profile
from django.contrib import messages
from django.utils.timezone import now
from .forms import TruckForm, DeliveryForm
from datetime import datetime, date
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count, Min
from datetime import timedelta
from django.db.models.functions import ExtractMonth, ExtractWeekDay
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
import os
from django.conf import settings
from django.contrib.auth.models import User
import random
import string
from django.contrib.auth.hashers import make_password
from .models import Profile
from .forms import EditChauffeurForm 
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth, ExtractWeekDay



# Chemin vers les modèles
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'random_forest_model.pkl')
RETARD_MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'Random Forest_model_retard.pkl')

# Charger les modèles
model = joblib.load(MODEL_PATH)  # Modèle existant
retard_model = joblib.load(RETARD_MODEL_PATH)  # Nouveau modèle pour prédire le retard

# Initialiser le LabelEncoder
label_encoder = LabelEncoder()

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
    return render(request, 'trucks/manage_trucks.html', {'trucks': trucks, 'today': now().date(), 'segment': 'manage_trucks'})

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
        # Récupérer les données du formulaire
        name_truck = request.POST.get('name_truck')
        registration_number = request.POST.get('registration_number')
        model_truck = request.POST.get('model')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        tonnage = request.POST.get('tonnage')
        insurance_date = request.POST.get('insurance_date')
        gray_card_date = request.POST.get('gray_card_date')
        id_user = request.POST.get('name_chauffeur')  # Récupérer l'ID du chauffeur

        # Vérifier si un camion avec le même nom ou numéro d'immatriculation existe déjà
        if Truck.objects.filter(name_truck=name_truck).exists():
            messages.error(request, "Il existe déjà un camion portant ce nom.")
            return redirect('add_truck')
        if Truck.objects.filter(registration_number=registration_number).exists():
            messages.error(request, "Un camion portant ce numéro d'immatriculation existe déjà.")
            return redirect('add_truck')

        # Récupérer l'objet User correspondant au chauffeur
        try:
            id_user = User.objects.get(id=id_user, is_staff=True)
        except User.DoesNotExist:
            messages.error(request, "Le chauffeur sélectionné n'existe pas ou n'est pas valide.")
            return redirect('add_truck')

        # Créer et enregistrer le camion
        truck = Truck(
            name_truck=name_truck,
            registration_number=registration_number,
            model=model_truck,
            location=location,
            phone=phone,
            tonnage=tonnage,
            insurance_date=insurance_date,
            gray_card_date=gray_card_date,
            id_user=id_user  # Associer le chauffeur au camion
        )
        truck.save()

        messages.success(request, "Le camion a été ajouté avec succès !")
        return redirect('add_truck')

    # Récupérer uniquement les utilisateurs avec is_staff = True pour la liste déroulante
    users = User.objects.filter(is_staff=True)
    return render(request, 'trucks/add_truck.html', {
        'segment': 'add_truck',
        'users': users,  # Passer les utilisateurs au template
    })

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

    # Mapping des villes
    ville_mapping = {
        "Casablanca": 1,
        "Rabat": 3,
        "Marrakech": 2,
        "Tanger": 5,
        "Agadir": 0
    }

    if request.method == "POST":
        name_truck_id = request.POST.get('name_truck')
        locationstart = request.POST.get('locationstart')
        locationend = request.POST.get('locationend')
        datestart_str = request.POST.get('datestart')
        dateend_str = request.POST.get('dateend')
        phone = request.POST.get('phone')
        tonnage = request.POST.get('tonnage')
        weekend = request.POST.get('weekend')
        jour_ferie = request.POST.get('jour_ferie')

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

        departure_date = datetime.strptime(datestart_str, "%Y-%m-%dT%H:%M")
        arrival_date = datetime.strptime(dateend_str, "%Y-%m-%dT%H:%M")

        duration_hours = (arrival_date - departure_date).total_seconds() / 3600
        duration_days = duration_hours / 24

        # Vérifier si les villes existent dans le mapping
        if locationstart not in ville_mapping or locationend not in ville_mapping:
            messages.error(request, "Une ou plusieurs villes ne sont pas reconnues.")
            return redirect('deliveryadd')

        # Récupérer les valeurs encodées pour les villes
        ville_depart = ville_mapping.get(locationstart, -1)
        ville_arrivee = ville_mapping.get(locationend, -1)

        input_data = pd.DataFrame({
            'departure_city': [ville_depart],
            'arrival_city': [ville_arrivee],
            'duration_hours': [duration_hours],
            'tonnage': [int(tonnage)],
            'duration_days': [duration_days],
        })

        try:
            loaded_trip = model.predict(input_data)[0]
        except Exception as e:
            messages.error(request, f"Erreur lors de la prédiction : {str(e)}")
            return redirect('deliveryadd')

        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        last_id = Delivery.objects.count() + 1
        custom_id = f"RF{last_id}{timestamp}"
        delivery = Delivery(
            id=custom_id,
            departure_city=locationstart,
            arrival_city=locationend,
            departure_date=departure_date,  
            arrival_date=arrival_date,      
            phone_number=phone,
            tonnage=tonnage,
            loaded_trip=bool(loaded_trip),
            weekend=weekend,
            jour_ferie=jour_ferie,
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
                'duration': str(duration)
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

        if not delivery_id:
            messages.error(request, "Veuillez sélectionner une livraison.")
            return redirect('delayadd')

        delivery = get_object_or_404(Delivery, id=delivery_id)

        # Prédire le retard si l'utilisateur n'a pas saisi de valeur
        if not delay:
            try:
                # Mapping des villes
                ville_mapping = {
                    "Casablanca": 1,
                    "Rabat": 3,
                    "Marrakech": 2,
                    "Tanger": 5,
                    "Agadir": 0
                }

                # Récupérer les valeurs encodées pour les villes
                ville_depart = ville_mapping.get(delivery.departure_city, -1)
                ville_arrivee = ville_mapping.get(delivery.arrival_city, -1)

                if ville_depart == -1 or ville_arrivee == -1:
                    messages.error(request, "Ville de départ ou d'arrivée non reconnue.")
                    return redirect('delayadd')

                # Calculer la durée réelle en minutes
                duree_reelle = (delivery.arrival_date - delivery.departure_date).total_seconds() / 60

                # Préparer les données pour la prédiction
                input_data = pd.DataFrame({
                    'Ville de depart': [ville_depart],
                    'Ville d\'arrivee': [ville_arrivee],
                    'Distance (km)': [100],  # Remplacez par la distance réelle si disponible
                    'Poids (kg)': [delivery.tonnage],
                    'Heure_depart': [delivery.departure_date.hour],
                    'Heure_arrivee': [delivery.arrival_date.hour],
                    'Weekend': [delivery.weekend],
                    'Jour ferie': [delivery.jour_ferie],
                    'Duree reelle (minutes)': [duree_reelle]
                })

                # Prédire le retard
                predicted_delay = retard_model.predict(input_data)[0]
                predicted_delay = int(predicted_delay)  # Convertir en entier
                delay = predicted_delay  # Utiliser la valeur prédite
                messages.info(request, f"Retard prédit : {predicted_delay} minutes.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la prédiction du retard : {str(e)}")
                return redirect('delayadd')

        # Enregistrer le retard dans la base de données
        delivery.delay = delay  # Utiliser la valeur prédite ou saisie
        delivery.save()  # Sauvegarder l'objet Delivery

        messages.success(request, "Le retard a été ajouté avec succès.")
        return redirect('delayadd')

    # Récupérer les livraisons sans retard
    deliveries = Delivery.objects.filter(delay__isnull=True)
    return render(request, 'delay/delayadd.html', {'deliveries': deliveries, 'segment': 'delayadd'})

@login_required(login_url="/login/")
def delayupdate(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)

    if request.method == "POST":
        delay = request.POST.get('delay')

        if not delay:
            messages.error(request, "Veuillez entrer un retard valide.")
            return redirect('delayupdate', delivery_id=delivery_id)
        
        delivery.delay = delay
        delivery.save()

        messages.success(request, "Le retard a été mis à jour avec succès.")
        return redirect('delaymanage')

    return render(request, 'delay/delayupdate.html', {
        'delivery': delivery,
        'segment': 'delayupdate'
    })

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
    
    # Filtrer les livraisons en fonction des permissions
    if request.user.is_superuser:
        # Si superutilisateur, afficher toutes les livraisons du jour
        deliveries = Delivery.objects.filter(departure_date__date=today) | Delivery.objects.filter(arrival_date__date=today)
    elif request.user.is_staff:
        # Si personnel, afficher uniquement les livraisons associées à ses propres camions
        deliveries = Delivery.objects.filter(
            (Q(departure_date__date=today) | Q(arrival_date__date=today)) & 
            Q(truck__id_user=request.user)
        )
    else:
        # Si ni superutilisateur ni personnel, ne montrer aucune livraison
        deliveries = Delivery.objects.none()
    
    # Formater les données des livraisons
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
            'loaded_trip': delivery.loaded_trip,
            'arrival_delivery': delivery.arrival_delivery,
        }
        formatted_deliveries.append(formatted_delivery)
    
    return render(request, 'home/managedeliverynow.html', {'deliveries': formatted_deliveries, 'segment': 'managedeliverynow'})

@login_required(login_url="/login/")
def index(request):
    total_trucks = Truck.objects.count()
    now = timezone.now()

    # Filtrer les livraisons en fonction du type d'utilisateur
    if request.user.is_superuser:
        # Pour les superutilisateurs, afficher toutes les livraisons
        deliveries = Delivery.objects.all()
    elif request.user.is_staff:
        # Pour les utilisateurs staff, afficher uniquement leurs livraisons
        deliveries = Delivery.objects.filter(truck__id_user=request.user)
    else:
        deliveries = Delivery.objects.none()  # Aucune livraison pour les autres utilisateurs

    # Récupérer les données générales
    deliveries_this_month = deliveries.filter(
        departure_date__year=now.year,
        departure_date__month=now.month,
        arrival_delivery=1
    ).count()
    deliveries_this_month_loaded = deliveries.filter(
        departure_date__year=now.year,
        departure_date__month=now.month,
        loaded_trip=True
    ).count()
    unique_departure_cities = deliveries.values('departure_city').distinct().count()
    unique_arrival_cities = deliveries.values('arrival_city').distinct().count()
    max_unique_cities = max(unique_departure_cities, unique_arrival_cities)

    # Récupérer les livraisons par mois
    deliveries_by_month = deliveries.filter(
        departure_date__year=now.year
    ).annotate(
        month=ExtractMonth('departure_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    monthly_deliveries = [0] * 12
    for entry in deliveries_by_month:
        monthly_deliveries[entry['month'] - 1] = entry['count']

    # Récupérer les livraisons par jour de la semaine
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    deliveries_by_day = deliveries.filter(
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

    # Récupérer les retards par jour de la semaine
    delays_by_day = {day: 0 for day in ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']}
    deliveries_this_week = deliveries.filter(
        departure_date__date__gte=start_of_week.date(),
        departure_date__date__lte=end_of_week.date()
    )
    for delivery in deliveries_this_week:
        if delivery.delay:
            try:
                delay_hours = int(delivery.delay)
                day_of_week = delivery.departure_date.strftime('%a')
                day_key = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mer', 'Thu': 'Jeu', 'Fri': 'Ven', 'Sat': 'Sam', 'Sun': 'Dim'}[day_of_week]
                delays_by_day[day_key] += delay_hours
            except (ValueError, IndexError):
                continue
    days_of_week = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    delays_data = [delays_by_day[day] for day in days_of_week]

    # Récupérer les camions expirés
    today = date.today()
    if request.user.is_superuser:
        # Pour les superutilisateurs, afficher tous les camions expirés
        expired_trucks = Truck.objects.filter(
            Q(gray_card_date__lte=today) | Q(insurance_date__lte=today))
    elif request.user.is_staff:
        # Pour les utilisateurs staff, afficher uniquement leurs camions expirés
        expired_trucks = Truck.objects.filter(
            Q(gray_card_date__lte=today) | Q(insurance_date__lte=today),
            id_user=request.user
        )
    else:
        expired_trucks = []

    # Récupérer les livraisons du chauffeur pour aujourd'hui
    today_deliveries = deliveries.filter(
        departure_date__date=now.date()
    )

    # Calculer le temps restant pour chaque livraison
    delivery_timers = []
    for delivery in today_deliveries:
        time_remaining = delivery.arrival_date - now
        if time_remaining.total_seconds() > 0:
            delivery_timers.append({
                'id': delivery.id,
                'time_remaining': int(time_remaining.total_seconds())
            })

    # Contexte pour le template
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
        'delivery_timers': delivery_timers,  # Ajout des timers pour les livraisons
    }
    return render(request, 'home/index.html', context)


@login_required(login_url="/login/")
def deliverynow_1(request):
    today = timezone.now().date()

    # Si l'utilisateur est superutilisateur, il peut voir toutes les livraisons
    if request.user.is_superuser:
        deliveries = Delivery.objects.filter(arrival_date__date=today)
    # Si l'utilisateur est un membre du staff, il ne voit que ses propres livraisons
    elif request.user.is_staff:
        deliveries = Delivery.objects.filter(arrival_date__date=today, truck__id_user=request.user)
    else:
        # Autrement, on n'affiche aucune livraison pour les autres utilisateurs
        deliveries = []

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
            'arrival_delivery': delivery.arrival_delivery,
            'jour_ferie': delivery.jour_ferie,
            'weekend' : delivery.weekend,
        }
        formatted_deliveries.append(formatted_delivery)

    return render(request, 'home/deliverynow_1.html', {
        'deliveries': formatted_deliveries,
        'segment': 'deliverynow_1'
    })



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


@login_required(login_url="/login/")
def managedeliverynowtraject(request):
    trucks = Truck.objects.all()
    return render(request, 'home/managedeliverynowtraject.html', {'trucks': trucks, 'segment': 'managedeliverynowtraject'})

@login_required(login_url="/login/")
def get_today_deliveries(request):
    if request.method == "GET":
        truck_name = request.GET.get('truck_name')
        today = timezone.now().date()

        # Filtrer les camions en fonction de l'utilisateur
        if request.user.is_superuser:
            # Superutilisateur voit tous les camions
            trucks = Truck.objects.all()
        else:
            # Staff voit seulement ses propres camions
            trucks = Truck.objects.filter(id_user=request.user)

        # Récupérer les livraisons pour le camion sélectionné et la date d'aujourd'hui
        deliveries = Delivery.objects.filter(
            truck__name_truck=truck_name,
            departure_date__date=today,
            truck__in=trucks  # Filtrer les livraisons par les camions accessibles
        ).values('departure_city', 'arrival_city').distinct()

        # Formater les données pour la réponse JSON
        cities = [
            {
                'departure_city': delivery['departure_city'],
                'arrival_city': delivery['arrival_city']
            }
            for delivery in deliveries
        ]

        return JsonResponse(cities, safe=False)



@login_required(login_url="/login/")
def add_chauffeur(request):
    if request.method == "POST":
        username = request.POST.get("name_chauffeur")
        email = request.POST.get("email_chauffeur")
        
        # Vérifier si l'email ou le username existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return redirect('add_chauffeur')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('add_chauffeur')
        
        # Générer un mot de passe aléatoire
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = make_password(password)

        # Créer l'utilisateur
        user = User.objects.create(
            username=username,
            email=email,
            password=hashed_password,
            is_superuser=False,
            is_staff=True,
            is_active=True
        )
        user.save()

        # Créer un profil pour stocker le mot de passe en clair
        Profile.objects.create(user=user, plain_password=password)

        messages.success(request, "Le chauffeur a été ajouté avec succès.")
        return redirect('add_chauffeur')

    users = User.objects.all()
    return render(request, 'home/add_chauffeur.html', {'users': users, 'today': datetime.now().date(), 'segment': 'add_chauffeur'})


@login_required(login_url="/login/")
def manage_chauffeurs(request):
    users = User.objects.filter(is_staff=True, is_superuser=False)
    user_data = []
    for user in users:
        profile = Profile.objects.get(user=user)
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'plain_password': profile.plain_password,  # Mot de passe en clair
            'date_joined': user.date_joined
        })
    return render(request, 'home/manage_chauffeurs.html', {
        'users': user_data,  # Passez les données au template
        'segment': 'manage_chauffeurs'
    })

@login_required(login_url="/login/")
def edit_chauffeur(request, chauffeur_id):
    # Récupérer le chauffeur à modifier
    chauffeur = get_object_or_404(User, id=chauffeur_id, is_staff=True, is_superuser=False)

    if request.method == "POST":
        # Remplir le formulaire avec les données POST et l'instance du chauffeur
        form = EditChauffeurForm(request.POST, instance=chauffeur)
        if form.is_valid():
            form.save()  # Enregistrer les modifications
            messages.success(request, "Le chauffeur a été modifié avec succès.")
            return redirect('manage_chauffeurs')
    else:
        # Afficher le formulaire pré-rempli avec les données actuelles du chauffeur
        form = EditChauffeurForm(instance=chauffeur)

    # Passer le formulaire au template
    context = {
        'form': form,
        'segment': 'edit_chauffeur'
    }
    return render(request, 'home/edit_chauffeur.html', context)
    
@login_required(login_url="/login/")
def delete_chauffeur(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_staff and not user.is_superuser:
        user.delete()
        messages.success(request, 'Chauffeur supprimé avec succès.')
    else:
        messages.error(request, 'Vous ne pouvez pas supprimer cet utilisateur.')
    return redirect('manage_chauffeurs')  # Redirigez vers la page de gestion des chauffeurs


@login_required(login_url="/login/")
def predict_delay(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)

    # Encoder les villes selon le mapping fourni
    ville_mapping = {
        "Casablanca": 1,
        "Rabat": 3,
        "Marrakech": 2,
        "Tanger": 5,
        "Agadir": 0
    }

    ville_depart = ville_mapping.get(delivery.departure_city, -1)
    ville_arrivee = ville_mapping.get(delivery.arrival_city, -1)

    if ville_depart == -1 or ville_arrivee == -1:
        return JsonResponse({'error': 'Ville de départ ou d\'arrivée non reconnue.'}, status=400)

    # Calculer la durée réelle en minutes
    duree_reelle = (delivery.arrival_date - delivery.departure_date).total_seconds() / 60

    # Préparer les données pour la prédiction
    input_data = pd.DataFrame({
        'Ville de depart': [ville_depart],
        'Ville d\'arrivee': [ville_arrivee],
        'Distance (km)': [0],  # Remplacez par la distance réelle si disponible
        'Poids (kg)': [delivery.tonnage],
        'Heure_depart': [delivery.departure_date.hour],
        'Heure_arrivee': [delivery.arrival_date.hour],
        'Weekend': [delivery.weekend],
        'Jour ferie': [delivery.jour_ferie],
        'Duree reelle (minutes)': [duree_reelle]
    })

    # Prédire le retard
    try:
        predicted_delay = retard_model.predict(input_data)[0]
        predicted_delay = int(predicted_delay)  # Convertir en entier
        return JsonResponse({'predicted_delay': predicted_delay})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)