<script>
    import { onMount } from "svelte";
    import { BASE_URL } from "../main";

    let apicall = "kommt Was?"

    onMount(async () => {
      fetch(BASE_URL + "feed?starting_station=Steyr%20Kellaugasse&starting_time=21%3A10%3A00&timelimit=00%3A30%3A00")
      .then(response => response.json())
      .then(data => {
            console.log(data);
            apicall = (data)}).catch(error => {
        console.log(error);
        return [];
      });
    });

    </script>
    
    <main>
        <h1>Whiskey Drinks Menu</h1>
        <p>{apicall}</p>
    </main>
    
    <style>
    
    </style>