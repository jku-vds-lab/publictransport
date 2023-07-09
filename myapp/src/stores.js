import { writable } from 'svelte/store';
  
export const url_stored = writable("should be url")
export const marker = writable("should be marker")
export const selectedOption = writable("should be selectedOption")
export const selectedOptionB = writable("should be selectedOption")
export const currentTime = writable("should be currentTime")
export const currentMinutes = writable("should be currentMinutes")
export const isOpen = writable(true);
export const showAltenPflegeHeim = writable(false);
export const showKindergarten = writable(false);
export const showUnis = writable(false);
export const showMus = writable(false);
export const showBib = writable(false);
