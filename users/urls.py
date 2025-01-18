from django.urls import path

from .views import home, profile, RegisterView, dashboard, add_project, liste_projects, edit_project, delete_project, project_summary, gestion_equipements, modifier_equipement, supprimer_equipement,weather

urlpatterns = [
    path('', home, name='users-dashboard'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('dashboard/', dashboard, name='users-dashboard'),
    path('add_project/', add_project, name='users-add_project'),
    path('projects/', liste_projects, name='users-liste_projects'),
    path('projects/<int:project_id>/edit/', edit_project, name='users-edit_project'),
    path('projects/<int:project_id>/delete/', delete_project, name='users-delete_project'),
    path('projects/<int:project_id>/summary/', project_summary, name='users-project_summary'),
    path('equipements/', gestion_equipements, name='users-gestion_equipements'),
    path('equipements/<int:equipement_id>/modifier/', modifier_equipement, name='users-modifier_equipement'),
    path('equipements/<int:equipement_id>/supprimer/', supprimer_equipement, name='users-supprimer_equipement'),
    path('weather/', weather, name='users-weather'),


]
