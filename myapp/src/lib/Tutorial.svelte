<script>
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  import {showTutorial} from '../stores.js';
  import { _ } from 'svelte-i18n';
  import { onMount } from 'svelte';

  let progres = 1;
  let cx, cy;
  let places = [
    {id: 1, elementId: 'element1', left: 0, up: 0, rad: 50},
    {id: 2, elementId: 'element2', left: 100, up: 22, rad: 80},
    {id: 3, elementId: 'minutesInput', left: 50, up: 0, rad: 40},
    {id: 4, elementId: 'timeInput', left: 50, up: 0, rad: 40},
    {id: 5, elementId: 'element2', left: 100, up: -100, rad: 80},
    {id: 6, elementId: 'element6', left: 200, up: -20, rad: 140},
    {id: 7, elementId: 'element7', left: 0, up: 0, rad: 40},
    {id: 8, elementId: 'element8', left: 0, up: 0, rad: 100},
    {id: 9, elementId: 'element9', left: 0, up: 0, rad: 60},
    // add more places as needed
  ];

  let currentPlace = places[0];

  let rad_var = tweened(100, { duration: 1000, easing: cubicOut });
  cx = tweened(window.innerWidth / 2, { duration: 1000, easing: cubicOut });
  cy = tweened(window.innerHeight / 2, { duration: 1000, easing: cubicOut });

  onMount(() => {
      updatePosition();
  });

  function nextPlace() {
      let index = places.indexOf(currentPlace);
      progres ++;
      if (index < places.length - 1) {
      currentPlace = places[index + 1];
      updatePosition();
      }  else {
      $showTutorial = false
    }
  }

  function updatePosition() {
      let element = document.getElementById(currentPlace.elementId);
      rad_var.set(currentPlace.rad);
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
      <circle r={$rad_var} fill="black" cx={$cx} cy={$cy}/>
    </mask>
    <rect width="100%" height="100%" fill="rgba(0,0,0,0.8)" mask="url(#mask)"/>
  </svg>
</div>
<div class="infotext">
  <p>{$_("p"+currentPlace.id+"_desc")}</p>
  <button on:click={nextPlace}>{$_("tutorial_confirm")} ({progres}/{places.length})</button>
</div>

<style>
  .infotext {
      position: absolute;
      width: 340px; 
      height: 140px;
      z-index: 10000;
      left: 50%;
      top: 50%;
      background-color: white;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      transform: translate(-50%, -50%);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
  }

  .infotext p {
    text-align: center;
    margin: 0;
    flex-grow: 1;
    display: flex;
    align-items: center; 
    justify-content: center; 
  }

  .infotext button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 5px;
    align-self: center;
  }

  .infotext button:hover {
    background-color: #3e8e41;
    color: white;
  }

</style>