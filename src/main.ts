import { createApp } from "vue"
import App from "./App.vue"
import "./index.css"

// Create and mount the Vue application
const app = createApp(App)

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error("[v0] Vue error:", err, info)
}

// Mount the app
app.mount("#app")
