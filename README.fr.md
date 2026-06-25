# Passerelle d'acquisition de données industrielles v1.0.0

## Qu'est-ce que c'est ?

Une **passerelle d'acquisition de données industrielles** en **un seul EXE, double-clic pour lancer, zéro dépendance, entièrement open-source et gratuite**.

Conçue pour les ingénieurs de terrain, le personnel IT d'usine et les petits intégrateurs de systèmes dans l'industrie manufacturière.

## Pourquoi ce projet ?

- Les passerelles commerciales coûtent plus de 1 000 € par unité — nous en avons créé une gratuite
- Les autres projets open-source nécessitent Docker, que les ingénieurs d'atelier ne savent pas utiliser
- La plupart des projets internationaux n'ont pas de documentation en chinois, rendant le dépannage difficile

## Comment utiliser ?

1. [Télécharger `FactoryLink.exe`](https://github.com/qinshihu/FactoryLink/releases/latest)

2. Double-cliquez pour lancer (une icône apparaîtra dans la barre d'état système en bas à droite)

![Icône de la barre d'état](industrial-gateway\images\1 (2).png)

3. Le navigateur ouvre automatiquement la page de configuration (par défaut `http://localhost:8000`)

![Page de configuration](industrial-gateway\images\1 (1).png)

4. Configurez l'IP de votre PLC, la table de points et l'adresse MQTT

  ![Configuration du périphérique](industrial-gateway\images\1 (4).png)

5. Cliquez sur "Démarrer l'acquisition" — c'est tout !

> Clic droit sur l'icône de la barre d'état pour : ouvrir la page de configuration, démarrer/arrêter l'acquisition, quitter le programme.
> 
> Le déploiement Docker est également pris en charge : [Guide de déploiement Docker](#déploiement-docker)

## Protocoles pris en charge

| Protocole | Modèles pris en charge | Bibliothèque |
|-----------|----------------------|--------------|
| Modbus TCP | Tous les appareils Modbus TCP standard | pymodbus 3.x |
| Modbus RTU | Tous les appareils Modbus RTU standard (série) | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0 (Python pur) |
| Mitsubishi MC | FX5U / Série Q / Série L | pymcprotocol |

## Fonctionnalités principales

- **EXE unique** : Double-clic pour lancer, aucun environnement d'exécution requis
- **Interface Web** : Configuration via navigateur, aucune connaissance en ligne de commande nécessaire
- **Données en temps réel** : Push WebSocket, données actualisées en temps réel
- **Transfert MQTT** : Transfert automatique des données collectées vers le serveur MQTT
- **Import Excel** : Import en masse des configurations de points depuis des feuilles Excel
- **Test de connexion** : Test de connectivité PLC en un clic
- **Reconnexion automatique** : Reconnexion automatique en cas de perte réseau avec backoff exponentiel
- **Démarrage automatique** : Configuration du démarrage Windows en un clic
- **Barre d'état système** : Fonctionne en arrière-plan, clic droit sur l'icône pour les opérations
- **Visualiseur de logs** : Consultez les logs d'acquisition directement dans l'interface Web avec filtrage par niveau
- **Rechargement à chaud** : Cliquez sur "Appliquer" après les modifications pour redémarrer automatiquement le collecteur
- **Sauvegarde automatique** : Génération automatique de `config.json.bak` à chaque sauvegarde
- **Gestion des conflits de port** : Basculement automatique vers 8001, 8002... si le port 8000 est occupé

## Aperçu de l'interface

| Page | Fonctions |
|------|-----------|
| **Accueil** | Liste des cartes de périphériques, affichage des données en temps réel, bouton démarrer/arrêter, état en ligne des périphériques, état de connexion MQTT |
| **Configuration** | Ajouter/modifier/supprimer des périphériques, configuration par protocole, CRUD de la table de points, import Excel/téléchargement de modèle, test de connexion |
| **Paramètres** | Configuration MQTT, intervalle de collecte, stratégie de reconnexion, démarrage automatique, visualiseur de logs (avec filtrage par niveau) |

## Format des données

### Topic de données MQTT

```
{topic_prefix}/{device_id}
```

Exemple : `factory/gateway-001/dev1`

### Charge utile MQTT

```json
{
  "gateway": "Passerelle Atelier 1",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "Température1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "Pression1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### Topic d'état

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "Connexion réussie",
  "timestamp": 1719123456789
}
```

- Valeurs de status : `online` (acquisition normale), `offline` (déconnecté), `error` (anomalie)
- Valeurs de quality : `good` (normal), `bad` (échec de lecture), `uncertain` (données suspectes)

## Types de données des points

| Type | Description | Octets |
|------|-------------|--------|
| bool | Booléen | 1 bit |
| int16 | Entier signé 16 bits | 2 |
| uint16 | Entier non signé 16 bits | 2 |
| int32 | Entier signé 32 bits | 4 |
| uint32 | Entier non signé 32 bits | 4 |
| float | Virgule flottante 32 bits | 4 |
| double | Virgule flottante 64 bits | 8 |

> Valeur réelle = Valeur brute × Coefficient + Décalage. Le coefficient et le décalage sont configurés dans les paramètres du point.

## Fichier de configuration

Toute la configuration est enregistrée dans `config.json` dans le même répertoire que l'EXE, sauvegardée automatiquement dans `config.json.bak` à chaque modification.

```json
{
  "gateway_name": "Passerelle Atelier 1",
  "devices": [
    {
      "id": "dev1",
      "name": "Siemens S7-1200",
      "protocol": "s7",
      "ip": "192.168.1.100",
      "rack": 0,
      "slot": 1,
      "enabled": true,
      "points": [
        {"name": "Température1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
      ]
    }
  ],
  "mqtt": {
    "host": "192.168.1.200",
    "port": 1883,
    "client_id": "gateway-001",
    "topic_prefix": "factory/gateway-001",
    "username": "",
    "password": "",
    "qos": 1,
    "enabled": true
  },
  "collect_interval": 1000,
  "reconnect": {
    "max_retries": 0,
    "base_delay": 1,
    "max_delay": 60
  }
}
```

- `collect_interval` : Intervalle de collecte en millisecondes, 1000 = une fois par seconde
- `reconnect.max_retries` : 0 = tentatives illimitées
- Intervalle de réessai : backoff exponentiel, 1s → 2s → 4s → 8s → 16s → 32s → 60s (plafond)

## Formats d'adresse des protocoles

### Modbus

| Plage d'adresses | Zone | Exemple |
|------------------|------|---------|
| 40001-49999 | Registres de maintien | `40001` |
| 30001-39999 | Registres d'entrée | `30001` |
| 10001-19999 | Entrées discrètes | `10001` |
| 00001-09999 | Bobines | `00001` |

### Siemens S7

| Format | Description | Exemple |
|--------|-------------|---------|
| DBx.DBDy | Double mot bloc DB (32 bits) | `DB1.DBD0` |
| DBx.DBXy.z | Bit bloc DB | `DB1.DBX8.0` |
| DBx.DBWy | Mot bloc DB (16 bits) | `DB1.DBW0` |
| Mx.y | Bit mémoire | `M0.0` |
| Ix.y | Bit d'entrée | `I0.0` |
| Qx.y | Bit de sortie | `Q0.0` |

> S7-1200/1500 : rack=0, slot=1 ; S7-300/400 : rack=0, slot=2

### Mitsubishi MC

| Format | Description | Exemple |
|--------|-------------|---------|
| Dxxxx | Registre de données | `D100` |
| Mxxxx | Relais interne | `M100` |
| Xx | Relais d'entrée | `X0` |
| Yx | Relais de sortie | `Y0` |
| Wxxxx | Registre de liaison | `W100` |

## Format du tableau Excel des points

| Nom du point | Adresse | Type de données | Coefficient | Décalage | Unité |
|-------------|---------|----------------|-------------|----------|-------|
| Température1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| Pression1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| État marche | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- La première ligne est l'en-tête (format fixe), les données commencent à la ligne 2
- Prend en charge les formats `.xlsx` et `.xls`
- Téléchargez le modèle depuis la page de configuration du périphérique

## Exécuter depuis les sources

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Compiler le frontend
cd frontend
npm install
npm run build
cd ..

# 4. Démarrer le backend
cd backend
python main.py
```

Ouvrez `http://localhost:8000` dans votre navigateur.

## Compiler en EXE

```bash
# S'assurer que le frontend est compilé
cd frontend && npm run build && cd ..

# Exécuter le script de compilation
build.bat
```

Sortie : `dist/FactoryLink.exe` (~25 Mo)

## Déploiement Docker

Si vous préférez ne pas utiliser l'EXE, vous pouvez utiliser Docker (adapté aux serveurs, PC industriels, Raspberry Pi).

### Démarrage rapide

```bash
# Récupérer l'image
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# Créer les répertoires pour la configuration et les logs
mkdir -p /opt/factorylink/{logs,config}

# Lancer le conteneur
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### Référence des paramètres

| Paramètre | Description |
|-----------|-------------|
| `-p 8000:8000` | Mapper le port de la page de configuration Web |
| `-v /opt/factorylink/config:/app/config` | Monter le répertoire de configuration (config.json stocké ici) |
| `-v /opt/factorylink/logs:/app/logs` | Monter le répertoire des logs |
| `--restart always` | Redémarrage automatique en cas d'échec du conteneur |

### Première utilisation

1. Après le démarrage du conteneur, ouvrez `http://ip-de-votre-serveur:8000` dans le navigateur
2. Configurez les périphériques PLC et MQTT
3. Cliquez sur "Démarrer l'acquisition"

> Remarque : La version Docker **ne prend pas en charge** l'icône de la barre d'état système et le démarrage automatique (fonctionnalités exclusives à Windows).

### Utiliser docker-compose

Créez `docker-compose.yml` :

```yaml
version: '3'
services:
  factorylink:
    image: registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
    container_name: factorylink
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
```

Démarrer :

```bash
docker-compose up -d
```

## Stack technique

- **Backend** : Python 3.11+ / FastAPI / WebSocket / uvicorn
- **Frontend** : Vue 3 / Vite / Element Plus / xlsx
- **Bibliothèques de protocole** : pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT** : paho-mqtt
- **Empaquetage** : PyInstaller 6.x (`--onefile --windowed`)
- **Barre d'état** : pystray + Pillow

## Structure du projet

```
FactoryLink/
├── backend/
│   ├── main.py              # Point d'entrée FastAPI (WebSocket, barre d'état, détection de port)
│   ├── config.py            # Gestion de la configuration (lecture/écriture, sauvegarde, thread-safe)
│   ├── logger.py            # Gestion des logs (rotation 10 Mo × 5, lecture API)
│   ├── schemas.py           # Modèles de données Pydantic
│   ├── collector/
│   │   ├── base.py          # Classe de base du collecteur (reconnexion avec backoff exponentiel, thread de reconnexion)
│   │   ├── modbus.py        # Modbus TCP/RTU (pymodbus)
│   │   ├── s7.py            # Siemens S7 (python-snap7 3.0)
│   │   └── mitsubishi.py    # Mitsubishi MC (pymcprotocol)
│   └── forwarder/
│       └── mqtt.py          # Transfert MQTT (paho-mqtt)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Framework de mise en page (navigation, logo, infos auteur)
│   │   ├── router.js        # Configuration des routes
│   │   └── views/
│   │       ├── Home.vue          # Page d'accueil (cartes périphériques, données temps réel, WebSocket)
│   │       ├── DeviceConfig.vue  # Configuration périphérique (CRUD, gestion points, import Excel)
│   │       └── Settings.vue      # Paramètres système (MQTT, collecte, reconnexion, démarrage auto, logs)
│   └── dist/                # Fichiers statiques compilés
├── build.bat                # Script de compilation PyInstaller
├── requirements.txt         # Liste des dépendances Python
├── Dockerfile               # Image Docker
└── README.md                # Ce fichier
```

## FAQ

**Q : Rien ne se passe quand je double-clique sur l'EXE ?**

R : Vérifiez la barre d'état système en bas à droite pour l'icône de la passerelle. Si le port est occupé, le programme changera automatiquement de port. Faites un clic droit sur l'icône et sélectionnez "Ouvrir la page de configuration".

**Q : Impossible de se connecter au PLC ?**

R : Cliquez d'abord sur "Tester la connexion" dans la page de configuration du périphérique pour vérifier l'IP, le port, les numéros de rack/slot. Siemens S7-1200/1500 utilise rack=0, slot=1 ; S7-300/400 utilise rack=0, slot=2.

**Q : MQTT ne reçoit pas de données ?**

R : Vérifiez que l'adresse et le port du serveur MQTT sont corrects et que MQTT est activé. Consultez les logs dans la page des paramètres système pour diagnostiquer les erreurs de connexion.

**Q : Comment importer des points en masse ?**

R : Téléchargez le modèle Excel depuis la page de configuration du périphérique, remplissez-le et importez-le. L'en-tête est fixe : Nom du point, Adresse, Type de données, Coefficient, Décalage, Unité.

**Q : Comment configurer le port série Modbus RTU ?**

R : Entrez directement le nom du port, par exemple `COM3`, `COM4`. Le débit en bauds par défaut est 9600, la parité par défaut est Aucune (N).

**Q : Quel intervalle de collecte est optimal ?**

R : La valeur par défaut est 1000 ms (1 seconde). Pour les PLC rapides, 500 ms est possible. Pour les appareils plus lents, 2000 ms+ est recommandé. Un intervalle trop court peut entraîner des timeouts de lecture.

---

Parce que 90 % des ingénieurs d'atelier n'ont pas besoin de cloud-native ou de Docker — ils veulent simplement un outil simple et facile à utiliser qui fait le travail.

---

## Licence

Ce projet est open-source sous la licence **Mozilla Public License 2.0 (MPL-2.0)**.

## Auteur

**Tan Ce** — Développeur indépendant | Explorateur IoT industriel

- 📝 Blog : [https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 Email : huawei_network@foxmail.com
- 💬 Compte officiel WeChat : **IT Online**

![QR Code WeChat](industrial-gateway\images\公众号背面.png)

---

[MPL-2.0](./LICENSE) © Tan Ce
