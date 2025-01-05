# Bilingual-GitHub
Bilingual-GitHub est un outil basé sur Python conçu pour traduire automatiquement les problèmes GitHub en plusieurs langues. Cet outil s'intègre à l'API de GitHub et utilise des modèles de traduction pour ajouter du contenu traduit aux problèmes.

## Caractéristiques
- Traduction Automatique : Traduit le corps des problèmes GitHub ouverts et des fichiers markdown en plusieurs langues.
- Support pour Plusieurs Langues : Actuellement, il prend en charge le japonais et le français, mais peut être facilement étendu pour prendre en charge d'autres langues.

## Installation
1. Clonez le dépôt :
```
git clone <repository-url>
cd bilingual-github
```
2. Installez les dépendances :
```
pip install -r requirements.txt
```
3. Initialisez l'outil dans votre dépôt :
```
python src/hooks/install_hooks.py
```

## Utilisation
### Git Hooks pour les Fichiers Markdown
1. Assurez-vous que les hooks git sont installés en exécutant :
```
python src/hooks/install_hooks.py
```
2. Après avoir engagé des modifications dans un fichier Markdown (*.md), le hook post-commit le traduit automatiquement dans les langues cibles.
3. Vérifiez les fichiers traduits (*.language_code.md) dans votre dépôt.

### Traduction des Issues GitHub
```
python src/actions/translate_issues.py
```