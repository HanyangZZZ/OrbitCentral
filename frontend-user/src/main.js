/**
 * main.js — Application Entry Point
 * ====================================
 * PURPOSE:
 *   This is the first file that runs. It creates the Vue app,
 *   plugs in the router, loads global styles, and mounts to the DOM.
 *
 * MODULAR LOGIC:
 *   Vue's plugin system (app.use) lets us add features like routing
 *   without coupling them to the core app. Each plugin is independent.
 *
 * BOOT SEQUENCE:
 *   1. Import Vue, root component, router, and global CSS
 *   2. Create the app instance from App.vue
 *   3. Install the Vue Router plugin
 *   4. Mount to the #app div in index.html
 */
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/global.css'

const app = createApp(App)
app.use(router)     // Install Vue Router for page navigation
app.mount('#app')   // Attach to <div id="app"> in index.html
