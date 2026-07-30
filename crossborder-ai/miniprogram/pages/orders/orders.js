// Shopify 订单查看页
const api = require('../../utils/api')

Page({
  data: {
    channels: [],
    selectedChannel: '',
    orders: [],
    loading: false,
  },

  onLoad() {
    this.loadChannels()
  },

  async loadChannels() {
    try {
      const data = await api.request('GET', '/shopify/channels')
      this.setData({ channels: data || [] })
      if (data && data.length > 0) {
        this.setData({ selectedChannel: data[0].id })
        this.loadOrders(data[0].id)
      }
    } catch (e) { /* ignore */ }
  },

  onChannelChange(e) {
    const id = this.data.channels[e.detail.value].id
    this.setData({ selectedChannel: id })
    this.loadOrders(id)
  },

  async loadOrders(channelId) {
    this.setData({ loading: true })
    try {
      const data = await api.request('GET', `/shopify/orders?channel_id=${channelId}`)
      this.setData({ orders: data || [], loading: false })
    } catch (e) {
      this.setData({ loading: false })
    }
  },

  formatPrice(p) { return `$${parseFloat(p || 0).toFixed(2)}` },
  formatDate(d) { return d ? d.slice(0, 10) : '-' },
})
