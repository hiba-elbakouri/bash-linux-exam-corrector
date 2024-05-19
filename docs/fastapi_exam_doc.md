# Sujet d'Examen

**Titre : Création et Gestion d'une API de Questions à Choix Multiples avec FastAPI**

**Aperçu :**
Dans cet examen, vous démontrerez votre capacité à créer et gérer une API pour un système de questions à choix multiples en utilisant FastAPI. L'API gérera l'authentification des utilisateurs, la récupération des questions et la création de nouvelles questions. Vous utiliserez diverses bibliothèques Python, notamment FastAPI, Pydantic, Pandas et Enum, ainsi que l'authentification HTTP Basic pour la sécurité des utilisateurs.

**Tâches de l'Examen :**

1. **Installation et Initialisation :**
   - Initialiser une application FastAPI.
   - Importer les modules nécessaires : `Enum`, `FastAPI`, `Query`, `Depends`, `HTTPException`, `status`, `Form`, `HTTPBasic`, `HTTPBasicCredentials` de `fastapi`, `BaseModel` de `pydantic`, `List`, `Union` de `typing`, et `Annotated` de `typing_extensions`.
   - Charger et prétraiter les données des questions à partir d'un fichier CSV en utilisant Pandas, en s'assurant que les noms des colonnes sont renommés pour plus de clarté.

2. **Prétraitement des Données :**
   - Charger le fichier CSV `questions.csv` contenant les questions.
   - Renommer les colonnes en `Question`, `Response_A`, `Response_B`, `Response_C`, `Response_D`, et `Subject`.
   - Corriger les fautes de frappe ou les incohérences dans les données, comme s'assurer que les noms des sujets sont correctement orthographiés.

3. **Modèles de Données :**
   - Créer des modèles Pydantic pour représenter une question avec trois choix de réponse (`Question`) et une question avec quatre choix de réponse (`Question_D`).

4. **Énumérations pour les Types de Test et les Nombres de Questions :**
   - Définir l'énumération `Test_Type` avec les options pour les tests de `positioning` et de `validation`.
   - Définir l'énumération `Quest_Num` avec les options pour sélectionner 5, 10 ou 20 questions.

5. **Authentification des Utilisateurs :**
   - Implémenter un dictionnaire `users_db` pour stocker les paires nom d'utilisateur-mot de passe.
   - Créer une fonction `get_current_username` pour valider les identifiants des utilisateurs en utilisant l'authentification HTTP Basic. Retourner le nom d'utilisateur si les identifiants sont valides, sinon lever une exception `HTTP_401_UNAUTHORIZED`.

6. **Endpoint de Récupération des Questions :**
   - Implémenter un endpoint `/questions` pour récupérer des questions à choix multiples.
   - Utiliser des paramètres de requête pour filtrer les questions par type de test, nombre de questions, et éventuellement par sujets.
   - S'assurer que le modèle de réponse peut retourner dynamiquement soit `Question` soit `Question_D` en fonction de la présence du quatrième choix de réponse.

7. **Endpoint de Création de Questions :**
   - Implémenter un endpoint `/new_question` pour permettre aux utilisateurs authentifiés de créer de nouvelles questions.
   - Utiliser les données de formulaire pour accepter les détails de la question, y compris le texte de la question, le sujet, la réponse correcte, l'utilisation prévue, et les choix de réponse.
   - Restreindre la création de questions aux utilisateurs ayant le nom d'utilisateur "admin".
   - Ajouter la nouvelle question au DataFrame et la sauvegarder dans le fichier CSV.

**Fichiers à Soumettre :**

1. `main.py` : Le script Python complet implémentant l'application FastAPI.
2. `README.md` : Un fichier expliquant comment configurer et exécuter votre application FastAPI, y compris les dépendances nécessaires.
3. `requirements.txt` : Un fichier listant toutes les dépendances Python nécessaires pour exécuter votre application.
4. `tests.py` : Un script Python contenant des tests unitaires et d'intégration pour vérifier les fonctionnalités de votre application.

**Exigences de Soumission :**

- Assurez-vous que votre script suit une mise en forme correcte du code et inclut des commentaires expliquant les sections clés du code.
- Le fichier `README.md` doit fournir des instructions claires et détaillées pour l'installation et l'exécution de l'application.
- Le fichier `tests.py` doit contenir des tests utilisant `pytest` ou `unittest` pour valider le bon fonctionnement des endpoints de l'API, incluant des tests pour l'authentification, la récupération de questions et la création de nouvelles questions.

**Évaluation :**
- Votre code sera évalué en exécutant des scripts de test Python automatisés. Assurez-vous que tous les tests passent et que l'application fonctionne comme prévu.

Bonne chance !
