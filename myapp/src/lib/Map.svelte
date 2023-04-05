<script>
    import { onMount, onDestroy } from 'svelte'
    import { Map, NavigationControl, Marker, LngLat, Popup  } from 'maplibre-gl'
    import 'maplibre-gl/dist/maplibre-gl.css'
    import Navbar from './Navbar.svelte';
    import {isOpen, url_stored, marker, currentMinutes, currentTime, selectedOption} from '../stores.js';
    import { object_without_properties } from 'svelte/internal';
    import { _ } from 'svelte-i18n'
    import { locale } from '../i18n';
    import { BASE_URL } from '../main';
   
    let map;
    let mapContainer;
    let stops_list = [];
    let spinns;
    let marker_a = new Marker();
    let request_url_start = BASE_URL + "feed?"
    let request_url_start2 = BASE_URL + "marker?"

    function showSpinner() {
      spinns.style.display = "block";
    }

    // Hide spinner
    function hideSpinner() {
      spinns.style.display = "none";
    }

    function changeLanguage(lang) {
      locale.set(lang);
    }

    function closePopup() {
      popupVisible = false;
      selectedOption.set("Choose");
    }

    document.addEventListener("DOMContentLoaded", () => {
    spinns = document.querySelector("#spin");
    }); 

    let url = null;
    let url2 = null
    let strii = null
    let apicall = "waiting for apicall...";
    var marker_array = null
    let popupVisible = false;
  
    onMount(async() => {
      popupVisible = true; 

      const apiKey = 'QOmo53z4iFjM8sny5h67';
  
      const initialState = { lng: 14.28611, lat: 48.30639, zoom: 12 };

      map = new Map({
        container: mapContainer,
        style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
        center: [initialState.lng, initialState.lat],
        zoom: initialState.zoom
      });
  
      map.addControl(new NavigationControl(null),'top-right');
      
          // load stops from file
      const response = await fetch('stops.txt');
      const text = await response.text();
      stops_list = text.split('\n').slice(1).map((line) => {
        const [stop_id, stop_name, stop_lat, stop_lon, zone_id] = line.split(',');
        return { stop_id, stop_name: (String(stop_name).replace(/"/g, '')), stop_lat: Number(String(stop_lat).replace(/"/g, '')), stop_lon: Number(String(stop_lon).replace(/"/g, '')), zone_id };
      });
      console.log(stops_list[0].stop_lat)
      console.log(stops_list[0].stop_name)
      console.log(stops_list)
      //add markers for each stop
      stops_list.forEach((stopi) => {
        const markerx = new Marker({color: "#00bfff"})
          .setLngLat(new LngLat(stopi.stop_lon, stopi.stop_lat))
          .addTo(map);
        
        // create popup
        const popup = new Popup({ closeButton: false })
          .setHTML(stopi.stop_name)
          .setLngLat(new LngLat(stopi.stop_lon, stopi.stop_lat));

        // bind popup to marker
        markerx.setPopup(popup);
        // make marker clickable and update selectedOption

        markerx.getElement().addEventListener('click', () => {
          // update the selected stop name store
          //console.log("ckick")
          selectedOption.set(stopi.stop_name);
        });
        markerx.getElement().style.cursor = 'pointer';
      });
    })

      //new Marker({color: "#FF0000"})
       // .setLngLat([14.28611,48.30639])
        //.addTo(map);
  
    onDestroy(() => {
      map.remove();
    });

    function toggleNavbar() {
      isOpen.update(value => !value);
    }

    const startAction = () => {
      return new Promise((resolve, reject) => {
        url = request_url_start + "starting_station=" + String($selectedOption) + "&starting_time=" + String($currentTime).substring(0, 5) + ':00' + "&timelimit=" + String($currentMinutes);
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

    const startA = async () => {
        showSpinner()
        await startAction()
        marker_a.remove();
        if (map.getLayer('polygons')) map.removeLayer('polygons');
        if (map.getSource('map_source')) map.removeSource('map_source');
        marker_array = JSON.parse("[" + String(strii) + "]");
        marker_a = new Marker({color: "#FF0000"}).setLngLat([marker_array[1],marker_array[0]]).addTo(map); 
        fetch(url)
        .then(response => response.json())
        .then(data => {
          apicall = (data)
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
                'fill-color': '#d50b55',
                'fill-opacity': 0.2
            }
          })
          hideSpinner()
          map.setCenter([marker_array[1],marker_array[0]]); 
          })
        .catch(error => {
          console.log(error);
          return [];
        }) 
        toggleNavbar()
    } 
  </script>
  
  {#if popupVisible}
    <div class="popup-overlay">
      <div class="popup">
        <h2>{$_("popup_head")}</h2>
        <p>{$_("popup_text")}</p>
        <button on:click={closePopup}>{$_("popup_button")}</button>
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
    <a href="https://www.maptiler.com" class="watermark"><img
      src="https://api.maptiler.com/resources/logo.svg" alt="MapTiler logo"/></a>
    <div class="map" id="map" bind:this={mapContainer}></div>
  </div>

  <div class="language-switcher">
    <button on:click={() => changeLanguage('en')} class="language-button-en">EN</button>
    <button on:click={() => changeLanguage('de')} class="language-button-de">DE</button>
  </div>
  
  <style>
    
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
      height: calc(100vh); /* calculate height of the screen minus the heading */
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
    }

    .popup button:hover {
      background-color: #3e8e41;
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