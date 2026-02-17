import { defineStore } from 'pinia'
import userServices from '@/services/user'
import type { User, UserRegister, UserUpdate } from '@/types/user'
import { getErrorMessage } from '@/utils/error'

export const userStore = defineStore('user', {
  state: () => ({
    users: [] as User[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof UserRegister, string>>,
    lastFetched: null as number | null,
  }),

  getters: {},

  actions: {
    async fetchAll(force = false) {
      const now = Date.now()
      if (
        !force &&
        this.users.length > 0 &&
        this.lastFetched &&
        now - this.lastFetched < 5 * 60 * 1000
      ) {
        return
      }

      this.loading = true
      this.error = null

      try {
        this.users = await userServices.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: UserRegister) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const newUser = await userServices.create(payload)
        this.users.push(newUser)
        return newUser
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors

        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create user'
          this.fieldErrors = {}
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: UserUpdate) {
      this.loading = true
      try {
        const updatedUser = await userServices.update(id, payload)

        const index = this.users.findIndex((c) => c.id === id)
        if (index !== -1) {
          this.users[index] = updatedUser
        }
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousProduct = [...this.users]

      this.users = this.users.filter((c) => c.id !== id)

      try {
        await userServices.delete(id)
      } catch (err: unknown) {
        this.users = previousProduct
        this.error = 'Failed to delete user'
        alert('Could not delete user.')
      }
    },
  },
})
