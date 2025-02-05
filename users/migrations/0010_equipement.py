# Generated by Django 4.1.2 on 2025-01-14 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_project_irradiation_solaire_annuelle'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name="Nom de l'équipement")),
                ('puissance_nominale', models.FloatField(verbose_name='Puissance nominale (W)')),
                ('nombre', models.IntegerField(default=1, verbose_name="Nombre d'équipements")),
                ('duree_moyenne_utilisation', models.FloatField(verbose_name='Durée moyenne d’utilisation (h/jour)')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipements', to='users.project')),
            ],
        ),
    ]
