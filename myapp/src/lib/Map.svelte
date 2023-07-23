<script>
    import { onMount, onDestroy } from 'svelte'
    import { Map, NavigationControl, Marker, LngLat, Popup  } from 'maplibre-gl'
    import 'maplibre-gl/dist/maplibre-gl.css'
    import Navbar from './Navbar.svelte';
    import {isOpen, url_stored, marker, currentMinutes, currentTime, selectedOption, selectedOptionB, showAltenPflegeHeim, showKindergarten, showBib, showMus, showUnis, showKra, showCin, showSch, showTutorial} from '../stores.js';
    import { alten_pflege_coords } from "./alten_pflege_heim.js";
    import { kinder_coords } from "./kindergarten.js";
    import { unis_coords } from './unis';
    import { mus_coords } from './mus';
    import { bib_coords } from './bib';
    import { cin_coords } from './cin';
    import { kra_coords } from './kra';
    import { sch_coords } from './sch';  
    import { object_without_properties } from 'svelte/internal';
    import { _ } from 'svelte-i18n'
    import { locale } from '../i18n';
    import { BASE_URL } from '../main';
    import { get } from 'svelte/store';
    import Tutorial from './Tutorial.svelte';
   
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
    let CurrentPosStation;
    let markerCurPos;

    function getCoords() {
      isGettingCoords = true;
      map.getCanvas().style.cursor = 'crosshair';
    }

    function getCurrent() {
      selectedOption.set(CurrentPosStation);
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
      CurrentPosStation = nearStation;
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

    function closePopup2() {
      popupVisible2 = false;
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
    let popupVisible2 = false;
    let popup2List = [null, null, null,  null, null];
    let popup2DistList = [null, null, null,  null, null];
    let legendVisible = false;
    let initialState = null;
    let nearStation = null;
    let yourCoords_ = null;


    const check_first_popup = {};
    check_first_popup["bib"] = true; 
    check_first_popup["mus"] = true;
    check_first_popup["unis"] = true;
    check_first_popup["pflege"] = true;
    check_first_popup["kindergarten"] = true;
    check_first_popup["cin"] = true; 
    check_first_popup["kra"] = true; 
    check_first_popup["sch"] = true; 
  
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

        // if a marker already exists, remove it
        if (markerCurPos) {
          markerCurPos.remove();
        }
        // add a new marker at the clicked location
        markerCurPos = new Marker()
          .setLngLat([lng, lat])
          .addTo(map);

        initialState.lat = lat
        initialState.lng = lng
        isGettingCoords = false;
        map.getCanvas().style.cursor = '';
        startClosestStation().then(() => {
          popupVisible2 = true
          legendVisible = false
          yourCoords_ = `${lng.toFixed(3)}, ${lat.toFixed(3)}`
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
        clusterMaxZoom: 12,
        clusterRadius: 50
      });
      // Add cluster layer
      addCluster('pflege', '#8ABF98', '/alt.png');
      } else {
      // Remove source and layers
      try {
        map.removeLayer('pflege-cluster');
        map.removeLayer('pflege-cluster-count');
        map.removeLayer('pflege-point');
        map.removeLayer('pflege-point_background');
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
        clusterMaxZoom: 12,
        clusterRadius: 50
      });
      addCluster('kindergarten', '#FFC107', '/kin.png');
      } else {
      try {
        map.removeLayer('kindergarten-cluster');
        map.removeLayer('kindergarten-cluster-count');
        map.removeLayer('kindergarten-point');
        map.removeLayer('kindergarten-point_background');
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
        clusterMaxZoom: 12,
        clusterRadius: 50
      });

      addCluster('unis', '#B84ED3', '/uni.png');
      } else {
      try {
        map.removeLayer('unis-cluster');
        map.removeLayer('unis-cluster-count');
        map.removeLayer('unis-point');
        map.removeLayer('unis-point_background');
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
        clusterMaxZoom: 12,
        clusterRadius: 50
      });

      addCluster('mus', '#1E88E5', '/mus.png');
      } else {
      try {
        map.removeLayer('mus-cluster');
        map.removeLayer('mus-cluster-count');
        map.removeLayer('mus-point');
        map.removeLayer('mus-point_background');
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
        clusterMaxZoom: 12,
        clusterRadius: 50
      });

      addCluster('bib', '#D81B60', '/bib.png');
      } else {
      try {
        map.removeLayer('bib-cluster');
        map.removeLayer('bib-cluster-count');
        map.removeLayer('bib-point');
        map.removeLayer('bib-point_background');
        map.removeSource('bib');
      } catch (error) {
        //nothing
      }
    }

    // Kinos
    $: if ($showCin) {
      const geojson = {
        type: 'FeatureCollection',
        features: cin_coords.map(coord => ({
          type: 'Feature',
          properties: { name: 'Cinema' },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };

      map.addSource('cin', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 12,
        clusterRadius: 50
      });

      addCluster('cin', '#A4A9FF', '/cin.png'); //color
      } else {
      try {
        map.removeLayer('cin-cluster');
        map.removeLayer('cin-cluster-count');
        map.removeLayer('cin-point');
        map.removeLayer('cin-point_background');
        map.removeSource('cin');
      } catch (error) {
        //nothing
      }
    }

    // Krankenanstalten
    $: if ($showKra) {
      const geojson = {
        type: 'FeatureCollection',
        features: kra_coords.map(coord => ({
          type: 'Feature',
          properties: { name: coord[2] }, //name coord[2]
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };

      map.addSource('kra', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 12,
        clusterRadius: 50
      });

      addCluster('kra', '#e5743c', '/kra.png');
      } else {
      try {
        map.removeLayer('kra-cluster');
        map.removeLayer('kra-cluster-count');
        map.removeLayer('kra-point');
        map.removeLayer('kra-point_background');
        map.removeSource('kra');
      } catch (error) {
        //nothing
      }
    }

    // Schulen
    $: if ($showSch) {
      const geojson = {
        type: 'FeatureCollection',
        features: sch_coords.map(coord => ({
          type: 'Feature',
          properties: { name: coord[2] },
          geometry: {
            type: 'Point',
            coordinates: [coord[1], coord[0]]
          }
        }))
      };

      map.addSource('sch', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 12,
        clusterRadius: 50
      });

      addCluster('sch', '#EF798A', '/sch.png');
      } else {
      try {
        map.removeLayer('sch-cluster');
        map.removeLayer('sch-cluster-count');
        map.removeLayer('sch-point');
        map.removeLayer('sch-point_background');
        map.removeSource('sch');
      } catch (error) {
        //nothing
      }
    }

    // Function to add a clustered layer for a group of markers
    function addCluster(id, color, pathPic) {
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

      map.loadImage(pathPic, function(error, image) {
        if (error) {
          //nothing
        };
        if (pathPic == '/uni.png') {
          map.addImage('uniIcon', image);     
          map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.055,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'uniIcon',
            }
          })
        } else if (pathPic == '/mus.png') {
        map.addImage('musIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.025,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'musIcon',
            'icon-rotate': 0,
            } 
          })
        } else if (pathPic == '/alt.png') {
        map.addImage('altIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.045,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'altIcon',
            }
          })
        } else if (pathPic == '/bib.png') {
        map.addImage('bibIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.07,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'bibIcon',
            }
          })
        } else if (pathPic == '/cin.png') {
        map.addImage('cinIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.043,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'cinIcon',
            }
          })
        } else if (pathPic == '/kra.png') {
        map.addImage('kraIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.045,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'kraIcon',
            }
          })
        } else if (pathPic == '/sch.png') {
        map.addImage('schIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.04,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'schIcon',
            }
          })
        } else if (pathPic == '/kin.png') {
        map.addImage('kinIcon', image);
        map.addLayer({
          id: id + '-point',
          type: 'symbol',
          source: id,
          filter: ['!', ['has', 'point_count']],
          layout: {
            'icon-size': 0.06,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center',
            'icon-optional': true,
            'icon-image': 'kinIcon',
            }
          })
        } 
      });

      // determine the icon size
      let iconSize = 0.03; // default size
      let iconOffset = [0, 0]
      let type = pathPic.substring(1,4);

      switch(type) {
        case 'kin':
          iconSize = 0.039;
          break;
        case 'uni':
          iconSize = 0.035;
          break;
        case 'mus':
          iconSize = 0.016;
          break;
        case 'bib':
          iconSize = 0.043;
          iconOffset = [-120, 0];
          break;
        case 'cin':
          iconSize = 0.033;
          iconOffset = [-80, 0];
          break;
        case 'kra':
          iconSize = 0.033;
          iconOffset = [-80, 0];
          break;
        case 'sch':
          iconSize = 0.03;
          iconOffset = [-100, -40];
          break;
        case 'alt':
          iconSize = 0.03;
          iconOffset = [-200, 0];
          break;
      }

      map.addLayer({
        id: id + '-cluster-count',
        type: 'symbol',
        source: id,
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}' ,
          'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
          'text-size': 12,
          'text-anchor': 'right',
          'text-offset': [-0.42, 0],
          'icon-size': iconSize,
          'icon-allow-overlap': false,
          'icon-ignore-placement': true,
          'icon-anchor': 'left',
          'icon-optional': true,
          'icon-offset': iconOffset,
          'icon-image': pathPic.substring(1,4)+'Icon',
        }
      });


      map.addLayer({
        id: id + '-point_background',
        type: 'circle',
        source: id,
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': color,
          'circle-radius': 18,
          'circle-stroke-width': 0,
          'circle-stroke-color': '#fff',
        }
      });

      // Add popup
      if (check_first_popup[id]) {
        map.on('click', id + '-point', function (e) {
          var coordinates = e.features[0].geometry.coordinates.slice();
          var name = e.features[0].properties.name;

          new Popup({ offset: [0, -10] })
              .setLngLat(coordinates)
              .setHTML(name)
              .addTo(map);
        });
        check_first_popup[id] = false;
      }

      // Add popup on mouseenter
      map.on('mouseenter', id + '-point', function (e) {
        map.getCanvas().style.cursor = 'pointer';
      });
      // Remove popup on mouseleave
      map.on('mouseleave', id + '-point', function () {
        map.getCanvas().style.cursor = '';
      });
    }

    //tooltip select Position function (GetCoordsButton)
    function tooltip(node, ctx) {
      const tip = document.createElement('span');
      if (ctx == "legend_desc") {
        tip.className = 'tooltip2';
      } else if (ctx == "tooltip_select_custom_place") {
        tip.className = 'tooltip';
      } else {
        tip.className = 'tooltip3';
      }
      tip.textContent = $_(ctx);
      node.appendChild(tip);

      const update = () => {
          tip.textContent = $_(ctx);
      };

      update();

      const unsubscribe = locale.subscribe(() => {
        update();
      });

      const handleMouseover = () => {
        tip.style.visibility = 'visible';
      };

      const handleMouseout = () => {
        tip.style.visibility = 'hidden';
      };

      node.addEventListener('mouseover', handleMouseover);
      node.addEventListener('mouseout', handleMouseout);

      return {
        update,
        destroy() {
          unsubscribe();
          node.removeEventListener('mouseover', handleMouseover);
          node.removeEventListener('mouseout', handleMouseout);
        }
      };
    }

    function toggleNavbar() {
      isOpen.update(value => !value);
    }

    const startAction = () => {
      return new Promise((resolve, reject) => {
        let force_setting = "&forced=forced" //secondDropdown Enabled
        if ($selectedOptionB == null) { //secondDropdown Disabled
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
            let rawData = data.toString()
            nearStation = rawData.split(";")[0]
            popup2List[0] = rawData.split(";")[0]
            popup2List[1] = rawData.split(";")[2]
            popup2List[2] = rawData.split(";")[4]
            popup2List[3] = rawData.split(";")[6]
            popup2List[4] = rawData.split(";")[8]
            popup2DistList[0] = rawData.split(";")[1]
            popup2DistList[1] = rawData.split(";")[3]
            popup2DistList[2] = rawData.split(";")[5]
            popup2DistList[3] = rawData.split(";")[7]
            popup2DistList[4] = rawData.split(";")[9]
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
        legendVisible = true;
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
        if (!($selectedOptionB==null)) {
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

  {#if $showTutorial}
    <Tutorial />
  {/if}

  <div id = "element9" class = "top_right_dot">
    .X
  </div>
  
  {#if popupVisible}
    <div class="popup-overlay">
      <div class="popup">
        <h2>{$_("popup_head")}</h2>
        <p>{$_("popup_text")}</p>
        <button on:click={closePopup}>{$_("popup_button")}</button>
        <button on:click={() => {
          $showTutorial = true; 
          closePopup();
        }}>{$_("tutorial_start_button")}</button>
        <button on:click={() => window.open('https://forms.office.com/e/Gvf0iveeWc', '_blank')} class="popup-button secondary">{$_("link_quiz")}</button>
      </div>
    </div>
  {/if}

  {#if popupVisible2}
      <div class="popup2">
        <h2>{yourCoords_}</h2>
        <p>{$_("popup_curpos_text")}</p>
        <button on:click={() => {selectedOption.set(popup2List[0]);closePopup2();markerCurPos.remove()}} class="popup-button secondary">{popup2List[0] +" ("+ popup2DistList[0]+")"}</button>
        <button on:click={() => {selectedOption.set(popup2List[1]);closePopup2();markerCurPos.remove()}} class="popup-button secondary">{popup2List[1] +" ("+ popup2DistList[1]+")"}</button>
        <button on:click={() => {selectedOption.set(popup2List[2]);closePopup2();markerCurPos.remove()}} class="popup-button secondary">{popup2List[2] +" ("+ popup2DistList[2]+")"}</button>
        <button on:click={() => {selectedOption.set(popup2List[3]);closePopup2();markerCurPos.remove()}} class="popup-button secondary">{popup2List[3] +" ("+ popup2DistList[3]+")"}</button>
        <button on:click={() => {selectedOption.set(popup2List[4]);closePopup2();markerCurPos.remove()}} class="popup-button secondary">{popup2List[4] +" ("+ popup2DistList[4]+")"}</button>
        <button class="close-button" on:click={() => {closePopup2();markerCurPos.remove()}}>X</button>
      </div>
  {/if}

  <div class="map-wrap">
    <div>
      <button class= "startsearchb" id="element8" on:click={startA}><h4>{$_("start_search")}</h4></button>
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

  <div class="GetCoordsButtonDiv" id="element7" class:open="{!$isOpen}">
    <button on:click={getCoords} class="GetCoordsButton" use:tooltip={"tooltip_select_custom_place"}>.</button>
  </div>

  <div class="CurrentPosButtonDiv" id="element10" class:open="{!$isOpen}">
    <button on:click={getCurrent} class="CurrentPosButton" use:tooltip={"tooltip_current_pos_button"}>.</button>
  </div>

  {#if legendVisible}
    <div class="legend_field_div" use:tooltip={"legend_desc"}>
      <div class="legend_header">
        {$_("legend_header")} <br>
      </div>
      <span class="legend_dot1"></span> 3 Min<br>
      <span class="legend_dot2"></span> 10 Min<br>
      <span class="legend_dot3"></span> 15 Min
    </div>
  {/if}

  <div class="language-switcher" id="element1">
    <button on:click={() => changeLanguage('en')} class="language-button-en">EN</button>
    <button on:click={() => changeLanguage('de')} class="language-button-de">DE</button>
  </div>
  
  <style>
    .top_right_dot{
      position: absolute;
      top: 46px;
      right: 20px;
      z-index: 1;
    }

    .legend_header {
      text-align: center;
      font-weight: bold;
    }

    .legend_dot1 {
      display: inline-block;
      justify-content: center;
      align-items: center;
      width: 10px;
      height: 10px;
      position: relative;
      top: 3px;
      right: 16px;
      border-radius: 50%;
      background-color: #ff8400a2;
      margin-right: 5px;
    }

    .legend_dot2 {
      display: inline-block;
      justify-content: center;
      align-items: center;
      width: 20px;
      height: 20px;
      position: relative;
      top: 8px;
      right: 5px;
      border-radius: 50%;
      background-color: #ff8400a2;
      margin-right: 5px;
    }

    .legend_dot3 {
      display: inline-block;
      justify-content: center;
      align-items: center;
      width: 30px;
      height: 30px;
      position: relative;
      top: 10px;
      border-radius: 50%;
      background-color: #ff8400a2;
      margin-right: 5px;
    }

    .legend_field_div {
      position: fixed;
      z-index: 100;
      top: 110px;
      right: 10px;
      background-color: #fff;
      padding: 10px;
      border-radius: 10px;
      text-align: right;
      box-shadow: 0 0 0 2px rgba(0,0,0,.1);
    }

    :global(.tooltip3) {
      visibility: hidden;
      background-color: rgba(255, 255, 255, 0.8);
      color: black;
      border-radius: 10px;
      text-align: center;
      padding: 7px;
      position: absolute;
      width: 100px;
      z-index: 1;
      top: 50%;
      left: 260%;
      transform: translate(-50%, -50%);
    }

    :global(.tooltip2) {
      visibility: hidden;
      background-color: rgba(255, 255, 255, 0.8);
      color: black;
      border-radius: 10px;
      text-align: center;
      padding: 7px;
      position: absolute;
      width: 100px;
      z-index: 1;
      top: 50%;
      right: 50%;
      transform: translate(-50%, -50%);
    }

    :global(.tooltip) {
      visibility: hidden;
      background-color: rgba(255, 255, 255, 0.8);
      color: black;
      border-radius: 10px;
      text-align: center;
      padding: 7px;
      position: absolute;
      width: 100px;
      z-index: 1;
      top: 50%;
      left: 340%;
      transform: translate(-50%, -50%);
    }

    .CurrentPosButton {
      color: transparent;
      background-color: transparent;
      background-image: url('../crosshair.svg');
      background-position: center;
      background-repeat: no-repeat;
      border: none;
      outline: none;
      z-index: 120;
      height: 25px;
      background-size: 65%;
    }

    .CurrentPosButton:active {
      background-size: 55%;
    }

    .CurrentPosButtonDiv {
      position: fixed;
      z-index: 120;
      top: 90px;
      left: 445px;
      transition: left 0.35s ease-in-out;
    }

    .CurrentPosButtonDiv.open {
      left: -65px;
    }

    .GetCoordsButton {
      color: transparent;
      background-color: transparent;
      background-image: url('../map-pin.svg');
      background-position: center;
      background-repeat: no-repeat;
      border: none;
      outline: none;
      z-index: 120;
      height: 25px;
      background-size: 50%;
    }

    .GetCoordsButton:active {
      background-size: 40%;
    }

    .GetCoordsButtonDiv {
      position: fixed;
      z-index: 120;
      top: 90px;
      left: 415px;
      transition: left 0.35s ease-in-out;
    }

    .GetCoordsButtonDiv.open {
      left: -65px;
    }

    .language-switcher {
      position: fixed;
      bottom: 25px;
      right: 5px;
      border-radius: 5px;
      padding: 5px;
      z-index: 10010;
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
      box-shadow: -10px 4px 4px 4px rgba(0,0,0,.1);
      z-index: 100; 
      position: fixed;
      font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
      font-size: 12px;
      line-height: 18px;
      left: 0;
      top: 365px;
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

    .popup2 {
      position: fixed;
      right: 50px;
      top: 20px;
      background-color: white;
      padding: 20px;
      z-index: 999 !important;
      border-radius: 10px;
      width: 200px;
      text-align: center;
    }

    .popup2 h2 {
      margin-top: 0;
    }

    .popup2 button {
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

    .popup2 button:hover {
      background-color: #3e8e41;
      color: white;
    }

    .close-button {
      position: absolute;
      top: 10px;
      right: 10px;
      padding: 0px 0px !important;
      width: 15px !important;
      height: 15px !important;
      background-color: rgba(245, 5, 5, 0.735) !important;
      margin-top: 0px !important;
      border: none !important;
      border-radius: 50% !important;
      cursor: pointer;
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