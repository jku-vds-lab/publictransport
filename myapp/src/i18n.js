
import { init, getLocaleFromNavigator, register, locale } from 'svelte-i18n';

const SUPPORTED_LOCALES = ['en', 'de'];

register('en', () => import('./localisation/en.json'));
register('de', () => import('./localisation/de.json'));

init({
    fallbackLocale: 'en',
    initialLocale: getLocaleFromNavigator(),
  });

export { locale };