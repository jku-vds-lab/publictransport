import './app.css'
import App from './App.svelte'
//let map: google.maps.Map;

// export const BASE_URL = "http://127.0.0.1:9000/" // for local development
export const BASE_URL = "" // for AWS/docker

const app = new App({
  target: document.getElementById('app'),
  //target: document.body,
  props: {}
})

export default app
