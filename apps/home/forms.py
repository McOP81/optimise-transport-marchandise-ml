from django import forms
from .models import Truck,Delivery
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        fields = ['name_truck', 'registration_number', 'model', 'location', 'phone', 'tonnage', 'insurance_date', 'gray_card_date']

        widgets = {
            'name_truck': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name Truck'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Model'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+212 777111106'}),
            'tonnage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Tonnage (Kg)'}),
            'insurance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gray_card_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_name_truck(self):
        name_truck = self.cleaned_data.get('name_truck')
        query = Truck.objects.filter(name_truck=name_truck)        
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)        
        if query.exists():
            raise forms.ValidationError("Le nom de ce camion existe déjà.")
        return name_truck

    def clean_registration_number(self):
        registration_number = self.cleaned_data.get('registration_number')
        query = Truck.objects.filter(registration_number=registration_number)        
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)        
        if query.exists():
            raise forms.ValidationError("Un camion portant ce numéro d'immatriculation existe déjà.")
        return registration_number
        

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            'truck', 'departure_city', 'arrival_city', 'departure_date', 
            'arrival_date', 'phone_number', 'tonnage','weekend','jour_ferie', 'loaded_trip'
        ]
        widgets = {
            'truck': forms.Select(attrs={'class': 'form-control'}),
            'departure_city': forms.Select(attrs={'class': 'form-control'}),
            'arrival_city': forms.Select(attrs={'class': 'form-control'}),
            'departure_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'arrival_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0XXXXXXXXX'}),
            'tonnage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tonnage (Kg)'}),
            'weekend': forms.Select(attrs={'class': 'form-control', 'placeholder': 'weekend'}),
            'jour_ferie': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Jour ferie'}),
            'loaded_trip': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        arrival_date = cleaned_data.get('arrival_date')
        tonnage = cleaned_data.get('tonnage')
        truck = cleaned_data.get('truck')

        if departure_date and arrival_date and arrival_date < departure_date:
            raise forms.ValidationError({
                'arrival_date': "La date d'arrivée doit être postérieure ou égale à la date de départ."
            })

        if truck and tonnage and tonnage > truck.tonnage:
            raise forms.ValidationError({
                'tonnage': "Le tonnage de la livraison doit être inférieur ou égal au tonnage du camion."
            })

        return cleaned_data

class EditChauffeurForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Laisser vide pour ne pas modifier'}),
        required=False,
        label="Mot de passe"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Nom du chauffeur',
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nom du chauffeur'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Hacher le mot de passe
        if commit:
            user.save()
        return user