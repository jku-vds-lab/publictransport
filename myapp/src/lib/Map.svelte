<script>
    import { onMount, onDestroy } from 'svelte'
    import { Map, NavigationControl, Marker, LngLat  } from 'maplibre-gl'
    import 'maplibre-gl/dist/maplibre-gl.css'
    import Navbar from './Navbar.svelte';
    import {url_stored, marker, currentMinutes, currentTime, selectedOption} from '../stores.js';
    import { object_without_properties } from 'svelte/internal';
   
    let spinns;
    let marker_a = new Marker();
    let request_url_start = "http://127.0.0.1:8000/feed?"
    let request_url_start2 = "http://127.0.0.1:8000/marker?"

    function showSpinner() {
      spinns.style.display = "block";
    }

    // Hide spinner
    function hideSpinner() {
      spinns.style.display = "none";
    }

    document.addEventListener("DOMContentLoaded", () => {
    spinns = document.querySelector("#spin");
    }); 

    let map;
    let mapContainer;
    let url = null;
    let url2 = null
    let strii = null
    let apicall = "waiting for apicall...";
    var marker_array = null
    //var ll = new LngLat(Float32Array(marker_array[0]),Float32Array(marker_array[1]))
  
    onMount(() => {
  
      const apiKey = 'QOmo53z4iFjM8sny5h67';
  
      const initialState = { lng: 14.28611, lat: 48.30639, zoom: 12 };
  
      map = new Map({
        container: mapContainer,
        style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
        center: [initialState.lng, initialState.lat],
        zoom: initialState.zoom
      });
  
      map.addControl(new NavigationControl(null),'top-right');
    })

      //new Marker({color: "#FF0000"})
       // .setLngLat([14.28611,48.30639])
        //.addTo(map);
  
    onDestroy(() => {
      map.remove();
    });

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
    } 

  </script>
  
  <div class="map-wrap">
    <div>
      <button on:click={startA}><h4>Start Search</h4></button>
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
  
  <style>

    .map-wrap {
      position: relative;
      width: calc(100vw);
      height: calc(100vh); /* calculate height of the screen minus the heading */
    }
  
    .map {
      position: fixed;
      width: 100%;
      height: 100%;
      color: rgb(24, 10, 10);
      background-color: rgb(233, 233, 34);
    }

    button{
      position: absolute;
      font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
      font-size: 12px;
      line-height: 18px;
      left: 0;
      top: 25%;
      z-index: 900;
      width: 200px;
      height: 10%;
      z-index: 500;
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
      z-index: 999;
    }

    .spinner {
      position: absolute;
      top: 50%;
      left: 50%;
      z-index: 9;
      margin: 10px auto;
      text-align: center;
      font-size: 10px;
    }

    .spinner > div {
      width: 18px;
      height: 18px;
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