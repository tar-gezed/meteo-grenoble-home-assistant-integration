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
Si vous utilisez la carte personnalisée populaire `lovelace-hourly-weather` (disponible sur HACS), voici une configuration idéale exploitant les attributs détaillés du capteur de pluie dans l'heure :

```yaml
type: custom:hourly-weather
entity: weather.meteo_grenoble_com
name: Pluie dans l'heure (Grenoble)
icons: true
num_segments: '12'
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
