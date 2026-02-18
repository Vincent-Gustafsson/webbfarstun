import { http } from '@/utils/http'
import type { User, UserRegister, UserUpdate } from '@/types/user'

export type TokenOut = { access_token: string; token_type: string }

export default {
  async getAll() {
    return http.get<User[]>('/users/')
  },

  async getOne(id: number) {
    return http.get<User>(`/users/${id}`)
  },

  async create(data: UserRegister) {
    return http.post<User>('/auth/register', data)
  },

  async update(id: number, data: UserUpdate) {
    return http.patch<User>(`/users/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<User>(`/users/${id}`)
  },

  async me() {
    return http.get<User>('/users/me')
  },

  async login(email: string, password: string) {
    return http.postForm<TokenOut>('/auth/login', {
      username: email,
      password,
    })
  },

  async logout() {
    return http.post<{ ok: boolean }>('/auth/logout', {})
  },
}
