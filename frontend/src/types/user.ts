export interface User {
  id: number
  name: string
  email: string
  password: string
  is_admin: boolean
  is_employee: boolean
  is_active: boolean
}

export interface UserRegister {
  email: string
  password: string
  name: string
}

export interface UserUpdate {
  name?: string
  email?: string
  //password
  is_admin?: boolean
  is_employee?: boolean
  is_active?: boolean
}
