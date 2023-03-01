import { writable } from 'svelte/store';
  
export const url_stored = writable("should be url")
export const marker = writable("should be marker")
export const selectedOption = writable("should be selectedOption")
export const currentTime = writable("should be currentTime")
export const currentMinutes = writable("should be currentMinutes")
