import apiClient from './client'
import type { Product, ProductCreate, ProductListResponse } from '@/types'

export const productsApi = {
  list: async (params?: {
    search?: string
    category?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }): Promise<ProductListResponse> => {
    const response = await apiClient.get('/products', { params })
    return response.data
  },

  getById: async (id: number): Promise<Product> => {
    const response = await apiClient.get(`/products/${id}`)
    return response.data
  },

  create: async (data: ProductCreate): Promise<Product> => {
    const response = await apiClient.post('/products', data)
    return response.data
  },

  update: async (id: number, data: Partial<ProductCreate>): Promise<Product> => {
    const response = await apiClient.put(`/products/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/products/${id}`)
  },
}
