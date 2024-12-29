# Bilingue-GitHub

Bilingue-GitHub est un outil basé sur Python conçu pour traduire automatiquement les problèmes GitHub en plusieurs langues. Cet outil s'intègre à l'API de GitHub et utilise des modèles de traduction pour ajouter du contenu traduit aux problèmes.

## Caractéristiques

- Traduction automatique : Traduit le corps des problèmes GitHub ouverts et des fichiers markdown en plusieurs langues.

- Support pour plusieurs langues : Actuellement, il prend en charge le japonais et le français, mais peut être facilement étendu pour soutenir d'autres langues.

## Installation

1. Clonez le dépôt :

```
git clone <url-du-depot>

cd bilingue-github
```

2. Installez les dépendances :

```
pip install -r requirements.txt
```

3. Initialisez l'outil dans votre dépôt :

```
python src/hooks/install_hooks.py
```

### Utilisation

### Git Hooks pour les fichiers Markdown

1. Assurez-vous que les hooks git sont installés en exécutant :

```
python src/hooks/install_hooks.py
```

2. Après avoir commité des modifications sur un fichier Markdown (*.md), le hook post-commit traduira automatiquement le fichier dans les langues cibles.

3. Vérifiez les fichiers traduits (*.langue_code.md) dans votre dépôt.

### Traduction des problèmes GitHub

```
python src/actions/translate_issues.py
```

# Bonjour, comment ça va ? J'espère que vous allez bien.