import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './views/Home.vue'
import DeviceConfig from './views/DeviceConfig.vue'
import Settings from './views/Settings.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/devices', name: 'DeviceConfig', component: DeviceConfig },
  { path: '/settings', name: 'Settings', component: Settings },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
