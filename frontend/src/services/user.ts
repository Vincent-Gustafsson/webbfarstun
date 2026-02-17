import { http } from '@/utils/http'
import type { User, UserRegister, UserUpdate } from '@/types/user'

export default {
  async getAll() {
    return http.get<User[]>('/users/')
  },

  async getOne(id: number) {
    return http.get<User>(`/users/${id}`)
  },

  async create(data: UserRegister) {
    return http.post<User>('/users/', data)
  },

  async update(id: number, data: UserUpdate) {
    return http.patch<User>(`/users/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<User>(`/users/${id}`)
  },
}
