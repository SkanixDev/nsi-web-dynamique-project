const searchParams = new URLSearchParams(window.location.href);
console.log(searchParams.get("info"));
function compte() {
   if (searchParams.toStrings(session) === "logged_in") {
    alert("l")
   }
}