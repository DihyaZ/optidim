from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from .models import Project
from django.http import HttpResponse
from .forms import ProjectForm
from django.shortcuts import get_object_or_404
from .forms import EquipementForm
from .models import Equipement
from django.db.models import F, Sum, FloatField
from .utils import get_weather_data, get_meteo_data, get_coordinates



def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})



@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')


def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le projet a été ajouté avec succès.")
            return redirect('users-liste_projects')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProjectForm()

    return render(request, 'users/add_project.html', {'form': form})

def liste_projects(request):
    projects = Project.objects.all()
    return render(request, 'users/liste_projects.html', {'projects': projects})

def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Le projet a été modifié avec succès.")
            return redirect('users-liste_projects')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProjectForm(instance=project)

    return render(request, 'users/edit_project.html', {'form': form, 'project': project})

def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
        return redirect('users-liste_projects')

    return render(request, 'users/delete_project.html', {'project': project})

def gestion_equipements(request):
    # Gestion du formulaire d'ajout d'équipement
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "L'équipement a été ajouté avec succès.")
            return redirect('users-gestion_equipements')  # Rechargement pour afficher l'équipement ajouté
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EquipementForm()

    # Calculer la puissance totale pour chaque équipement
    equipements = Equipement.objects.annotate(
        puissance_totale=F('nombre') * F('puissance_nominale') * F('duree_moyenne_utilisation')
    )

    # Calculer la somme des puissances totales
    somme_puissance_totale = equipements.aggregate(
        total=Sum('puissance_totale', output_field=FloatField())
    )['total'] or 0  # Si aucun équipement, la somme est 0

    return render(request, 'users/gestion_equipements.html', {
        'form': form,
        'equipements': equipements,
        'somme_puissance_totale': somme_puissance_totale,
    })
def modifier_equipement(request, equipement_id):
    equipement = get_object_or_404(Equipement, id=equipement_id)

    if request.method == 'POST':
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, "L'équipement a été modifié avec succès.")
            return redirect('users-gestion_equipements')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EquipementForm(instance=equipement)

    return render(request, 'users/modifier_equipement.html', {'form': form, 'equipement': equipement})

def supprimer_equipement(request, equipement_id):
    equipement = get_object_or_404(Equipement, id=equipement_id)

    if request.method == 'POST':
        equipement.delete()
        messages.success(request, "L'équipement a été supprimé avec succès.")
        return redirect('users-gestion_equipements')

    return render(request, 'users/supprimer_equipement.html', {'equipement': equipement})

def project_summary(request, project_id):
    """
    Vue pour afficher le résumé d'un projet spécifique avec ses calculs.
    """
    project = get_object_or_404(Project, id=project_id)
    context = {
        'project': project,
        'pertes_thermiques': project.calcul_pertes_thermiques(),
        'gains_solaires': project.calcul_gains_solaires(),
        'consommation_eclairage': project.calcul_consommation_eclairage(),
        'energy_total': project.calcul_energy_total(),
        'puissance_panneau': project.calcul_puissance_panneau(),
    }
    return render(request, 'users/project_summary.html', context)



# views.py

def weather(request):
    city = request.GET.get('city', 'Paris')  # Ville choisie par l'utilisateur ou 'Paris' par défaut

    # Récupérer les coordonnées de la ville choisie
    lat, lon = get_coordinates(city)

    # Si les coordonnées sont valides, obtenir les données météo journalières
    if lat and lon:
        meteo_data = get_meteo_data(lat, lon)
    else:
        meteo_data = None

    # Récupérer les données actuelles d'OpenWeather pour la ville
    weather_data = get_weather_data(city)

    # Calcul de la température moyenne pour chaque jour des données météorologiques
    if meteo_data:
        for day in meteo_data:
            # Calcul de la température moyenne
            temp_moyenne = (day['temp_max'] + day['temp_min']) / 2
            day['temp_moyenne'] = round(temp_moyenne, 1)

            # Conversion de la durée d'ensoleillement en heures
            # Calcul du nombre d'heures et de minutes
            hours = day['sunshine'] // 3600
            minutes = (day['sunshine'] % 3600) // 60
            day['sunshine_in_hours_minutes'] = f"{int(hours)}h {int(minutes)}m"

            # Conversion de l'irradiation solaire en kWh/m²
            day['irradiance_in_kWh'] = round(day['irradiation'] * 0.2778, 2)

    # Passer les données au template
    context = {
        'weather_data': weather_data,  # Température, humidité, vent...
        'meteo_data': meteo_data,      # Données détaillées sur les jours
        'city': city,
    }

    return render(request, 'users/weather.html', context)

