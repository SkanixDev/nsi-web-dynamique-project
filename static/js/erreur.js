const allPopups = [];
let searchParams = new URLSearchParams(window.location.search);

// Création d'un table pour répertorier toutes les erreurs
const allMessages = [
  {
    name: "user_exist",
    type: "info",
    message: "Ce compte existe déjà !",
  },
  {
    name: "wrong_password",
    type: "error",
    message: "Mot de passe incorrect !",
  },
  {
    name: "login_success",
    type: "success",
    message: "Vous êtes connecté !",
  },
  {
    name: "register_success",
    type: "success",
    message: "Votre compte à bien été créé !",
  },
  {
    name: "already_logged_in",
    type: "warning",
    message: "Vous êtes déjà connecté !",
  },
  {
    name: "user_not_found",
    type: "error",
    message: "Cet utilisateur n'existe pas !",
  },
  {
    name: "login_error",
    type: "error",
    message: "Erreur lors de la connexion !",
  },
  {
    name: "register_error",
    type: "error",
    message: "Erreur lors de l'inscription !",
  },
  {
    name: "not_logged_in",
    type: "warning",
    message: "Vous n'êtes pas connecté !",
  },
  {
    name: "not_admin",
    type: "warning",
    message: "Vous n'êtes pas administrateur !",
  },
  {
    name: "add_shoe_incomplete",
    type: "error",
    message: "Veuillez remplir tous les champs !",
  },
  {
    name: "logout_success",
    type: "info",
    message: "Vous êtes déconnecté !",
  },
  {
    name: "add_shoe_success",
    type: "success",
    message: "La chaussure a bien été ajoutée !",
  },
  {
    name: "info_user_success",
    type: "success",
    message: "Les informations ont bien été modifiées !",
  },
  {
    name: "info_user_incomplete",
    type: "error",
    message: "Veuillez remplir tous les champs !",
  },
  {
    name: "order_success",
    type: "success",
    message: "La commande a bien été passée !",
  },
  {
    name: "password_not_match",
    type: "error",
    message: "Les mots de passe ne correspondent pas !"
  }
];

// si dans l'url un message (erreur, info,warning,...) alors chercher dans la table et appeller la fonction createPopups
if (searchParams.has("error")) {
  const error = searchParams.get("error");
  const message = allMessages.find((msg) => msg.name === error);
  createPopups(message.type, message.message);
} else if (searchParams.has("warning")) {
  const warning = searchParams.get("warning");
  const message = allMessages.find((msg) => msg.name === warning);
  createPopups(message.type, message.message);
} else if (searchParams.has("success")) {
  const success = searchParams.get("success");
  const message = allMessages.find((msg) => msg.name === success);
  createPopups(message.type, message.message);
} else if (searchParams.has("info")) {
  const info = searchParams.get("info");
  const message = allMessages.find((msg) => msg.name === info);
  createPopups(message.type, message.message);
}

// Fonction pour créer une popup
function createPopups(type, message, duration = 5000) {
  //ajouter tous le css
  const div = document.createElement("div");
  div.style.position = "absolute";
  div.style.top = allPopups.length * 60 + 20 + "px";
  div.style.right = "20px";
  div.style.zIndex = "100";
  div.style.width = "300px";
  div.style.boxShadow = "0 0 10px rgba(0,0,0,0.25)";
  div.style.borderRadius = "5px";
  div.style.padding = "10px";
  div.style.color = "white";
  div.style.textAlign = "center";
  div.style.fontWeight = "bold";

  // permet de mettre la bonne couleur à l'erreur
  switch (type) {
    case "success":
      div.style.backgroundColor = "#28a745";
      break;
    case "error":
      div.style.backgroundColor = "#dc3545";
      break;
    case "warning":
      div.style.backgroundColor = "#ffc107";
      break;
    case "info":
      div.style.backgroundColor = "#17a2b8";
      break;
    default:
      div.style.backgroundColor = "black";
      break;
  }

  div.setAttribute("role", "alert");
  div.innerHTML = message;
  document.body.appendChild(div);

  allPopups.push({ type, message, duration });

  setTimeout(() => {
    // transition lors de la suppression d'une popup
    div.style.transition = "opacity 1s ease-in";
    div.style.opacity = "0";
    setTimeout(() => {
      div.remove();
    }, 2000);
  }, duration - 2000);
}
