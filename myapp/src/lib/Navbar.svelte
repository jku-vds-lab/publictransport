<script>
    import App from "../App.svelte";
    import Api from "./Api.svelte";
    import {isOpen, url_stored, marker, currentMinutes, currentTime, selectedOption, selectedOptionB, secondDropdownEnabled, showAltenPflegeHeim, showKindergarten, showBib, showMus, showUnis} from '../stores.js'; 
    import { options } from "./options.js";
    import { _ } from 'svelte-i18n';
    import { locale } from '../i18n';
    import { onMount } from 'svelte';
    import { BASE_URL } from "../main";
    import { get } from "svelte/store";
    
    onMount((async) => {
        // Set the initial value for the select element
        selectedOption.set($_("start_select"))
        selectedOptionB.set($_("start_select"))
    });

    selectedOption.set($_("start_select"))
    selectedOptionB.set($_("start_select"))

    let currentMinutes_l = null
    let currentTime_l = null
    let sortOpt = options.sort()

    let currentLocale;
    locale.subscribe(value => {
      currentLocale = value;
    });
    //let start = true
    //let url = null
    //let url2 = null

    //let apicall = "waiting for response..."
    let request_url_start = BASE_URL + "feed?"
    let request_url_start2 = BASE_URL + "marker?"

    const funktionbeiInputMinutes = (e) => {
      let value = e.target.value;
      if (Number.isInteger(Number(value))) {
        currentMinutes_l = value;
        currentMinutes.update(cm => currentMinutes_l)
      } else {
        let alertM = get(_)("integerAlert")
        alert(alertM);
        currentMinutes_l = "";
        currentMinutes.update(cm => currentMinutes_l)
      }
    }  

    const funktionbeiInputTime = (e) => {
      let currentTime_l = e.target.value;
      let parts = currentTime_l.split(":");
      if (parts[0].length === 1) {
        parts[0] = "0" + parts[0];
      }
      currentTime_l = parts.join(":");
      currentTime.update(ct => currentTime_l);
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

        <label class="checkBox">
          <input type="checkbox" bind:checked={$secondDropdownEnabled}> 
          {$_("enable_second_dropdown")}
        </label>

        <button on:click="{toggleNavbar}" class="toggle-button {currentLocale === 'en' ? 'en' : ''}">{$_("toggle_navbar")}</button>

        <select class="headingInput" bind:value={$selectedOptionB} on:change={() => {
          selectedOptionB.update(so => $selectedOptionB)
        }} disabled={!$secondDropdownEnabled}>
          <option selected disabled>{$_("option_select")}</option> 
          {#each sortOpt as option} 
              <option value={option}>{option}</option>
          {/each}
        </select>
        
        <br>
        <input class="public_check" type="checkbox" bind:checked={$showAltenPflegeHeim}> {$_("alt_plu")}
        <input class="public_check" type="checkbox" bind:checked={$showKindergarten}> {$_("kin_plu")}
        <input class="public_check" type="checkbox" bind:checked={$showUnis}> {$_("uni_plu")}
        <br>
        <input class="public_check" type="checkbox" bind:checked={$showMus}> {$_("mus_plu")}
        <input class="public_check" type="checkbox" bind:checked={$showBib}> {$_("bib_plu")}
      
    </div>
  </nav>
</div>

<style>
    .public_check {
      position: sticky;
      display: flexbox;
    }

    .heading {
      position: absolute;
      left: 0px;
      top: 0px;
      width: 500px;
      height: 240;
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
      height: 300px;
      overflow-y: hidden;
      z-index: 110;
      overflow-x: hidden;
      transition: left 0.35s ease-in-out;
    }

    .navbar-container.open {
      left: 0;
    }

    .toggle-button {
      position: absolute;
      z-index: 100;
      transform: rotate(270deg);
      font-family: sans-serif;
      font-size: 12px;
      line-height: 18px;
      background: transparent;
      border: none;
      outline: none;
      color: rgb(47, 45, 45);
      top: 115px !important;
      left: 460px !important;
    }

    .toggle-button.en {
    left: 485px !important;
    }
  
    .heading > h2 {
      padding: 0px;
      margin: 2px;
    }

    .heading > h4 {
      padding: 0px;
      margin: 6px;
      margin-bottom: 10px;
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

    .checkBox {
      display: block;
    }

    
</style>