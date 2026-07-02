# Radar à ultrasons

Un radar à ultrasons qui balaie de 0 à 180° et affiche ses mesures en temps réel sur l'ordinateur, sous la forme d'un nuage de points façon écran radar.

Le projet se compose de deux programmes qui communiquent par la liaison série USB. Un programme embarqué sur une carte Arduino Uno pilote le servomoteur et le capteur, puis envoie chaque mesure sur le port série. Un script Python tournant sur l'ordinateur reçoit ces mesures et les dessine.

## Aperçu

<!-- Ajoute ici une capture ou un GIF du radar en action, c'est ce qui vend le mieux ce genre de projet -->
<!-- Exemple : ![Aperçu du radar](docs/apercu.gif) -->

## Fonctionnement

L'Arduino fait tourner le servomoteur degré par degré. À chaque position, il déclenche une mesure du capteur à ultrasons, puis envoie sur le port série une ligne au format `angle,distance`. Il ne se préoccupe pas de savoir si quelqu'un l'écoute, il émet en continu.

Le script Python ouvre le port série, lit ces lignes dans un fil d'exécution séparé pour ne jamais bloquer l'affichage, et dessine avec pygame une grille de radar, un faisceau qui balaie avec une traînée, et un nuage de points colorés selon la distance qui s'estompent avec le temps.

## Matériel

| Composant | Rôle |
|-----------|------|
| Arduino Uno R3 | Pilotage du balayage et de la mesure |
| Capteur à ultrasons HC-SR04 | Mesure de distance |
| Servomoteur SG90 | Rotation du capteur de 0 à 180° |
| Câble USB | Alimentation et liaison série avec l'ordinateur |

Une plaque d'essai et une alimentation externe 5V (par exemple un module d'alimentation pour breadboard) sont conseillées pour alimenter le servomoteur sans faire redémarrer la carte.

## Câblage

| Fil | Vers l'Arduino |
|-----|----------------|
| HC-SR04 VCC | 5V |
| HC-SR04 GND | GND |
| HC-SR04 TRIG | D11 |
| HC-SR04 ECHO | D12 |
| Servo signal (orange) | D9 |
| Servo + (rouge) | 5V (idéalement une alimentation externe) |
| Servo GND (marron) | GND |

Remarque sur l'alimentation : le servomoteur peut provoquer des appels de courant qui font redémarrer l'Arduino. Si la carte se réinitialise quand le servo force, alimente le servo depuis une source 5V séparée en reliant impérativement sa masse à celle de l'Arduino.

## Structure du dépôt

```
Radar_V1/
├── platformio.ini        Configuration PlatformIO
├── src/
│   └── main.cpp          Programme Arduino (balayage + mesure)
├── affichage_radar.py    Affichage du radar sur l'ordinateur
└── README.md
```

## Installation et utilisation

### Partie Arduino

Le projet utilise PlatformIO. Le fichier `platformio.ini` déclare la carte et la bibliothèque du servomoteur :

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
lib_deps = arduino-libraries/Servo
```

Ouvre le projet dans VS Code avec l'extension PlatformIO, branche l'Arduino, puis téléverse (icône flèche de la barre PlatformIO, ou `Ctrl+Alt+U`). La bibliothèque Servo est téléchargée automatiquement au premier build.

### Partie ordinateur

Le script a besoin de deux bibliothèques Python :

```bash
python3 -m pip install pyserial pygame
```

Ouvre ensuite `affichage_radar.py` et règle la variable `PORT` en haut du fichier selon ton système :

- Windows : `COM3`, `COM4`, etc.
- macOS : `/dev/cu.usbmodemXXXX` ou `/dev/cu.usbserial-XXXX`
- Linux : `/dev/ttyACM0` ou `/dev/ttyUSB0`

Pour trouver le port, la commande `pio device list` liste les ports disponibles. Lance ensuite le script depuis un terminal :

```bash
python3 affichage_radar.py
```

Le port série ne pouvant être ouvert que par un seul programme à la fois, ferme tout moniteur série avant de lancer le script.

### Test sans matériel

Pour vérifier l'affichage sans brancher l'Arduino, passe `SIMULATE = True` en haut du script. Il génère alors un balayage avec des obstacles fictifs. Repasse sur `False` pour utiliser les vraies données.

## Réglages

Quelques constantes permettent d'ajuster le comportement.

`MAX_DISTANCE` fixe la portée en centimètres. Elle est présente dans les deux fichiers et doit rester identique de part et d'autre.

`STEP_DELAY` (côté Arduino) contrôle la vitesse du balayage. Plus la valeur est basse, plus le balayage est rapide.

`FADE` (côté Python) fixe la durée en secondes avant qu'un point ne disparaisse. Une valeur plus élevée donne un nuage plus dense.

## Protocole série

L'échange est volontairement minimal. À chaque degré, l'Arduino envoie une ligne au format `angle,distance` terminée par un retour à la ligne, à 115200 bauds. Une distance de `0` signifie qu'aucun obstacle n'a été détecté dans la portée.

## Dépannage

Si rien ne s'affiche, teste d'abord avec `SIMULATE = True` pour isoler le problème. Si la fenêtre s'ouvre mais reste vide, c'est le port qui est en cause : vérifie sa valeur et qu'aucun moniteur série ne l'occupe. Si l'installation de pygame échoue sur une version très récente de Python, essaie `pygame-ce` à la place, qui suit les nouvelles versions plus rapidement.

## Pistes d'amélioration

Plusieurs extensions sont possibles : un signal sonore via un buzzer lors d'une détection, une légende de distance à l'écran, l'enregistrement des mesures dans un fichier, ou un pas de balayage plus fin pour une meilleure résolution.

## Auteurs

<!-- À compléter -->

## Licence

<!-- Suggestion : licence MIT. Ajoute un fichier LICENSE à la racine si tu la choisis. -->
