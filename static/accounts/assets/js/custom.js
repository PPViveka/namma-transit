// ...................SEARCHBAR CHANGING........................ 
function findDerections() {
  document.getElementById("findDerections").style.display = "block";
  document.getElementById("nearbyStations").style.display = "none";
  document.getElementById("specificBus").style.display = "none";
}

function nearbyStations() {
  document.getElementById("findDerections").style.display = "none";
  document.getElementById("nearbyStations").style.display = "block";
  document.getElementById("specificBus").style.display = "none";
}

function specificBus() {
  document.getElementById("findDerections").style.display = "none";
  document.getElementById("nearbyStations").style.display = "none";
  document.getElementById("specificBus").style.display = "block";
}
// ...................SEARCHBAR CHANGING........................ 


// ..............GOOGLE MAP.................. 
// get and passing location 
var lat = "";

function getLocation() {
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(showPosition);
    
} else {
  lat = "Geolocation is not supported by this browser.";
  console.log(lat);
}
}

function showPosition(position) {
lat = position.coords.latitude + "," + position.coords.longitude;
console.log(lat);
document.getElementById("userLocation").value = lat;
document.getElementById("passLat").click();
}
// ..............GOOGLE MAP.................. 

// ..............MOVING BUS.................. 
function initialiseAxisImages() {
  var axis = document.getElementById('axis');
  if (!axis) return;
  var axisImages = axis.getElementsByTagName('img');
  if (axisImages && axisImages.length > 0) {
    axisImages[0].classList.remove('move-right');
  }
  if (axisImages && axisImages.length > 1) {
    axisImages[1].classList.remove('move-left');
  }
}

window.addEventListener('load', initialiseAxisImages, false);
// ..............MOVING BUS.................. 

// ..............TABLE SEARCHING.................. 
$(document).ready(function(){
  $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#myTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});
// ..............TABLE SEARCHING.................. 



// ....................................SEARCH SUGGESTION ....................................... 
function autocomplete(inp, arr) {
  if (!inp) return;

  var currentFocus;

  inp.addEventListener("input", function(e) {
    var a, b, i, val = this.value;
  
    closeAllLists();
    if (!val) { return false;}
    currentFocus = -1;
  
    a = document.createElement("DIV");
    a.setAttribute("id", this.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
 
    this.parentNode.appendChild(a);
    for (i = 0; i < arr.length; i++) {
      if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
        b = document.createElement("DIV");
        b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
        b.innerHTML += arr[i].substr(val.length);
        b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
        b.addEventListener("click", function(e) {
            inp.value = this.getElementsByTagName("input")[0].value;
            closeAllLists();
        });
        a.appendChild(b);
      }
    }
});
inp.addEventListener("keydown", function(e) {
    var x = document.getElementById(this.id + "autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode == 40) {
    
      currentFocus++;
      addActive(x);
    } else if (e.keyCode == 38) { 
      currentFocus--;
      addActive(x);
    } else if (e.keyCode == 13) {
      e.preventDefault();
      if (currentFocus > -1) {
        if (x) x[currentFocus].click();
      }
    }
});
function addActive(x) {
  if (!x) return false;
  removeActive(x);
  if (currentFocus >= x.length) currentFocus = 0;
  if (currentFocus < 0) currentFocus = (x.length - 1);
  x[currentFocus].classList.add("autocomplete-active");
}
function removeActive(x) {
  for (var i = 0; i < x.length; i++) {
    x[i].classList.remove("autocomplete-active");
  }
}
function closeAllLists(elmnt) {
  var x = document.getElementsByClassName("autocomplete-items");
  for (var i = 0; i < x.length; i++) {
    if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }
  }
}
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}

// Bengaluru bus stops — sourced from BMTC fixture data + common localities
var places = [
  "Ananda Rao Circle", "Arekere", "Attiguppe",
  "Bagalur", "Baiyappanahalli", "Banasawadi", "Banashankari", "Bannerughatta",
  "BEL Circle", "Bellandur", "Bommanahalli", "BTM Layout", "Brigade Road",
  "Chikkabanavara", "City Railway Station", "Coles Park", "Cubbon Park",
  "Dairy Circle", "Deepanjalinagar", "Devanahalli", "Domlur",
  "Electronic City",
  "Frazer Town",
  "Goraguntepalya", "Gottigere", "Gunjur Palya",
  "HAL", "Halasuru", "Hampapura", "Hampinagara", "HBR Layout",
  "Hebbala", "Hebbal", "Hesaraghatta", "HSR Layout", "Hulimavu",
  "Indiranagar", "ITPL",
  "Jakkur", "Jalahalli", "Jayanagar", "JP Nagar",
  "Kadugodi", "Kambipura", "Kempegowda International Airport",
  "Kengeri", "KR Circle", "KR Market", "KR Puram",
  "Koramangala",
  "Lalbagh", "Lakkasandra",
  "Majestic", "Malleshwaram", "Manyatha Tech Park", "Marathahalli",
  "Mathikere", "Mekhri Circle", "MG Road", "Mysore Road",
  "Nagasandra", "Nagavara", "Nagarabhavi", "National College", "Nayandahalli",
  "Nimhans",
  "Old Airport Road",
  "Peenya", "Palace Grounds",
  "Rajajinagar", "Ramamurthynagar", "Richmond Circle", "RT Nagar", "RV College",
  "Sadashivanagar", "Sarjapura", "Shanthinagara", "Shivajinagar",
  "Silk Board", "Sirsi Circle",
  "Tin Factory",
  "Ulsoor",
  "Vidhana Soudha", "Vidyaranyapura", "Vijayanagara",
  "Whitefield",
  "Yelahanka", "Yeshwanthpur"
];

// BMTC bus numbers and Namma Metro lines
var busName = [
  "201", "218", "221", "226", "252", "253", "289", "298M", "303",
  "335E", "340", "356G", "365",
  "401", "401B", "401K",
  "500A", "500C", "500D",
  "600KA",
  "Metro Green Line", "Metro Purple Line"
];

autocomplete(document.getElementById("myInput"), busName);
autocomplete(document.getElementById("inputFrom"), places);
autocomplete(document.getElementById("inputTo"), places);

// .............................................SEARCH SUGGESTION.................................................... 
