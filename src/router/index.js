import { createRouter, createWebHistory } from 'vue-router'
import Wrapper from '../components/Wrapper.vue'

const routes = [
  {
    path: '/',
    name: 'Top',
    component: Wrapper
  },
  {
    path: '/reader',
    name: 'Root',
    component: Wrapper
  },
  {
    path: '/reader/:bookNumber',
    name: 'Book',
    component: Wrapper,
    props: true
  },
  {
    path: '/reader/:bookNumber/:chapterNumber',
    component: Wrapper,
    name: 'Chapter',
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
