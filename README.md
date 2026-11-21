<h1>Étude comparative : Llama 3.2 vs Qwen 0.5B</h1>

<h2>1. Objectif de l'expérimentation</h2>
<p>
Cette étude compare deux modèles de langage exécutés localement avec Ollama :
<strong>Llama 3.2</strong> et <strong>Qwen 0.5B</strong>.
L'objectif est d'évaluer leurs performances sur cinq tâches : explication d'un concept,
raisonnement, génération de code Python, synthèse courte et traduction.
</p>

<h2>2. Protocole expérimental</h2>
<p>Les deux modèles sont évalués à partir des mêmes questions :</p>

<table>
  <thead>
    <tr><th>Question</th><th>Type de tâche</th><th>Consigne</th></tr>
  </thead>
  <tbody>
    <tr><td>Q1</td><td>Explication</td><td>Expliquer simplement le fonctionnement d'un réseau de neurones artificiels (ANN).</td></tr>
    <tr><td>Q2</td><td>Raisonnement</td><td>Un train parcourt 120 km en 2 heures. Calculer sa vitesse moyenne et expliquer le raisonnement.</td></tr>
    <tr><td>Q3</td><td>Génération de code</td><td>Écrire un programme Python qui vérifie si un nombre est premier.</td></tr>
    <tr><td>Q4</td><td>Synthèse</td><td>Résumer en trois phrases le rôle de l'intelligence artificielle dans le domaine de la santé.</td></tr>
    <tr><td>Q5</td><td>Traduction</td><td>Traduire en anglais une phrase portant sur l'automatisation et l'aide à la décision par l'IA.</td></tr>
  </tbody>
</table>

<p>
<strong>Environnement :</strong> Windows, Ollama et Streamlit.
<strong>Matériel :</strong> 31,71 Go de RAM et GPU NVIDIA T1200 Laptop avec 4 096 Mo de VRAM.
</p>

<h2>3. Résultats de performance</h2>
<table>
  <thead>
    <tr><th>Indicateur</th><th>Llama 3.2</th><th>Qwen 0.5B</th></tr>
  </thead>
  <tbody>
    <tr><td>Temps de réponse</td><td>21,20 s</td><td><strong>3,04 s</strong></td></tr>
    <tr><td>Temps du premier token (TTFT)</td><td>7,45 s</td><td><strong>2,02 s</strong></td></tr>
    <tr><td>Nombre de tokens générés</td><td>512</td><td>173</td></tr>
    <tr><td>Vitesse de génération</td><td>24,16 tokens/s</td><td><strong>56,89 tokens/s</strong></td></tr>
  </tbody>
</table>

<p>
Qwen 0.5B présente un temps de réponse environ sept fois plus faible et une vitesse de génération
environ 2,35 fois supérieure à celles de Llama 3.2, selon les mesures globales relevées.
</p>

<h2>4. Consommation des ressources matérielles</h2>
<table>
  <thead>
    <tr><th>Indicateur</th><th>Llama 3.2</th><th>Qwen 0.5B</th></tr>
  </thead>
  <tbody>
    <tr><td>Utilisation CPU</td><td>31,8 %</td><td>21,6 %</td></tr>
    <tr><td>Utilisation RAM</td><td>62,1 %</td><td>62,5 %</td></tr>
    <tr><td>RAM affichée</td><td>19,71 Go</td><td>19,81 Go</td></tr>
    <tr><td>Utilisation GPU</td><td>0 %</td><td>0 %</td></tr>
    <tr><td>Mémoire GPU (VRAM)</td><td>0 Mo</td><td>0 Mo</td></tr>
  </tbody>
</table>

<p>
Qwen affiche une utilisation CPU inférieure de 10,2 points de pourcentage.
La consommation RAM affichée est presque identique pour les deux modèles.
Aucune utilisation du GPU ni de la VRAM n'a été observée lors des captures.
</p>

<p>
<strong>Limite de mesure :</strong> les valeurs de RAM semblent correspondre à l'utilisation globale
du système et non à la mémoire attribuable exclusivement à chaque processus du modèle.
Elles ne permettent donc pas de conclure que Qwen consomme moins de RAM.
Les mesures CPU et RAM sont des instantanés qui peuvent varier selon la charge du système.
</p>

<h2>5. Analyse et réponses aux questions</h2>

<h3>1. Quel modèle présente le temps de réponse le plus faible ?</h3>
<p>
Qwen 0.5B, avec 3,04 secondes contre 21,20 secondes pour Llama 3.2.
</p>

<h3>2. Quel modèle offre la vitesse de génération la plus élevée ?</h3>
<p>
Qwen 0.5B, avec 56,89 tokens par seconde contre 24,16 tokens par seconde pour Llama 3.2.
</p>

<h3>3. Quelle différence constatez-vous en matière de consommation des ressources matérielles ?</h3>
<p>
Qwen présente une utilisation CPU plus faible (21,6 % contre 31,8 %).
La RAM affichée est presque identique (19,81 Go pour Qwen et 19,71 Go pour Llama).
Les deux modèles affichent 0 % d'utilisation GPU.
</p>

<h3>4. Les différences de performances sont-elles constantes pour toutes les questions ?</h3>
<p>
Pas nécessairement. Les performances peuvent varier selon la complexité de la tâche.
L'explication, le raisonnement, la génération de code, la synthèse et la traduction ne sollicitent
pas exactement les mêmes capacités. Les résultats disponibles sont globaux : les mesures
individuelles Q1 à Q5 sont nécessaires pour vérifier précisément ces variations.
</p>

<h3>5. Quel modèle recommanderiez-vous pour une machine disposant de ressources limitées ?</h3>
<p>
Qwen 0.5B est recommandé dans le cadre de cette expérimentation, car il présente un temps de réponse
plus faible, une vitesse de génération supérieure et une utilisation CPU plus réduite.
Cette recommandation reste conditionnée à une qualité de réponse suffisante pour l'application visée.
Les mesures de RAM ne montrent pas d'avantage net.
</p>

<h2>6. Conclusion</h2>
<p>
Dans les conditions de test observées, Qwen 0.5B se distingue par sa rapidité et sa plus faible
sollicitation du processeur. Llama 3.2 peut rester préférable lorsque la qualité des réponses
sur des tâches complexes est prioritaire, mais cette qualité doit être évaluée à partir des réponses
effectivement produites. Le GPU n'ayant pas été sollicité pendant les mesures, les résultats reflètent
principalement une exécution sur CPU.
</p>

<p>
<strong>Bilan :</strong> Qwen 0.5B est le choix le plus adapté à une exécution rapide dans cette expérience.
Pour une conclusion complète, il est recommandé de relever les mesures séparément pour chacune des
cinq questions et de mesurer la RAM propre à chaque processus Ollama.
</p>
