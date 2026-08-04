// 整店巡检：查看巡检历史 + 手动触发
const api = require('../../utils/api')

Page({
  data: {
    loading: false,
    checking: false,
    latest: null,
    history: [],
  },

  onShow() {
    this.loadHistory()
  },

  onPullDownRefresh() {
    this.loadHistory().finally(() => wx.stopPullDownRefresh())
  },

  async loadHistory() {
    this.setData({ loading: true })
    try {
      const data = await api.getStoreCheckHistory()
      const items = (data.items || []).map((item) => ({
        ...item,
        time: this.formatTime(item.created_at),
      }))
      this.setData({
        history: items,
        latest: items[0] || null,
        loading: false,
      })
    } catch (e) {
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败，请重试', icon: 'none' })
    }
  },

  async onCheckNow() {
    if (this.data.checking) return
    this.setData({ checking: true })
    try {
      const res = await api.runStoreCheck()
      wx.showToast({ title: res.summary || '巡检完成', icon: 'none' })
      await this.loadHistory()
    } catch (e) {
      const msg = (e && e.detail) || '巡检失败，积分不足或服务异常'
      wx.showToast({ title: String(msg).slice(0, 20), icon: 'none' })
    }
    this.setData({ checking: false })
  },

  formatTime(iso) {
    if (!iso) return ''
    const d = new Date(String(iso).replace(' ', 'T'))
    const pad = (n) => (n < 10 ? '0' + n : n)
    return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`
  },
})
