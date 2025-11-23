// Afficher un message de confirmation dans la console du navigateur (F12)
console.log("Le script.js a été chargé avec succès !");

// Fonction pour modifier dynamiquement le contenu d'un élément
function updateFooterYear() {
    // Récupère l'année en cours
    const currentYear = new Date().getFullYear();
    
    // Récupèrer l'élément footer que nous avons dans index.html
    const footerElement = document.querySelector('footer p'); 

    // Vérifier si l'élément existe avant de le modifier
    if (footerElement) {
        // Change le texte pour mettre à jour l'année
        footerElement.innerHTML = `&copy; ${currentYear} AirQualitéFrance - Collaboration active.`;
    }
}

// Appelle la fonction lorsque la page est chargée
updateFooterYear();
