# Intégration Météo-Grenoble.com pour Home Assistant

<p align="center">
  <img src="hacs_logo.png" alt="Météo-Grenoble Home Assistant Logo" width="150" height="150">
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/tar-gezed/meteo-grenoble-home-assistant-integration?style=for-the-badge)](https://github.com/tar-gezed/meteo-grenoble-home-assistant-integration/releases)
[![License](https://img.shields.io/github/license/tar-gezed/meteo-grenoble-home-assistant-integration?style=for-the-badge)](LICENSE)
[![Donate](https://img.shields.io/badge/Donate-Météo--Grenoble-blue?style=for-the-badge)](https://www.meteo-grenoble.com/)


Cette intégration personnalisée pour Home Assistant permet de récupérer en temps réel les données météorologiques locales, les prévisions à 9 jours et les bulletins de vigilance de la station météo professionnelle de Grenoble, issue du site de référence [meteo-grenoble.com](https://www.meteo-grenoble.com/).

---

## 🌟 Fonctionnalités

L'intégration extrait les données directement depuis le flux Next.js RSC (React Server Components) de meteo-grenoble.com afin d'offrir une précision maximale et un ensemble très riche d'entités :

*   **Entité Météo (`weather`)** : Une entité météo standard supportant les prévisions quotidiennes sur 9 jours avec des icônes adaptées dynamiquement en fonction du créneau horaire de la journée.
*   **Capteurs Temps Réel (`sensor`)** : Température, pression, humidité relative, humidex (indice et sensation), température ressentie (windchill), vitesse du vent, direction cardinale, rafales et vent maximum.
*   **Prévisions par Tranche Horaire** : Capteurs dédiés pour les tranches de la journée d'aujourd'hui (*Matin*, *Après-midi*, *Soir*, *Nuit*) avec température, état et comparaison avec la veille.
*   **Pluie dans l'heure** : Capteur détaillé indiquant l'état général de la pluie pour l'heure à venir, accompagné des données brutes par créneaux en attributs.
*   **Vigilances Météo (`binary_sensor`)** : 8 capteurs binaires représentant les vigilances spécifiques émises (Canicule, Gel, Grand Froid, Neige, Orage, Pluie-Inondation, Vent Fort, Verglas).
*   **Informations Générales & Alertes** : Alerte Flash météo (avec résumé textuel nettoyé du HTML), Saint du jour, isotherme 0°C, écart de température par rapport aux normales saisonnières, et indice de fiabilité des prévisions.

---

## 🚀 Installation

### Option 1 : Via HACS (Recommandé)

1.  Assurez-vous que [HACS](https://hacs.xyz/) est installé sur votre instance Home Assistant.
2.  Accédez à **HACS** > **Intégrations**.
3.  Cliquez sur les trois petits points en haut à droite et sélectionnez **Dépôts personnalisés** (*Custom repositories*).
4.  Entrez l'URL du dépôt : `https://github.com/tar-gezed/meteo-grenoble-home-assistant-integration`
5.  Sélectionnez la catégorie **Intégration** et cliquez sur **Ajouter**.
6.  Recherchez **Météo-Grenoble.com** dans le magasin HACS et cliquez sur **Télécharger**.
7.  Redémarrez Home Assistant.

### Option 2 : Installation Manuelle

1.  Téléchargez l'archive `.zip` de la dernière version à partir de la page des [Releases](https://github.com/tar-gezed/meteo-grenoble-home-assistant-integration/releases).
2.  Extrayez le dossier `custom_components/meteo_grenoble/` dans le dossier de configuration de votre Home Assistant (généralement `/config/custom_components/`).
3.  Vérifiez que la structure ressemble à ceci :
    ```text
    config/
    └── custom_components/
        └── meteo_grenoble/
            ├── __init__.py
            ├── binary_sensor.py
            ├── config_flow.py
            ├── const.py
            ├── coordinator.py
            ├── manifest.json
            ├── parser.py
            ├── picto.py
            ├── sensor.py
            └── weather.py
    ```
4.  Redémarrez Home Assistant.

---

## ⚙️ Configuration

L'intégration se configure entièrement via l'interface utilisateur de Home Assistant :

1.  Allez dans **Paramètres** > **Appareils et services**.
2.  Cliquez sur **Ajouter l'intégration** en bas à droite.
3.  Recherchez **Météo-Grenoble.com**.
4.  Validez. L'intégration s'initialise automatiquement sans demander d'informations complémentaires.

> [!NOTE]
> Cette intégration est configurée en mode singleton. Une seule instance peut être ajoutée à Home Assistant.

---

## 📊 Entités et Formats de Données

L'intégration crée un unique appareil nommé **Météo-Grenoble.com** contenant les entités suivantes :

### 🌤️ Entité Météo (`weather.meteo_grenoble_com`)

L'entité principale synthétise les conditions courantes et expose les prévisions journalières sur 9 jours.

*   **État** : La condition météo courante (parmi : `sunny`, `clear-night`, `partlycloudy`, `cloudy`, `fog`, `rainy`, `pouring`, `snowy-rainy`, `snowy`, `lightning-rainy`).
    *   *Note technique* : La condition actuelle est déterminée dynamiquement selon l'heure courante de la journée en associant le pictogramme de la tranche horaire correspondante : **Matin** (06h - 12h), **Après-midi** (12h - 18h), **Soir** (18h - 22h), ou **Nuit** (22h - 06h).
*   **Attributs d'état courants** :
    *   `temperature` : Température actuelle en °C (provenant de la station temps réel ou repli sur la température actuelle estimée).
    *   `humidity` : Humidité relative en % (de la station).
    *   `wind_speed` : Vitesse du vent en km/h.
    *   `wind_bearing` : Direction du vent convertie en degrés (ex: `Sud-Ouest` $\rightarrow 225^\circ$).
    *   `pressure` : Pression atmosphérique en hPa.
    *   `picto_code` : Code pictogramme brut de meteo-grenoble.com (ex: `1` pour ciel clair, `41` pour nuageux avec éclaircies, etc.).
    *   `picto_description` : Description en clair associée au pictogramme (ex: *"Ciel nuageux - les éclaircies et les nuages se partagent le ciel - pas de pluie"*).
*   **Service de prévision (`forecast`)** (Retourne une liste de 9 jours de prévisions) :
    *   `datetime` : Date de la prévision au format ISO (ex: `"2026-06-21T00:00:00+00:00"`).
    *   `native_temperature` : Température maximale prévue pour la journée en °C.
    *   `native_templow` : Température minimale prévue en °C.
    *   `native_precipitation` : Cumul de précipitations prévu sur 24 heures en mm.
    *   `precipitation_probability` : Probabilité de pluie en %.
    *   `condition` : Condition globale de la journée (basée sur le pictogramme de l'après-midi).
    *   `description` : Commentaire de l'expert météo pour la journée (ex: *"Soleil prédominant malgré quelques bourgeonnements sur les reliefs"*).
    *   `picto_description` : Description textuelle du pictogramme choisi pour la journée.
    *   `temp_gap` : Écart de la température par rapport aux normales saisonnières en °C.

---

### 🌡️ Capteurs Météo (`sensor`)

Tous les capteurs ci-dessous ont pour préfixe d'ID d'entité `sensor.meteo_grenoble_com_`.

| Nom de l'entité | ID de l'entité (`sensor.`) | Unité | Classe d'appareil | Classe d'état | Description / Attributs |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Température** | `meteo_grenoble_com_temperature` | °C | `temperature` | `measurement` | Température actuelle à la station de Grenoble. |
| **Humidex** | `meteo_grenoble_com_humidex` | — | — | `measurement` | Indice d'inconfort lié à la chaleur combinée à l'humidité.<br>**Attributs :** `sensation` (Interprétation en clair). |
| **Humidex - Sensation** | `meteo_grenoble_com_humidex_sensation` | — | — | — | Interprétation directe de l'humidex (ex: *"Sensation de bien-être"* ou *"Petit inconfort"*). |
| **Ressenti au vent** | `meteo_grenoble_com_ressenti_au_vent` | °C | `temperature` | `measurement` | Indice de refroidissement éolien (Windchill). |
| **Humidité** (🔇) | `meteo_grenoble_com_humidite` | % | `humidity` | `measurement` | Taux d'humidité relative de l'air. |
| **Vitesse du vent** | `meteo_grenoble_com_vitesse_du_vent` | km/h | `wind_speed` | `measurement` | Vitesse moyenne actuelle du vent. |
| **Direction du vent** | `meteo_grenoble_com_direction_du_vent` | — | — | — | Direction cardinale actuelle du vent (ex: *"Nord-Nord-Ouest"*). |
| **Rafales** (🔇) | `meteo_grenoble_com_rafales` | km/h | `wind_speed` | `measurement` | Vitesse maximale des rafales de vent actuelles. |
| **Vent max depuis 00h** (🔇) | `meteo_grenoble_com_vent_max_depuis_00h` | km/h | `wind_speed` | `measurement` | Vitesse de vent maximale mesurée depuis minuit. |
| **Pression** (🔇) | `meteo_grenoble_com_pression` | hPa | `atmospheric_pressure` | `measurement` | Pression atmosphérique actuelle mesurée en hPa. |
| **Pluie dans l'heure** | `meteo_grenoble_com_pluie_dans_l_heure` | — | — | — | Résumé de la prévision de pluie (ex: *"Temps sec"*).<br>**Attributs :** `forecast` (liste de 9 créneaux contenant l'horodatage `time`, le niveau de pluie `rain` et la description `desc`). |
| **Saint du jour** | `meteo_grenoble_com_saint_du_jour` | — | — | — | Saint célébré aujourd'hui.<br>**Attributs :** `gender` (Genre grammatical du prénom : `m` ou `f`). |
| **Isotherme 0°C** | `meteo_grenoble_com_isotherme_0_c` | m | — | — | Altitude limite à laquelle la température atteint 0°C. |
| **Fiabilité** | `meteo_grenoble_com_fiabilite` | % | — | `measurement` | Fiabilité de la prévision du jour évaluée par le météorologue. |
| **Alerte Flash** | `meteo_grenoble_com_alerte_flash` | — | — | — | Niveau d'alerte météo flash actif (ex: *"Pas d'alerte"*, *"Vigilance Orange"*).<br>**Attributs :** `text` (bulletin d'alerte nettoyé de son HTML), `updated_at`, `level` (code numérique 0-4). |
| **Écart de temp. de saison** | `meteo_grenoble_com_ecart_de_temperature_de_saison` | °C | — | `measurement` | Écart de température d'aujourd'hui comparé aux normales saisonnières. |
| **Description météo du jour** | `meteo_grenoble_com_description_meteo_du_jour` | — | — | — | Commentaire textuel complet du prévisionniste pour la journée. |
| **Dernière mise à jour** | `meteo_grenoble_com_derniere_mise_a_jour` | ISO | `timestamp` | — | Horodatage de la dernière actualisation des données par la station. |

*(🔇) Indique que l'entité est désactivée par défaut dans Home Assistant. Vous pouvez l'activer manuellement dans les options de l'entité si nécessaire.*

#### 🕒 Capteurs détaillés des tranches de la journée (Aujourd'hui)
Ces capteurs permettent de connaître à l'avance le comportement de la météo pour chaque moment clé de la journée.

*   `sensor.meteo_grenoble_com_meteo_matin` (Matin)
*   `sensor.meteo_grenoble_com_meteo_apres_midi` (Après-midi)
*   `sensor.meteo_grenoble_com_meteo_soir` (Soir)
*   `sensor.meteo_grenoble_com_meteo_nuit` (Nuit)

Chacune de ces entités a pour valeur d'état principale la **température prévue** (en °C) pour la période correspondante, et expose les attributs suivants :
*   `picto_code` : Le code pictogramme associé à cette tranche horaire.
*   `condition` : La condition météo au format standard Home Assistant (ex: `partlycloudy`).
*   `picto_description` : La description en français (ex: *"Ciel peu nuageux"*).
*   `veille_temp` : La température qui a été enregistrée la veille pour cette même tranche (permet de visualiser facilement les variations thermiques d'un jour à l'autre).

---

### ⚠️ Vigilances Météo (`binary_sensor`)

L'intégration génère des capteurs binaires pour suivre les vigilances locales émises pour Grenoble. L'état d'un capteur passe à `on` en cas de vigilance active.
Tous les capteurs ci-dessous ont pour préfixe d'ID d'entité `binary_sensor.meteo_grenoble_com_vigilance_`.

| Nom de l'entité | ID de l'entité | Classe d'appareil | Description |
| :--- | :--- | :---: | :--- |
| **Vigilance Canicule** | `vigilance_canicule` | `heat` | Alerte aux fortes chaleurs ou canicule. |
| **Vigilance Grand Froid** | `vigilance_grand_froid` | `cold` | Alerte aux températures extrêmement basses. |
| **Vigilance Gel** | `vigilance_gel` | `cold` | Alerte de gelées au sol. |
| **Vigilance Pluie Inondation** | `vigilance_pluie_inondation` | `moisture` | Risque de fortes pluies ou crues/inondations. |
| **Vigilance Neige** | `vigilance_neige` | `safety` | Risque de chutes de neige ou d'accumulation. |
| **Vigilance Verglas** | `vigilance_verglas` | `safety` | Risque de pluies verglaçantes et routes glissantes. |
| **Vigilance Orage** | `vigilance_orage` | `safety` | Risque d'orages locaux ou généralisés. |
| **Vigilance Vent Fort** | `vigilance_vent_fort` | `safety` | Alerte aux vents violents ou tempête. |

---

## 🎨 Exemples de Cartes Lovelace

### 1. Carte Météo Standard
Vous pouvez utiliser la carte météo native de Home Assistant pour afficher les prévisions de Grenoble :

```yaml
type: weather-forecast
entity: weather.meteo_grenoble_com
name: Météo Grenoble
show_forecast: true
```

### 2. Visualisation de la pluie dans l'heure (Card Lovelace-hourly-weather)

L'entité météo principale (`weather.meteo_grenoble_com`) ne fournit que des prévisions quotidiennes (sur 9 jours). Pour visualiser la prévision de pluie dans l'heure (qui est découpée en 9 intervalles de 5 à 10 minutes) sous forme de barre de couleur avec la carte personnalisée [`lovelace-hourly-weather`](https://github.com/decompil3d/lovelace-hourly-weather), il faut créer une entité météo virtuelle de type "Template".

Cette entité virtuelle va convertir les intensités de pluie du capteur en conditions standards (Sec $\rightarrow$ `sunny`/`clear-night`, Faible $\rightarrow$ `rainy`, Modérée $\rightarrow$ `pouring`, Forte $\rightarrow$ `lightning-rainy`) et adapter l'icône selon qu'il fasse jour ou nuit.

#### Étape 1 : Ajouter le Template dans `configuration.yaml`
Ajoutez le code suivant dans votre fichier `configuration.yaml` :

```yaml
# Météo-Grenoble - Pluie dans la prochaine heure
template:
  - weather:
      - name: "Météo Grenoble Pluie dans l'heure"
        unique_id: meteo_grenoble_pluie_dans_l_heure
        temperature_unit: "°C"
        condition: >
          {% set rain_val = state_attr('sensor.meteo_grenoble_com_pluie_dans_l_heure', 'forecast') %}
          {% if rain_val and rain_val|length > 0 %}
            {% if rain_val[0].rain == 1 %}
              {{ 'sunny' if is_state('sun.sun', 'above_horizon') else 'clear-night' }}
            {% elif rain_val[0].rain == 2 %}
              rainy
            {% elif rain_val[0].rain == 3 %}
              pouring
            {% else %}
              lightning-rainy
            {% endif %}
          {% else %}
            unknown
          {% endif %}
        temperature: "{{ states('sensor.meteo_grenoble_com_temperature') | float(0) }}"
        humidity: "{{ states('sensor.meteo_grenoble_com_humidity') | float(0) }}"
        forecast_hourly: >
          {% set rain_data = state_attr('sensor.meteo_grenoble_com_pluie_dans_l_heure', 'forecast') %}
          {% set is_day = is_state('sun.sun', 'above_horizon') %}
          {% if rain_data %}
            {% set ns = namespace(res=[]) %}
            {% for item in rain_data %}
              {% set cond = 'sunny' if is_day else 'clear-night' %}
              {% if item.rain == 2 %}
                {% set cond = 'rainy' %}
              {% elif item.rain == 3 %}
                {% set cond = 'pouring' %}
              {% elif item.rain == 4 %}
                {% set cond = 'lightning-rainy' %}
              {% endif %}
              {% set ns.res = ns.res + [{
                'datetime': item.time,
                'condition': cond,
                'precipitation_probability': (0 if item.rain == 1 else (30 if item.rain == 2 else (60 if item.rain == 3 else 90)))
              }] %}
            {% endfor %}
            {{ ns.res }}
          {% else %}
            []
          {% endif %}
```

Rechargez ensuite les **Entités de modèle** via les *Outils de développement* de Home Assistant (ou redémarrez-le).

#### Étape 2 : Configurer la carte Lovelace
Ajoutez ensuite la carte sur votre tableau de bord avec cette configuration :

```yaml
type: custom:hourly-weather
entity: weather.meteo_grenoble_pluie_dans_l_heure
num_segments: 9
name: Grenoble - Pluie dans l'heure
show_precipitation_probability: true
hide_temperatures: true
colors:
  sunny: "#a5d6a7"            # Vert (Sec en journée - Icône Soleil)
  clear-night: "#a5d6a7"      # Vert (Sec en soirée - Icône Lune)
  rainy: "#90caf9"            # Bleu ciel (Pluie faible)
  pouring: "#42a5f5"          # Bleu modéré (Pluie modérée)
  lightning-rainy: "#1565c0"  # Bleu foncé (Pluie forte)
```

### 3. Affichage d'un bulletin d'alerte flash (Markdown conditionnel)
Affichez dynamiquement un encart d'alerte uniquement si une vigilance flash est en cours (Vigilance Jaune, Orange ou Rouge) :

```yaml
type: conditional
conditions:
  - entity: sensor.meteo_grenoble_com_alerte_flash
    state_not: Pas d'alerte
card:
  type: markdown
  title: ⚠️ Alerte Météo Flash !
  content: >
    **Statut :** {{ states('sensor.meteo_grenoble_com_alerte_flash') }}
    
    **Bulletin :** {{ state_attr('sensor.meteo_grenoble_com_alerte_flash', 'text') }}
    
    *Mis à jour le : {{ state_attr('sensor.meteo_grenoble_com_alerte_flash', 'updated_at') }}*
```

### 4. Carte météo avancée (Platinum Weather Card)

Pour un affichage très complet et esthétique similaire à celui du site internet (incluant le bandeau d'alerte orange/rouge, le saint du jour, la pluie dans l'heure et l'indice humidex), vous pouvez installer la carte personnalisée [Platinum Weather Card](https://github.com/tommyjlong/platinum-weather-card) via HACS.

Cette carte exploite de façon optimale les entités spécifiques de notre intégration :
*   **Bulletin de vigilance (Alerte Flash)** : S'affiche sous forme de bandeau d'alerte en haut de la carte.
*   **Dernière mise à jour** : Affiche l'heure exacte d'actualisation de la station physique.
*   **Slots personnalisés (Custom slots)** : Permettent d'ajouter le saint du jour, la pluie dans l'heure, l'indice Humidex et le ressenti Humidex dans la grille d'informations.

#### Code de configuration Lovelace (YAML)

Ajoutez une carte de type **Manuel** sur votre tableau de bord et collez la configuration ci-dessous :

```yaml
type: custom:platinum-weather-card
card_config_version: 8
daily_extended_forecast_days: 9
daily_forecast_days: 9
daily_forecast_layout: vertical
daily_extended_name_attr: description
daily_extended_use_attr: true
forecast_type: daily
option_show_overview_decimals: true
option_show_overview_separator: true
overview_layout: complete
section_order:
  - overview
  - extended
  - slots
  - daily_forecast
show_section_daily_forecast: true
show_section_extended: true
show_section_overview: true
show_section_slots: true
text_card_title: Météo Grenoble
text_update_time_prefix: "Mise à jour :"
update_time_use_attr: false
weather_entity: weather.meteo_grenoble_com

# Horodatage et bulletin vigilance
entity_update_time: sensor.meteo_grenoble_com_derniere_mise_a_jour
entity_extended: sensor.meteo_grenoble_com_alerte_flash
extended_use_attr: true
extended_name_attr: text

# Données actuelles
entity: weather.meteo_grenoble_com
entity_temperature: sensor.meteo_grenoble_com_temperature
entity_apparent_temp: sensor.meteo_grenoble_com_ressenti_au_vent
entity_summary: sensor.meteo_grenoble_com_description_meteo_du_jour

# Prévisions à 9 jours
entity_forecast_icon: weather.meteo_grenoble_com
entity_forecast_icon_1: weather.meteo_grenoble_com
entity_forecast_max: weather.meteo_grenoble_com
entity_forecast_max_1: weather.meteo_grenoble_com
entity_forecast_min: weather.meteo_grenoble_com
entity_forecast_min_1: weather.meteo_grenoble_com
entity_extended_1: weather.meteo_grenoble_com
entity_summary_1: weather.meteo_grenoble_com
entity_pop_1: weather.meteo_grenoble_com
entity_pos_1: weather.meteo_grenoble_com

# Disposition des slots de données (Colonnes gauche & droite)
slot_l1: custom1        # Saint du jour
slot_l2: custom2        # Pluie dans l'heure
slot_l3: wind           # Vitesse et direction du vent
slot_l4: sun            # Repli par défaut -> Affiche la Pression (NaNhPa si non fournie)
slot_l5: sun            # Repli par défaut -> Affiche le prochain événement solaire (sun_next)
slot_l6: remove
slot_l7: remove
slot_l8: remove

slot_r1: custom3        # Indice Humidex
slot_r2: custom4        # Sensation Humidex
slot_r3: forecast_max   # Température maximale prévue pour aujourd'hui
slot_r4: forecast_min   # Température minimale prévue pour aujourd'hui
slot_r5: sun            # Repli par défaut -> Affiche l'événement solaire suivant (sun_following)
slot_r6: remove
slot_r7: remove
slot_r8: remove

# Entités pour le vent et le soleil
entity_wind_speed: sensor.meteo_grenoble_com_vitesse_du_vent
entity_wind_bearing: sensor.meteo_grenoble_com_direction_du_vent
entity_sun: sun.sun

# Définition des informations personnalisées
custom1_icon: mdi:hands-pray
custom1_units: ""
custom1_value: sensor.meteo_grenoble_com_saint_du_jour

custom2_icon: mdi:weather-rainy
custom2_units: ""
custom2_value: sensor.meteo_grenoble_com_pluie_dans_l_heure

custom3_icon: mdi:thermometer-water
custom3_units: ""
custom3_value: sensor.meteo_grenoble_com_humidex

custom4_icon: mdi:comment-alert
custom4_units: ""
custom4_value: sensor.meteo_grenoble_com_humidex_sensation

grid_options:
  columns: full
  rows: 4
```

#### 💡 Astuces de configuration (Éviter les valeurs "NaN")

La station météo en temps réel de Grenoble ne transmettant pas certaines données (comme l'humidité relative actuelle, la pression atmosphérique ou les rafales de vent) :
1. **Éviter `Gust NaN`** : Ne renseignez pas le champ `entity_wind_gust` dans la configuration. Ainsi, seul le vent moyen sera affiché (ex: `5 km/h`) sans essayer d'afficher des rafales inexistantes.
2. **Nettoyer les slots vides** : Assurez-vous d'avoir explicitement configuré sur `remove` les slots que vous n'utilisez pas afin que la carte ne tente pas d'afficher de données par défaut non disponibles (comme `pressure` qui afficherait `NaNhPa`).
3. **Configuration du Soleil** : Plutôt que d'utiliser la valeur `sun` (qui s'appuie sur le comportement de repli par défaut de la carte et peut charger la pression sur `slot_l4`), il est recommandé de déclarer explicitement `sun_next` (prochain événement solaire) et `sun_following` (événement solaire suivant) sur vos slots (par exemple `slot_l5: sun_next` et `slot_r5: sun_following`), en réglant `slot_l4` sur `remove`.

---


## 🛠️ Fonctionnement Technique et Crawling

Cette intégration a été conçue pour respecter le fonctionnement du site [meteo-grenoble.com](https://www.meteo-grenoble.com/) tout en assurant une mise à jour efficace.

1.  **Format RSC (React Server Components)** : Le site web utilise le framework Next.js. Au lieu d'analyser du code HTML lourd et instable par web-scraping classique, l'intégration effectue une requête HTTP `GET` avec le header spécifique `"RSC": "1"`. Le serveur retourne un flux de données structuré très léger.
2.  **Parser robuste** : Le fichier `parser.py` traite ligne par ligne ce flux Next.js RSC pour extraire de manière récursive les objets JSON contenant les prévisions de l'expert (`forecasts`), les relevés en temps réel de la station (`realtime`) et le radar de pluie (`rain`).
3.  **Gestion du Polling** :
    *   L'intervalle de rafraîchissement est fixé à **15 minutes** (défini dans `const.py` par `UPDATE_INTERVAL`).
    *   Conformément aux directives de développement de Home Assistant, cet intervalle n'est pas modifiable par l'utilisateur afin de ne pas surcharger les serveurs de meteo-grenoble.com.
4.  **Device Registry & Classes** : Toutes les entités sont rattachées à un appareil unique à l'aide d'un `CoordinatorEntity`, garantissant une synchronisation parfaite des états et évitant des requêtes HTTP redondantes.

---

## 🧪 Tests Unitaires en Local

Le projet intègre une suite de tests unitaires pour valider le comportement du parseur RSC, le mappage des pictogrammes et l'extraction des alertes.

### 1. Fonctionnement des tests
Les tests du parseur sont indépendants du framework Home Assistant. Ils se basent sur des **fixtures hors-ligne** (extraits textuels réels de flux RSC enregistrés localement dans `tests/components/meteo_grenoble/fixtures/`). Cela permet de valider le code d'analyse de manière déconnectée, sans dépendance réseau et sans solliciter les serveurs de meteo-grenoble.com.

### 2. Lancer les tests du parseur (Sans dépendance)
Vous pouvez exécuter les tests du parseur directement avec le moteur de test natif de Python (`unittest`), sans avoir besoin d'installer Home Assistant :

```bash
python -m unittest tests/components/meteo_grenoble/test_parser.py
```

### 3. Lancer la suite de tests complète (Avec dépendances)
Les autres fichiers de test (`test_init.py`, `test_config_flow.py`) valident l'intégration dans l'écosystème de Home Assistant et nécessitent d'exécuter les tests dans un environnement virtuel où Home Assistant et ses dépendances de développement (`pytest`, etc.) sont installés :

```bash
# Activation de votre environnement virtuel de développement
pytest tests/components/meteo_grenoble/
```

---
## 🐞 Résolution des problèmes et Debugging

Si vous rencontrez un problème avec l'intégration, vous pouvez activer les logs de débogage dans votre fichier `configuration.yaml` :

```yaml
logger:
  default: warning
  logs:
    custom_components.meteo_grenoble: debug
```

Une fois les logs activés, redémarrez Home Assistant et observez le fichier `home-assistant.log` pour identifier les éventuelles erreurs de connexion ou d'analyse du flux.

---

## 📄 Licence & Crédits

*   **Données** : Les données météo appartiennent exclusivement au site [Météo-Grenoble.com](https://www.meteo-grenoble.com/) et à ses prévisionnistes. Pensez à visiter leur site pour soutenir leur travail de prévision locale bénévole et professionnel.
*   **Intégration** : Développée par [tar-gezed](https://github.com/tar-gezed) et distribuée sous licence Apache 2.0.
