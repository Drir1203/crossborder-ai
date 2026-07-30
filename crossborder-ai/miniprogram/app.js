// VeyaShip AI - 小程序入口
App({
  globalData: {
    token: '',
    apiBase: 'https://veyaship.com/api/v1',
  },
  onLaunch() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },
})
