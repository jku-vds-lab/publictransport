<script>
    import App from "../App.svelte";
    import Api from "./Api.svelte";
    import {isOpen, url_stored, marker, currentMinutes, currentTime, selectedOption, selectedOptionB, showAltenPflegeHeim, showKindergarten, showBib, showMus, showUnis} from '../stores.js'; 
    import { options } from "./options.js";
    import { _ } from 'svelte-i18n';
    import { locale } from '../i18n';
    import { onMount } from 'svelte';
    import { BASE_URL } from "../main";
    import { get } from "svelte/store";
    import Svelecte from 'svelecte';
    
    let items = options.map(option => ({value: option, label: option}));

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

        <Svelecte bind:value={$selectedOption} options={items} placeholder={$_("option_select")} virtualList = {true}/>

        <br id="element2"/>
        {$_("min_input_desc")} <input id="minutesInput" type="text" placeholder="{$_("desc_min")}" value="{currentMinutes_l}" class="headingInput" on:input={funktionbeiInputMinutes}>
        <br />
        {$_("time_input_desc")} <input id="timeInput" type="text" placeholder="{$_("desc_time")}" value="{currentTime_l}" class="headingInput" on:input={funktionbeiInputTime}>
        <br />

        {$_("enable_second_dropdown")}

        <Svelecte bind:value={$selectedOptionB} options={items} placeholder={$_("option_select")} virtualList = {true}/>
        
        <br>
        <input class="public_check" type="checkbox" bind:checked={$showAltenPflegeHeim}> {$_("alt_plu")} <span class="altdot"><img class="alt_png_icons" src="/alt.png" alt="elderly care icon"></span>
        <input class="public_check" type="checkbox" bind:checked={$showKindergarten}> {$_("kin_plu")} <span class="kindot"><img class="kin_png_icons" src="/kin.png" alt="kindergarten icon"></span>
        <input class="public_check" type="checkbox" bind:checked={$showUnis}> {$_("uni_plu")} <span class="unidot"><img class="uni_png_icons" src="/uni.png" alt="university icon"></span>
        <br id="element6">
        <input class="public_check" type="checkbox" bind:checked={$showMus}> {$_("mus_plu")} <span class="musdot"><img class="mus_png_icons" src="/mus.png" alt="museum icon"></span>
        <input class="public_check" type="checkbox" bind:checked={$showBib}> {$_("bib_plu")} <span class="bibdot"><img class="bib_png_icons" src="/bib.png" alt="library icon"></span>
      
    </div>
  </nav>
</div>

<div class="toggle-button-div" class:open="{!$isOpen}">
  <button on:click="{toggleNavbar}" class="toggle-button {currentLocale === 'en' ? 'en' : ''}">{$_("toggle_navbar")}</button>
</div>


<style>

  .alt_png_icons {
    width: 100%;
    height: 100%;
    object-fit: cover; /* This keeps the aspect ratio of the image while filling the element */
  }
  .kin_png_icons {
    width: 85%;
    height: 85%;
    object-fit: cover; /* This keeps the aspect ratio of the image while filling the element */
  }
  .uni_png_icons {
    width: 90%;
    height: 90%;
    object-fit: cover; /* This keeps the aspect ratio of the image while filling the element */
  }
  .mus_png_icons {
    width: 70%;
    height: 70%;
    position: relative;
    top: 2px;
    object-fit: cover; /* This keeps the aspect ratio of the image while filling the element */
  }
  .bib_png_icons {
    width: 130%;
    height: 130%;
    position: relative;
    right: 3px;
    bottom: 3px;
    object-fit: cover; /* This keeps the aspect ratio of the image while filling the element */
  }

  :global(.svelecte-control) {
      --sv-active-border: 1px solid rgb(255, 255, 255) !important;
      --sv-border-color: #1A1A1A !important;	
      --sv-hover-border-color: white !important;	
      --sv-bg: #1A1A1A !important;
      --sv-disabled-bg: rgb(47, 45, 45) !important;
      --sv-item-color: rgb(188, 187, 187) !important;
      --sv-item-active-color: #1a1a1a !important;
      --sv-item-btn-bg-hover: rgb(47, 45, 45) !important;
      --sv-highlight-bg: #653939 !important;
      --sv-color: white !important;
    }

  :global(.sv-control) {
    border-radius: 12px !important;
    height: 26px;
    position: relative;
    padding: 0px;
  }

  :global(.svelecte) {
    height: 26px;
    width: 360px;
    left: 70px;
  }

  :global(.sv-dropdown) {
    overflow: clip !important;
    height: 125px;
  }

  .altdot {
    display: inline-block;
    justify-content: center;
    align-items: center;
    width: 20px;
    height: 20px;
    position: relative;
    top: 5px;
    border-radius: 50%;
    background-color: #8ABF98;
    margin-right: 5px;
  }

  .kindot {
    display: inline-block;
    justify-content: center;
    align-items: center;
    width: 20px;
    height: 20px;
    position: relative;
    top: 3px;
    border-radius: 50%;
    background-color: #FFC107;
    margin-right: 5px;
  }
  
  .unidot {
    display: inline-block;
    justify-content: center;
    align-items: center;
    width: 20px;
    height: 20px;
    position: relative;
    top: 5px;
    border-radius: 50%;
    background-color: #B84ED3;
    margin-right: 5px;
  }

  .musdot {
    display: inline-block;
    justify-content: center;
    align-items: center;
    width: 20px;
    height: 20px;
    position: relative;
    top: 0px;
    border-radius: 50%;
    background-color: #1E88E5;
    margin-right: 5px;
  }

  .bibdot {
    display: inline-block;
    justify-content: center;
    align-items: center;
    width: 20px;
    height: 20px;
    position: relative;
    top: 12px;
    border-radius: 50%;
    background-color: #D81B60;
    margin-right: 5px;
  }

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
    height: 365px;
    overflow-y: visible;
    z-index: 110;
    overflow-x: hidden;
    transition: left 0.35s ease-in-out;
  }

  .navbar-container.open {
    left: 0;
  }

  .toggle-button {
      position:absolute;
      z-index: 110;
      margin: 10px;
      transform: rotate(270deg);
      font-family: sans-serif;
      font-size: 12px;
      line-height: 18px;
      background: transparent;
      border: none;
      outline: none;
      color: rgb(47, 45, 45);
    }

    .toggle-button.en {
      left: 22px;
    }
  
    .toggle-button-div {
      position: fixed;
      z-index: 120;
      top: 145px;
      left: 435px;
      transition: left 0.35s ease-in-out;
    }

    .toggle-button-div.open {
      left: -45px;
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