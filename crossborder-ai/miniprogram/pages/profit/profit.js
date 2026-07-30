// 利润计算器
const api = require('../../utils/api')

Page({
  data: {
    form: {
      selling_price: 19.99,
      platform_fee_rate: 0.15,
      product_cost: 30,
      shipping_cost: 15,
      advertising_cost: 5,
      exchange_rate: 7.2,
    },
    result: null,
    loading: false,
  },

  onInput(e) {
    const { field } = e.currentTarget.dataset
    const value = parseFloat(e.detail.value) || 0
    this.setData({ [`form.${field}`]: value })
  },

  async onCalculate() {
    this.setData({ loading: true })
    try {
      const data = await api.calculateProfit(this.data.form)
      this.setData({ result: data, loading: false })
    } catch (e) {
      wx.showToast({ title: '计算失败', icon: 'none' })
      this.setData({ loading: false })
    }
  },
})
