// 合规检查页
const api = require('../../utils/api')

Page({
  data: {
    text: '',
    result: null,
    loading: false,
  },

  onInput(e) { this.setData({ text: e.detail.value }) },

  async onCheck() {
    if (!this.data.text.trim()) return
    this.setData({ loading: true, result: null })
    try {
      const data = await api.complianceCheck(this.data.text)
      this.setData({ result: data, loading: false })
    } catch (e) {
      wx.showToast({ title: '检查失败', icon: 'none' })
      this.setData({ loading: false })
    }
  },

  onClear() {
    this.setData({ text: '', result: null })
  },
})
