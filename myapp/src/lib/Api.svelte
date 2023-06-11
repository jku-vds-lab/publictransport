<script>
    import { onMount } from "svelte";
    import { BASE_URL } from "../main";

    let apicall = "waiting"

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
        <p>{apicall}</p>
    </main>
    
    <style>
    
    </style>