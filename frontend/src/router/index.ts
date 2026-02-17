import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/views/AppLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import HomeView from '@/views/HomeView.vue'
import CategoryView from '@/views/CategoryView.vue'
import ProductView from '@/views/ProductView.vue'
import UserRegisterView from '@/views/UserRegisterView.vue'
import AdminView from '@/views/admin/AdminView.vue'
import AdminCreateProductView from '@/views/admin/AdminCreateProductView.vue'
import AdminCategoryView from '@/views/admin/AdminCategoryView.vue'
import AdminProductGroupView from '@/views/admin/AdminCreateProductGroupView.vue'
import AdminCategoryListView from '@/views/admin/AdminCategoryListView.vue'
import AdminCategoryUpdate from '@/views/admin/AdminCategoryUpdateView.vue'

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
      path: '/account',
      name: 'account',
      component: UserRegisterView,
    },

    {
      path: '/admin',
      component: AdminLayout,
      children: [
        {
          path: '',
          name: 'admin',
          component: AdminView,
        },
        {
          path: 'product-groups',
          name: 'admin-product-groups',
          component: AdminProductGroupView,
        },
        {
          path: 'products',
          name: 'admin-products',
          component: AdminCreateProductView,
        },
        {
          path: 'categories',
          name: 'admin-categories',
          component: AdminCategoryView,
        },
        {
          path: 'list/categories',
          name: 'admin-category-list',
          component: AdminCategoryListView,
        },
        {
          path: 'categories/:category_id/update',
          name: 'admin-category-update',
          component: AdminCategoryUpdate,
          props: true,
        },
      ],
    },
  ],
})

export default router
