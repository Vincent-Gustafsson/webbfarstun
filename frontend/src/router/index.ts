import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../views/AppLayout.vue'
import HomeView from '../views/HomeView.vue'
import AdminView from '../views/AdminView.vue'
import CategoryView from '../views/CategoryView.vue'
import ProductView from '../views/AdminCreateProductView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView,
        },
        {
          path: 'categories/:category_id',
          name: 'categories',
          component: CategoryView,
        },
      ],
    },

    {
      path: '/products',
      name: 'products',
      component: ProductView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
    },
  ],
})

export default router
