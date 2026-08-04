// 首页 - 微信登录 + Dashboard
const api = require('../../utils/api')

Page({
  data: {
    loggedIn: false,
    stats: null,
    loading: false,
  },

  onShow() {
    const token = wx.getStorageSync('token')
    if (token) {
      getApp().globalData.token = token
      this.setData({ loggedIn: true })
      this.loadDashboard()
    }
  },

  // 微信登录
  handleLogin() {
    wx.login({
      success: async (res) => {
        if (res.code) {
          wx.showLoading({ title: '登录中...' })
          try {
            const data = await api.wxLogin(res.code)
            wx.setStorageSync('token', data.access_token)
            getApp().globalData.token = data.access_token
            this.setData({ loggedIn: true })
            wx.hideLoading()
            this.loadDashboard()
          } catch (e) {
            wx.hideLoading()
            wx.showToast({ title: '登录失败', icon: 'none' })
          }
        }
      },
    })
  },

  async loadDashboard() {
    this.setData({ loading: true })
    try {
      const data = await api.getDashboard()
      this.setData({ stats: data, loading: false })
    } catch (e) {
      this.setData({ loading: false })
    }
  },

  // 跳转页面
  goCategory() { wx.switchTab({ url: '/pages/category/category' }) },
  goProfit() { wx.switchTab({ url: '/pages/profit/profit' }) },
  goStoreCheck() { wx.navigateTo({ url: '/pages/storecheck/storecheck' }) },
})
