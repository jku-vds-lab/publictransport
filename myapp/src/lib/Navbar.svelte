<script>
    import App from "../App.svelte";
    import Api from "./Api.svelte";
    import {isOpen, url_stored, marker, currentMinutes, currentTime, selectedOption} from '../stores.js';
    import { options } from "./options.js";
    import { _ } from 'svelte-i18n';
    import { locale } from '../i18n';
    import { onMount } from 'svelte';
    import { BASE_URL } from "../main";
    
    onMount((async) => {
        // Set the initial value for the select element
        selectedOption.set($_("start_select"))
    });

    selectedOption.set($_("start_select"))

    let currentMinutes_l = null
    let currentTime_l = null
    let sortOpt = options.sort()
    //let start = true
    //let url = null
    //let url2 = null

    //let apicall = "waiting for response..."
    let request_url_start = BASE_URL + "feed?"
    let request_url_start2 = BASE_URL + "marker?"

    const funktionbeiInputMinutes = (e) => {
        currentMinutes_l = e.target.value;
        currentMinutes.update(cm => currentMinutes_l)
    } 

    const funktionbeiInputTime = (e) => {
        currentTime_l = e.target.value;
        currentTime.update(ct => currentTime_l)
    } 

    function toggleNavbar() {
      isOpen.update(value => !value);
    }


</script>

<div class="navbar-container" class:open="{$isOpen}">
  <nav class="navbar">
    <div class="heading">
        <h2>{$_("navbar_title")}</h2>
        <h4>{$_("navbar_describtion")}</h4>

        <select class="headingInput" bind:value={$selectedOption} on:change={() => {
          selectedOption.update(so => $selectedOption)
        }}>
          <option selected disabled>{$_("option_select")}</option> 
          {#each sortOpt as option}
              <option value={option}>{option}</option>
          {/each}
        </select>
        <br />
        <input id="minutesInput" type="text" placeholder="{$_("desc_min")}" value="{currentMinutes_l}" class="headingInput" on:input={funktionbeiInputMinutes}>
        <br />
        <input id="timeInput" type="text" placeholder="{$_("desc_time")}" value="{currentTime_l}" class="headingInput" on:input={funktionbeiInputTime}>
        <br />
        <button on:click="{toggleNavbar}" class="toggle-button">{$_("toggle_navbar")}</button>

    </div>
  </nav>
</div>

<style>
    .heading {
      position: absolute;
      left: 0px;
      top: 0px;
      width: 500px;
      height: 140px;
      z-index: 100;
      margin : 10px;
      margin-left: -20px;
      padding: 10px;
      padding-left: 5px;
      padding-right: 30px;
      padding-bottom: 30px;
      border-radius: 30px;
      background-color: 
  rgb(233, 233, 34);
      color: 
  rgb(24, 10, 10);
    }

    .navbar-container {
      position: fixed;
      top: 10px;
      left: -480px;
      width: 515px;
      height: 205px;
      z-index: 110;
      overflow-x: hidden;
      transition: left 0.35s ease-in-out;
    }

    .navbar-container.open {
      left: 0;
    }

    .toggle-button {
    /* Hier können Sie Stile für die Toggle-Schaltfläche hinzufügen */
      z-index: 100;
      position: relative;
      transform: rotate(270deg);
      font-family: sans-serif;
      font-size: 12px;
      line-height: 18px;
      background: transparent;
      border: none;
      outline: none;
      color: rgb(47, 45, 45);
      top: -85px;
      left: 260px;
    }
  
    .heading > h2 {
      padding: 0px;
      margin: 0px;
    }

    .headingInput {
      position: relative;
      padding: 5px;
      margin: 1px;
      color: rgb(188, 187, 187);
    }

    .headingInput::placeholder {
      color: rgb(188, 187, 187);
    }
    
</style>