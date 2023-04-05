<script>
  import Navbar from './lib/Navbar.svelte'
  import Map from './lib/Map.svelte' 
  import { locale, register, init, getLocaleFromNavigator, addMessages } from 'svelte-i18n';

    import en from './localisation/en.json';
    import de from './localisation/de.json';

    addMessages('en', en);
    addMessages('de', de);

    init({
      fallbackLocale: 'en',
      initialLocale: getLocaleFromNavigator(),
    });
</script>

<main>
  <div class="app">
    <Navbar />
    <Map />
  </div>
</main>

<style>
  .app {
  margin: 0;
  padding: 0;
  font-family: sans-serif;
  background-color: #f2f2f2;
  }
</style>
