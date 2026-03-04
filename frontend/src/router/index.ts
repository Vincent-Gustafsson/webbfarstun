import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/views/AppLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import HomeView from '@/views/HomeView.vue'
import CategoryView from '@/views/CategoryView.vue'
import ProductView from '@/views/ProductView.vue'
import UserRegisterView from '@/views/UserRegisterView.vue'
import UserLoginView from '@/views/UserLoginView.vue'
import AdminView from '@/views/admin/AdminView.vue'
import AdminCreateProductView from '@/views/admin/product/CreateView.vue'
import AdminCategoryView from '@/views/admin/category/CreateView.vue'
import AdminProductGroupView from '@/views/admin/productGroup/CreateView.vue'
import AdminCategoryListView from '@/views/admin/category/ListView.vue'
import AdminCategoryUpdateView from '@/views/admin/category/UpdateView.vue'
import AdminProductListView from '@/views/admin/product/ListView.vue'
import AdminProductUpdateView from '@/views/admin/product/UpdateView.vue'
import AdminProductGroupListView from '@/views/admin/productGroup/ListView.vue'
import AdminProductGroupUpdateView from '@/views/admin/productGroup/UpdateView.vue'
import { useUserStore } from '@/stores/user'

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
      path: '/account/register',
      name: 'account-register',
      component: UserRegisterView,
    },
    {
      path: '/account/login',
      name: 'account-login',
      component: UserLoginView,
    },

    {
      path: '/admin',
      component: AdminLayout,
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
      },
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
          props: true,
        },
        {
          path: 'list/products',
          name: 'admin-product-list',
          component: AdminProductListView,
          props: true,
        },
        {
          path: 'list/product-groups',
          name: 'admin-product-group-list',
          component: AdminProductGroupListView,
          props: true,
        },
        {
          path: 'categories/:category_id/update',
          name: 'admin-category-update',
          component: AdminCategoryUpdateView,
          props: true,
        },
        {
          path: 'products/:product_id/update',
          name: 'admin-product-update',
          component: AdminProductUpdateView,
          props: true,
        },
        {
          path: 'product-groups/:product_group_id/update',
          name: 'admin-product-group-update',
          component: AdminProductGroupUpdateView,
          props: true,
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const store = useUserStore()

  // Make sure we know the login state once per refresh
  if (!store.authChecked) {
    await store.fetchMe()
  }

  const isAuthed = !!store.me
  const isAdmin = !!store.me && (store.me.is_admin || store.me.is_employee)

  // Block protected routes
  if (to.meta.requiresAuth && !isAuthed) {
    return { name: 'account-login', query: { redirect: to.fullPath } }
  }

  // Block admin routes
  if (to.meta.requiresAdmin && !isAdmin) {
    return { name: 'home' } // or a dedicated forbidden page
  }

  // Prevent logged-in users from visiting login/register
  if (to.meta.requiresGuest && isAuthed) {
    return { name: 'home' }
  }

  return true
})

export default router
