from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)



#class Dimensionnement(models.Model):
 #   surface_habitable = models.FloatField("Surface habitable (m²)")
  #  hauteur_sous_plafond = models.FloatField("Hauteur sous plafond (m)")
   # volume_total = models.FloatField("Volume total (m³)")

    #def __str__(self):
     #   return f"Dimensionnement - {self.surface_habitable} m²"



class Project(models.Model):
    # Rubrique Installation
    surface_habitable = models.FloatField("Surface habitable (m²)")
    hauteur_sous_plafond = models.FloatField("Hauteur sous plafond (m)")
    volume_total = models.FloatField("Volume total (m³)")
    types_de_murs = models.CharField("Types de murs", max_length=50, choices=[
        ('béton', 'Béton'),
        ('brique', 'Brique'),
        ('bois', 'Bois'),
    ])
    coefficient_transmission_murs = models.FloatField("Coefficient de transmission thermique des murs (W/m²·K)",default=0.5)
    coefficient_transmission_toit = models.FloatField("Coefficient de transmission thermique du toit (W/m²·K)", default=0.5)
    coefficient_transmission_plancher = models.FloatField("Coefficient de transmission thermique du plancher (W/m²·K)", default=0.5)
    orientation = models.CharField("Orientation des fenêtres", max_length=10, choices=[
        ('Nord', 'Nord'),
        ('Sud', 'Sud'),
        ('Est', 'Est'),
        ('Ouest', 'Ouest'),
    ])
    epaisseur_des_isolants = models.FloatField("Épaisseur des isolants (mm)")
    facteur_transmission_solaire = models.FloatField("Facteur de transmission solaire (%)")
    surface_fenetres = models.FloatField("Surface totale des fenêtres (m²)",default=5)
    coefficient_transmission_vitrages = models.FloatField("Coefficient de transmission thermique des vitrages (W/m²·K)", default=0.5)
    taux_renouvellement_air = models.FloatField("Taux de renouvellement d’air (renouvellements/h)", default=2)
    type_ventilation = models.CharField(
        "Type de ventilation",
        max_length=25,  # Correction
        choices=[
            ('naturelle', 'Naturelle'),
            ('mécanique simple flux', 'Mécanique simple flux'),
            ('double flux', 'Double flux'),
        ], default='naturelle'
    )

    # Rubrique Usages Énergétiques
    temperature_hiver = models.FloatField("Température intérieure souhaitée (°C) en hiver")
    temperature_ete = models.FloatField("Température intérieure souhaitée (°C) en été")
    consommation_chauffage_climatisation = models.FloatField("Consommation moyenne pour le chauffage et la climatisation (kWh)")
    temperature_eau_chaude = models.FloatField("Température souhaitée de l’eau chaude (°C)")
    consommation_eau_chaude = models.FloatField("Consommation moyenne d’eau chaude par occupant (L/jour)")
    surface_eclairage = models.FloatField("Surface totale à éclairer (m²)", default=50)
    puissance_ampoules = models.FloatField("Puissance moyenne des ampoules (W)",default=10)
    duree_eclairage = models.FloatField("Durée quotidienne d’éclairage (h/jour)", default=8)

    # Liste des équipements électriques
    puissance_moyenne = models.FloatField("Puissance moyenne des équipements (W)")
    duree_utilisation = models.FloatField("Durée quotidienne d’utilisation des équipements (h/jour)")

    # Données Économiques
    prix_energie = models.FloatField("Prix de l’énergie (€/kWh)")
    prix_gaz = models.FloatField("Prix du gaz (€/kWh)", null=True, blank=True)
    budget_maximal = models.FloatField("Budget disponible (€)")

    # Priorités utilisateur
    reduction_couts_initiaux = models.BooleanField("Réduction des coûts initiaux", default=False)
    maximisation_independance_energetique = models.BooleanField("Maximisation de l’indépendance énergétique", default=False)
    optimisation_efficacite_energetique = models.BooleanField("Optimisation de l’efficacité énergétique", default=False)

    # Données Météorologiques
    temperature_exterieure_moyenne = models.FloatField("Température extérieure moyenne annuelle (°C)")
    duree_ensoleillement = models.FloatField("Durée moyenne d’ensoleillement par jour (h)")
    irradiation_solaire_annuelle = models.FloatField("Irradiation solaire journalière (kWh/m²)")



    # Méthodes de calcul
    def calcul_pertes_thermiques(self):
        delta_t = self.temperature_hiver - self.temperature_exterieure_moyenne
        pertes_murs = self.coefficient_transmission_murs * self.surface_habitable * delta_t
        pertes_toit = self.coefficient_transmission_toit * self.surface_habitable * delta_t
        pertes_plancher = self.coefficient_transmission_plancher * self.surface_habitable * delta_t
        pertes_air = 1.2 * 1005 * self.volume_total * delta_t * self.taux_renouvellement_air
        return pertes_murs + pertes_toit + pertes_plancher + pertes_air

    def calcul_gains_solaires(self):
        return (
            self.irradiation_solaire_annuelle *
            self.surface_fenetres *
            (self.facteur_transmission_solaire / 100)
        )

    def calcul_consommation_eclairage(self):
        return self.surface_eclairage * self.puissance_ampoules * self.duree_eclairage / 1000

    def __str__(self):
        return f"Projet : {self.surface_habitable} m² - {self.budget_maximal} €"

    def calcul_energy_total(self):
        """
        Calcul de l'énergie totale consommée par les équipements.
        Formule : Énergie totale = Puissance moyenne des équipements * Durée d'utilisation quotidienne
        """
        return self.puissance_moyenne * self.duree_utilisation

    def calcul_puissance_panneau(self):
        """
        Calcul de la puissance requise pour les panneaux solaires.
        Formule : Puissance_panneau = Puissance moyenne des équipements (W) /
                                       (Irradiation solaire annuelle (kWh/m²) * Rendement)
        """
        rendement = 0.22  # Rendement des panneaux solaires (22%)
        if self.irradiation_solaire_annuelle > 0:
            return self.puissance_moyenne / (self.irradiation_solaire_annuelle * rendement)
        else:
            return None  # Gérer les cas où l'irradiation est nulle ou manquante

    def calcul_puissance_moyenne(self):
        """
        Somme de la puissance moyenne de tous les équipements associés au projet.
        """
        return sum(equip.calcul_puissance_moyenne() for equip in self.equipements.all())


class Equipement(models.Model):
    nom = models.CharField("Nom de l'équipement", max_length=100)
    nombre = models.PositiveIntegerField("Nombre d'équipements")
    puissance_nominale = models.FloatField("Puissance nominale (W)")
    duree_moyenne_utilisation = models.FloatField("Durée moyenne d'utilisation (h/jour)")

    def puissance_totale(self):
        """
        Calcul de la puissance totale de cet équipement.
        """
        return self.nombre * self.puissance_nominale * self.duree_moyenne_utilisation

    def __str__(self):
        return f"{self.nom} - {self.nombre} unités"