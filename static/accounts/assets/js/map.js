function initMap() {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    // Use coordinates injected by the Django view; fall back to Bengaluru city centre
    const initLat = window.NAMMA_LAT || 12.9716;
    const initLng = window.NAMMA_LNG || 77.5946;
    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 13,
      center: { lat: initLat, lng: initLng },
    });
    directionsRenderer.setMap(map);

    const onChangeHandler = function () {
      calculateAndDisplayRoute(directionsService, directionsRenderer);
    };
    document
      .getElementById("start")
      .addEventListener("change", onChangeHandler);
    document
      .getElementById("end")
      .addEventListener("change", onChangeHandler);
  }

  function calculateAndDisplayRoute(directionsService, directionsRenderer) {
    directionsService.route(
      {
        origin: {
          query: document.getElementById("start").value,
        },
        destination: {
          query: document.getElementById("end").value,
        },
        travelMode: google.maps.TravelMode.DRIVING,
      },
      (response, status) => {
        if (status === "OK") {
          directionsRenderer.setDirections(response);
        } else {
          window.alert("Directions request failed due to " + status);
        }
      }
    );
  }
