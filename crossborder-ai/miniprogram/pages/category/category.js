// 品类分析页
const api = require('../../utils/api')

Page({
  data: {
    keyword: '',
    report: '',
    loading: false,
    history: [],
  },

  onLoad() {
    const history = wx.getStorageSync('cat_history') || []
    this.setData({ history })
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  async onAnalyze() {
    if (!this.data.keyword.trim()) {
      wx.showToast({ title: '请输入品类名', icon: 'none' })
      return
    }
    this.setData({ loading: true, report: '' })
    try {
      const data = await api.categoryAnalysis(this.data.keyword)
      this.setData({ report: data.report, loading: false })

      // 保存历史
      const kw = this.data.keyword
      const history = wx.getStorageSync('cat_history') || []
      if (!history.includes(kw)) {
        history.unshift(kw)
        wx.setStorageSync('cat_history', history.slice(0, 10))
        this.setData({ history })
      }
    } catch (e) {
      this.setData({ loading: false })
      wx.showToast({ title: '分析失败', icon: 'none' })
    }
  },

  onHistoryTap(e) {
    const kw = e.currentTarget.dataset.keyword
    this.setData({ keyword: kw })
    this.onAnalyze()
  },

  onClear() {
    wx.removeStorageSync('cat_history')
    this.setData({ history: [] })
  },
})
