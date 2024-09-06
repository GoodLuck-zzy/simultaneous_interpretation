import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/record',
      name: 'record',
      component: () => import('../views/Record.vue')
    }
  ]
})

export default router
