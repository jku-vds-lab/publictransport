<script>
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    import {showTutorial} from '../stores.js';
    import { _ } from 'svelte-i18n';
    import { onMount } from 'svelte';
  
    let cx, cy;
    let places = [
      {id: 1, elementId: 'element1', left: 0, up: 0},
      {id: 2, elementId: 'element2', left: 100, up: 22},
      {id: 3, elementId: 'minutesInput', left: 50, up: 0},
      {id: 4, elementId: 'timeInput', left: 50, up: 0},
      {id: 5, elementId: 'element2', left: 100, up: -100},
      {id: 6, elementId: 'element6', left: 200, up: -20},
      {id: 7, elementId: 'element7', left: 0, up: 0},
      {id: 8, elementId: 'element8', left: 0, up: 0},
      {id: 9, elementId: 'element9', left: 0, up: 0},
      // add more places as needed
    ];
  
    let currentPlace = places[0];

    cx = tweened(window.innerWidth / 2, { duration: 1000, easing: cubicOut });
    cy = tweened(window.innerHeight / 2, { duration: 1000, easing: cubicOut });

    onMount(() => {
        updatePosition();
    });
  
    function nextPlace() {
        let index = places.indexOf(currentPlace);
        if (index < places.length - 1) {
        currentPlace = places[index + 1];
        updatePosition();
        }  else {
        $showTutorial = false
      }
    }

    function updatePosition() {
        let element = document.getElementById(currentPlace.elementId);
        if (element) {
        let rect = element.getBoundingClientRect();
        cx.set(rect.x + rect.width / 2 - currentPlace.left);
        cy.set(rect.y + rect.height / 2 - currentPlace.up);
        }
    }
  </script>
  
  <div id="overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.01); z-index: 9999;">
    <svg width="100%" height="100%">
      <mask id="mask">
        <rect width="100%" height="100%" fill="white"/>
        <circle r="100" fill="black" cx={$cx} cy={$cy}/>
      </mask>
      <rect width="100%" height="100%" fill="rgba(0,0,0,0.8)" mask="url(#mask)"/>
    </svg>
  </div>
  <div class="infotext">
    <p>{$_("p"+currentPlace.id+"_desc")}</p>
    <button on:click={nextPlace}>{$_("tutorial_confirm")}</button>
  </div>

<style>
    .infotext {
        position: absolute;
        width: 200px; 
        z-index: 10000;
        left: 50%;
        top: 50%;
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        transform: translate(-50%, -50%);
    }

    .infotext button {
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

    .infotext button:hover {
      background-color: #3e8e41;
      color: white;
    }
</style>