import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/views/AppLayout.vue'
import HomeView from '@/views/HomeView.vue'
import CategoryView from '@/views/CategoryView.vue'
import ProductView from '@/views/ProductView.vue'
import AdminView from '@/views/admin/AdminView.vue'
import AdminCreateProductView from '@/views/admin/AdminCreateProductView.vue'
import VariationView from '@/views/admin/AdminVariationVíew.vue'
import AdminCategoryView from '@/views/admin/AdminCategoryView.vue'
import VariationOptionView from '@/views/admin/AdminVariationOptionView.vue'
import AdminProductGroupView from '@/views/admin/AdminCreateProductGroupView.vue'

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
        {
          path: '/products/:id',
          name: 'productDetails',
          component: ProductView,
          props: true,
        },
      ],
    },

    {
      path: '/admin/variations',
      name: 'admin-variations',
      component: VariationView,
    },
    {
      path: '/admin/product-groups',
      name: 'admin-product-groups',
      component: AdminProductGroupView,
    },
    {
      path: '/admin/variation-options',
      name: 'admin-variation-options',
      component: VariationOptionView,
    },

    {
      path: '/admin/products',
      name: 'admin-products',
      component: AdminCreateProductView,
    },
    {
      path: '/admin/categories',
      name: 'admin-categories',
      component: AdminCategoryView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
    },
  ],
})

export default router
