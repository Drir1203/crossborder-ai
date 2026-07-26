/** 店铺切换状态 */
import { create } from 'zustand'

export interface StoreInfo {
  id: string
  name: string
  platform: string  // shopify / amazon / manual
}

interface StoreStore {
  stores: StoreInfo[]
  currentStoreId: string | null
  setStores: (stores: StoreInfo[]) => void
  setCurrentStore: (id: string | null) => void
}

export const useStoreStore = create<StoreStore>((set) => ({
  stores: [],
  currentStoreId: null,
  setStores: (stores) => set({ stores, currentStoreId: stores[0]?.id || null }),
  setCurrentStore: (id) => set({ currentStoreId: id }),
}))
