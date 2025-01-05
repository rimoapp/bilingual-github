# Bilingue-GitHub

Bilingue-GitHub est un outil basé sur Python conçu pour automatiser la traduction des problèmes GitHub en plusieurs langues. Cet outil s'intègre à l'API de GitHub et utilise des modèles de traduction pour ajouter du contenu traduit aux problèmes.

## Fonctionnalités

- Traduction Automatique : Traduit le corps des problèmes GitHub ouverts et des fichiers markdown en plusieurs langues.
  
- Support pour Plusieurs Langues : Actuellement, il prend en charge le japonais et le français, mais peut être facilement étendu pour prendre en charge d'autres langues.

## Installation

1. Clonez le référentiel :

```
git clone <url-du-référentiel>

cd bilingue-github
```

2. Installez les dépendances :

```
pip install -r requirements.txt
```

3. Initialisez l'outil dans votre référentiel :

```
python src/hooks/install_hooks.py
```

### Utilisation
### Git Hooks pour Fichiers Markdown

1. Assurez-vous que les hooks git sont installés en exécutant :

```
python src/hooks/install_hooks.py
```

2. Après avoir engagé des modifications dans un fichier Markdown (*.md), le hook post-commit traduit automatiquement le fichier dans les langues cibles.

3. Vérifiez les fichiers traduits (*.code_langue.md) dans votre référentiel.

### Traduction des Issues GitHub

```
python src/actions/translate_issues.py
```

# Bonjour, comment ça va ?