<script>
    import { onMount, onDestroy } from 'svelte'
    import { Map, NavigationControl, Marker, LngLat, Popup  } from 'maplibre-gl'
    import 'maplibre-gl/dist/maplibre-gl.css'
    import Navbar from './Navbar.svelte';
    import {isOpen, url_stored, marker, currentMinutes, currentTime, selectedOption, selectedOptionB, secondDropdownEnabled, showAltenPflegeHeim, showKindergarten, showBib, showMus, showUnis} from '../stores.js';
    import { alten_pflege_coords } from "./alten_pflege_heim.js";
    import { kinder_coords } from "./kindergarten.js";
    import { unis_coords } from './unis';
    import { mus_coords } from './mus';
    import { bib_coords } from './bib';    
    import { object_without_properties } from 'svelte/internal';
    import { _ } from 'svelte-i18n'
    import { locale } from '../i18n';
    import { BASE_URL } from '../main';
    import { get } from 'svelte/store';
   
    let map;
    let mapContainer;
    let stops_list = [];
    let spinns;
    let spinnsB;
    let marker_a = new Marker();
    let marker_b = new Marker();
    let request_url_start = BASE_URL + "feed?"
    let request_url_start2 = BASE_URL + "marker?"
    let request_url_start3 = BASE_URL + "nearest_station?"

    let isGettingCoords = false
    let customeCoords

    function getCoords() {
      isGettingCoords = true;
      map.getCanvas().style.cursor = 'crosshair';
    }

    function changeLanguage(lang) {
      locale.set(lang);
    }

    function showSpinner() {
      spinns.style.display = "block";
    }

    function hideSpinner() {
      spinns.style.display = "none";
    }

    function showSpinnerB() {
      spinnsB.style.display = "block";
    }
    
    function hideSpinnerB() {
      spinnsB.style.display = "none";
    }

    function closePopup() {
      popupVisible = false;
      selectedOption.set(nearStation);
      const minutesInput = document.getElementById("minutesInput");
      const timeInput = document.getElementById("timeInput");
      
      // Get the current time
      const now = new Date();
      const currentH = now.getHours();
      const currentM = now.getMinutes();
      
      // Format the current time as "HH:mm"
      const formattedTime = `${String(currentH).padStart(2, '0')}:${String(currentM).padStart(2, '0')}`;
      
      // Set the input fields' values
      minutesInput.value = "60";
      timeInput.value = formattedTime;
      
      currentMinutes.set(minutesInput.value);
      currentTime.set(timeInput.value);
    }

    document.addEventListener("DOMContentLoaded", () => {
    spinns = document.querySelector("#spin");
    spinnsB = document.querySelector("#spinB");
    }); 

    let url = null;
    let url2 = null
    let strii = null
    let apicall = "waiting for apicall...";
    var marker_array = null
    let popupVisible = false;
    let initialState = null;
    let nearStation = null;
    let markers_pflege = [];
    let markers_kinder = [];
    let markers_uni = [];
    let markers_mus = [];
    let markers_bib = [];
  
    onMount(async() => {
      popupVisible = true; 

      const apiKey = 'QOmo53z4iFjM8sny5h67';
      
      // Get the user's current coordinates
      const getUserLocation = () => {
        return new Promise((resolve, reject) => {
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
              (position) => {
                resolve({
                  lat: position.coords.latitude,
                  lng: position.coords.longitude,
                });
              },
              (error) => {
                console.error(error);
                reject(error);
              }
            );
          } else {
            reject(new Error("Geolocation is not supported by this browser."));
          }
        });
      };

      // Set the user's coordinates as the initial state or use default coordinates
      try {
        const userLocation = await getUserLocation();
        initialState = { ...userLocation, zoom: 12 };
        startClosestStation(); 
      } catch (error) {
        initialState = { lng: 14.28611, lat: 48.30639, zoom: 12 };
        startClosestStation();
      }

      //create Map
      map = new Map({
        container: mapContainer,
        style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
        center: [initialState.lng, initialState.lat],
        zoom: initialState.zoom
      });
      map.addControl(new NavigationControl(null),'top-right');
      map.on('click', (e) => {
      if (isGettingCoords) {
        const { lng, lat } = e.lngLat;
        initialState.lat = lat
        initialState.lng = lng
        isGettingCoords = false;
        map.getCanvas().style.cursor = '';
        startClosestStation().then(() => {
          selectedOption.set(nearStation)
          let yourCoords_ = get(_)("yourCoords")
          let yourNextStation_ = get(_)("yourNextStation")
          alert(`${yourCoords_} ${lng}, ${lat}. ${yourNextStation_} ${nearStation}`)
          })
        }
      });
    })
  
    onDestroy(() => {
      map.remove();
    });

    //Altenheim
    $: if ($showAltenPflegeHeim) {
      // Convert coordinates to geojson
      const geojson = {
        type: 'FeatureCollection',
        features: alten_pflege_coords.map(coord => ({
          type: 'Feature',
          properties: { name: 'Alten/Pflegeheim' },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };
      // Add data source
      map.addSource('pflege', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 50
      });
      // Add cluster layer
      addCluster('pflege', '#00b3b3');
    } else {
      // Remove source and layers
      try {
        map.removeLayer('pflege-cluster');
        map.removeLayer('pflege-cluster-count');
        map.removeLayer('pflege-point');
        map.removeSource('pflege');
      } catch (error) {
        //do nothing
      }
    }

    // Kindergarten
    $: if ($showKindergarten) {
      const geojson = {
        type: 'FeatureCollection',
        features: kinder_coords.map(coord => ({
          type: 'Feature',
          properties: { name: 'Hort/Kindergarten' },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };
      map.addSource('kindergarten', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 50
      });
      addCluster('kindergarten', '#FFD633');
    } else {
      try {
        map.removeLayer('kindergarten-cluster');
        map.removeLayer('kindergarten-cluster-count');
        map.removeLayer('kindergarten-point');
        map.removeSource('kindergarten');
      } catch (error) {
        // Do nothing
      }
    }

    // Unis
    $: if ($showUnis) {
      const geojson = {
        type: 'FeatureCollection',
        features: unis_coords.map(coord => ({
          type: 'Feature',
          properties: { name: 'Hochschule/Universität' },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };

      map.addSource('unis', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 50
      });

      addCluster('unis', '#ED6BC7');
    } else {
      try {
        map.removeLayer('unis-cluster');
        map.removeLayer('unis-cluster-count');
        map.removeLayer('unis-point');
        map.removeSource('unis');
      } catch (error) {
        // Do nothing
      }
    }

    // Museen
    $: if ($showMus) {
      const geojson = {
        type: 'FeatureCollection',
        features: mus_coords.map(coord => ({
          type: 'Feature',
          properties: { name: 'Museum' },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };

      map.addSource('mus', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 50
      });

      addCluster('mus', '#FF3B33');
    } else {
      try {
        map.removeLayer('mus-cluster');
        map.removeLayer('mus-cluster-count');
        map.removeLayer('mus-point');
        map.removeSource('mus');
      } catch (error) {
        // Do nothing
      }
    }

    // Bibliotheken
    $: if ($showBib) {
      const geojson = {
        type: 'FeatureCollection',
        features: bib_coords.map(coord => ({
          type: 'Feature',
          properties: { name: 'Bibliothek' },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };

      map.addSource('bib', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 50
      });

      addCluster('bib', '#4FDF66');
    } else {
      try {
        map.removeLayer('bib-cluster');
        map.removeLayer('bib-cluster-count');
        map.removeLayer('bib-point');
        map.removeSource('bib');
      } catch (error) {
        // Do nothing
      }
    }

    // Function to add a clustered layer for a group of markers
    function addCluster(id, color) {
      map.addLayer({
        id: id + '-cluster',
        type: 'circle',
        source: id,
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': color,
          'circle-radius': ['step',['get', 'point_count'], 20, 10, 30, 50, 40]
        }
      });

      map.addLayer({
        id: id + '-cluster-count',
        type: 'symbol',
        source: id,
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
          'text-size': 12
        }
      });

      map.addLayer({
        id: id + '-point',
        type: 'circle',
        source: id,
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': color,
          'circle-radius': 12,
          'circle-stroke-width': 0,
          'circle-stroke-color': '#fff',
        }
      });

      // Add popup
      map.on('click', id + '-point', function (e) {
        var coordinates = e.features[0].geometry.coordinates.slice();
        var name = e.features[0].properties.name;

        new Popup()
            .setLngLat(coordinates)
            .setHTML(name)
            .addTo(map);
      });
      // Add popup on mouseenter
      map.on('mouseenter', id + '-point', function (e) {
        map.getCanvas().style.cursor = 'pointer';
      });
      // Remove popup on mouseleave
      map.on('mouseleave', id + '-point', function () {
        map.getCanvas().style.cursor = '';
      });
    }

    function toggleNavbar() {
      isOpen.update(value => !value);
    }

    const startAction = () => {
      return new Promise((resolve, reject) => {
        let force_setting = "&forced=forced" //secondDropdownEnabled
        if (!$secondDropdownEnabled) {
          force_setting = "&forced=not_forced"
        }
        url = request_url_start + "starting_station=" + String($selectedOption) + "&starting_time=" + String($currentTime).substring(0, 5) + ':00' + "&timelimit=" + String($currentMinutes) + force_setting;
        url2 = request_url_start2 + "station_name=" + String($selectedOption);
        fetch(url2)
        .then(response => response.json())
        .then(data => {
            strii = data.toString()
            resolve();
        }).catch(error => {
            console.log(error);
            reject(error);
        });
      });
    };

    const startActionB = () => {
      return new Promise((resolve, reject) => {
        url = request_url_start + "starting_station=" + String($selectedOptionB) + "&starting_time=" + String($currentTime).substring(0, 5) + ':00' + "&timelimit=" + String($currentMinutes)+ "&forced=forced";
        url2 = request_url_start2 + "station_name=" + String($selectedOptionB);
        fetch(url2)
        .then(response => response.json())
        .then(data => {
            strii = data.toString()
            resolve();
        }).catch(error => {
            console.log(error);
            hideSpinnerB()
            reject(error);
        });
      });
    };

    const startClosestStation = () => {
      return new Promise((resolve, reject) => {
        fetch(request_url_start3 + "lat=" + String(initialState.lat) + "&lon=" + String(initialState.lng))
        .then(response => response.json())
        .then(data => {
            nearStation = data.toString()
            resolve();
            }).catch(error => {
                console.log(error);
                reject(error);
            });
      });
    };

    const startA = async () => {
        showSpinner()
        showSpinnerB()
        await startAction()
        marker_a.remove();
        if (map.getLayer('polygons')) map.removeLayer('polygons');
        if (map.getSource('map_source')) map.removeSource('map_source');
        marker_array = JSON.parse("[" + String(strii) + "]");
        marker_a = new Marker({color: "#ff8200"}).setLngLat([marker_array[1],marker_array[0]]).addTo(map); 
        let popup = new Popup({ offset: 25 }).setText($selectedOption);
        marker_a.setPopup(popup);

        console.log(url)
        fetch(url)
        .then(response => response.json())
        .then(data => {
          if (typeof data === "string" && data.startsWith("!!!")) {
            hideSpinner()
            const textInsert = data.slice(3);
            const message = $_("popup2_prefix") + textInsert + $_("popup2_suffix");
            const confirmed = window.confirm(message);
            if (confirmed) {
              const timeInput = document.getElementById("timeInput");
              timeInput.value = data.slice(3);
              currentTime.set(timeInput.value);
              startA();
              return
            } else {
              apicall = (data);
              if (map.getLayer('polygons')) map.removeLayer('polygons');
              if (map.getSource('map_source')) map.removeSource('map_source');
              const parsedGeoJson = JSON.parse(apicall);
              map.addSource('map_source', {
              type: 'geojson',
              data: new Object(parsedGeoJson)
              }
              )
              map.addLayer({
                'id': 'polygons',
                'type': 'fill',
                'source': 'map_source',
                'layout': {},
                'paint': { 
                    'fill-color': '#ff8200',
                    'fill-opacity': 0.4
                }
              })
              hideSpinner()
              map.setCenter([marker_array[1],marker_array[0]]); 
            }
          }
          apicall = (data)
          if (map.getLayer('polygons')) map.removeLayer('polygons');
          if (map.getSource('map_source')) map.removeSource('map_source');
          const parsedGeoJson = JSON.parse(apicall);
          map.addSource('map_source', {
          type: 'geojson',
          data: new Object(parsedGeoJson)
          }
          )
          map.addLayer({
            'id': 'polygons',
            'type': 'fill',
            'source': 'map_source',
            'layout': {},
            'paint': { 
                'fill-color': '#ff8200',
                'fill-opacity': 0.4
            }
          })
          hideSpinner()
          if ($isOpen) (toggleNavbar());
          map.setCenter([marker_array[1],marker_array[0]]); 
          })
          .catch(error => {
          console.log(error);
          if ($isOpen) (toggleNavbar());
          return [];
        })
        //###### B
        if ($secondDropdownEnabled) {
          await startActionB() 
          marker_b.remove();
          if (map.getLayer('polygonsB')) map.removeLayer('polygonsB');
          if (map.getSource('map_sourceB')) map.removeSource('map_sourceB');
          marker_array = JSON.parse("[" + String(strii) + "]");
          marker_b = new Marker({color: "#703eb0"}).setLngLat([marker_array[1],marker_array[0]]).addTo(map); 
          let popupB = new Popup({ offset: 25 }).setText($selectedOptionB);
          marker_b.setPopup(popupB);
          fetch(url)
          .then(response => response.json())
          .then(data => {
            apicall = (data)
            if (map.getLayer('polygonsB')) map.removeLayer('polygonsB');
            if (map.getSource('map_sourceB')) map.removeSource('map_sourceB');
            const parsedGeoJson = JSON.parse(apicall);
            map.addSource('map_sourceB', {
            type: 'geojson',
            data: new Object(parsedGeoJson)
            }
            )
            map.addLayer({
              'id': 'polygonsB',
              'type': 'fill',
              'source': 'map_sourceB',
              'layout': {},
              'paint': { 
                  'fill-color': '#703eb0',
                  'fill-opacity': 0.4
              }
            })
            hideSpinnerB()
            if ($isOpen) (toggleNavbar());
            map.setCenter([marker_array[1],marker_array[0]]); 
            })
            .catch(error => {
            console.log(error);
            hideSpinnerB()
            if ($isOpen) (toggleNavbar());
            return [];}
            )
        } else {
          hideSpinnerB()
          marker_b.remove();
          if (map.getLayer('polygonsB')) map.removeLayer('polygonsB');
          if (map.getSource('map_sourceB')) map.removeSource('map_sourceB');
        }
    } 
  </script>
  
  {#if popupVisible}
    <div class="popup-overlay">
      <div class="popup">
        <h2>{$_("popup_head")}</h2>
        <p>{$_("popup_text")}</p>
        <button on:click={closePopup}>{$_("popup_button")}</button>
        <button on:click={() => window.open('https://forms.office.com/e/Gvf0iveeWc', '_blank')} class="popup-button secondary">{$_("link_quiz")}</button>
      </div>
    </div>
  {/if}

  <div class="map-wrap">
    <div>
      <button class= "startsearchb" on:click={startA}><h4>{$_("start_search")}</h4></button>
    </div>
    <div class="spinner" id="spin" style="display: none;">
      <h4>Loading ...</h4>
      <div class="bounce1"></div>
      <div class="bounce2"></div>
      <div class="bounce3"></div>
    </div>
    <div class="spinnerB" id="spinB" style="display: none;">
      <h4>Loading ...</h4>
      <div class="bounce1"></div>
      <div class="bounce2"></div>
      <div class="bounce3"></div>
    </div>
    <a href="https://www.maptiler.com" class="watermark"><img
      src="https://api.maptiler.com/resources/logo.svg" alt="MapTiler logo"/></a>
    <div class="map" id="map" bind:this={mapContainer}></div>
  </div>
  <div class="GetCoordsButtonDiv" class:open="{!$isOpen}">
    <button on:click={getCoords} class="GetCoordsButton">.</button>
  </div>

  <div class="language-switcher">
    <button on:click={() => changeLanguage('en')} class="language-button-en">EN</button>
    <button on:click={() => changeLanguage('de')} class="language-button-de">DE</button>
  </div>
  
  <style>

    .GetCoordsButton {
      color: transparent;
      background-color: transparent;
      background-image: url('../crosshairs-solid.svg');
      background-position: center;
      background-repeat: no-repeat;
      border: none;
      outline: none;
      z-index: 120;
      height: 25px;
    }

    .GetCoordsButton:active {
      background-size: 80%;
    }

    .GetCoordsButtonDiv {
      position: fixed;
      z-index: 120;
      top: 85px;
      left: 410px;
      transition: left 0.35s ease-in-out;
    }

    .GetCoordsButtonDiv.open {
      left: -70px;
    }
    .language-switcher {
      position: fixed;
      bottom: 25px;
      right: 5px;
      border-radius: 5px;
      padding: 5px;
      z-index: 1000;
    }

    .language-button-en {
      font-size: 14px;
      font-weight: bold;
      color: #000000;
      background-color: transparent;
      border: none;
      outline: none;
      cursor: pointer;
      padding: 5px;
      background-image: url('../gb.svg');

    }

    .language-button-en:hover {
      color: #545050;
    }

    .language-button-de {
      font-size: 14px;
      font-weight: bold;
      color: rgb(0, 0, 0);
      background-color: transparent;
      border: none;
      outline: none;
      cursor: pointer;
      padding: 5px;
      background-image: url('../de.svg');

    }

    .language-button-de:hover {
      color: #545050;
    }

    .map-wrap {
      position: relative;
      width: calc(100vw);
      height: calc(100vh);
      z-index: 100;
    }
  
    .map {
      position: fixed;
      width: 100%;
      height: 100%;
      color: rgb(24, 10, 10);
      background-color: rgb(233, 233, 34);
      z-index: 90;
    }
    
    .startsearchb {
      height: 70px;
      top: 45%;
      z-index: 100; 
      position: fixed;
      font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
      font-size: 12px;
      line-height: 18px;
      left: 0;
      top: 50%;
      width: 200px;
      margin : 10px;
      margin-left: -30px;
      padding: 10px;
      padding-left: 25px;
      border-radius: 20px;
      background-color: 
  rgb(233, 233, 34);
      color: 
  rgb(24, 10, 10);
    }
  
    .watermark {
      position: absolute;
      left: 10px;
      bottom: 10px;
      z-index: 100;
    }

    .spinner {
      position: absolute;
      top: 50%;
      left: 50%;
      z-index: 200;
      margin: 10px auto;
      text-align: center;
      font-size: 15px;
    }

    .spinner > div {
      width: 25px;
      height: 25px;
      background-color: #333;

      border-radius: 100%;
      display: inline-block;
      -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
      animation: sk-bouncedelay 1.4s infinite ease-in-out both;
    }

    .spinner .bounce1 {
      -webkit-animation-delay: -0.32s;
      animation-delay: -0.32s;
    }

    .spinner .bounce2 {
      -webkit-animation-delay: -0.16s;
      animation-delay: -0.16s;
    }

    .spinnerB {
      position: absolute;
      top: 50%;
      left: 50%;
      z-index: 200;
      margin: 10px auto;
      text-align: center;
      font-size: 15px;
    }

    .spinnerB > div {
      width: 25px;
      height: 25px;
      background-color: #333;

      border-radius: 100%;
      display: inline-block;
      -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
      animation: sk-bouncedelay 1.4s infinite ease-in-out both;
    }

    .spinnerB .bounce1 {
      -webkit-animation-delay: -0.32s;
      animation-delay: -0.32s;
    }

    .spinnerB .bounce2 {
      -webkit-animation-delay: -0.16s;
      animation-delay: -0.16s;
    }

    .popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 999;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    }

    .popup {
      background-color: white;
      padding: 20px;
      border-radius: 10px;
      max-width: 500px;
      text-align: center;
    }

    .popup h2 {
      margin-top: 0;
    }

    .popup button {
      background-color: #4CAF50;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      font-size: 16px;
      cursor: pointer;
      display: block;
      margin-top: 5px;
      margin-left: auto;
      margin-right: auto;
    }

    .popup button:hover {
      background-color: #3e8e41;
      color: white;
    }

    .popup-button.secondary {
      background-color: rgb(225, 236, 225);
      color: #4CAF50;
      opacity: 1;
    }

    :global(.maplibregl-popup-close-button),
    :global(.mapboxgl-popup-close-button) {
    font-size: 7px;
    background-color: red;
    border-color: red;
    outline: none !important;
    }

    :global(.maplibregl-popup-close-button:hover),
    :global(.mapboxgl-popup-close-button:hover) {
    font-size: 7px;
    background-color: rgb(198, 16, 16);
    border-color: red;
    outline: none !important;
    }

    :global(.maplibregl-marker),
    :global(.mapboxgl-marker) {
    cursor: pointer;
    }

    @-webkit-keyframes sk-bouncedelay {
      0%, 80%, 100% { -webkit-transform: scale(0) }
      40% { -webkit-transform: scale(1.0) }
    }

    @keyframes sk-bouncedelay {
      0%, 80%, 100% { 
        transform: scale(0);
        -webkit-transform: scale(0);
      } 40% { 
        transform: scale(1.0);
        -webkit-transform: scale(1.0);
      }
    }
  </style>