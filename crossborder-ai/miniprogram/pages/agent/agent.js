// AI 助手对话页
const api = require('../../utils/api')

Page({
  data: {
    messages: [],
    input: '',
    loading: false,
    convId: '',
  },

  onLoad() {
    this.addMessage('assistant', '你好！我是你的 AI 决策助手。\n\n📊 说"蓝牙耳机能不能做"→ 分析市场\n💰 说"算利润"→ 自动计算\n✍️ 说"生成 Listing"→ AI 写文案')
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  addMessage(role, content) {
    const msgs = this.data.messages
    msgs.push({ role, content })
    this.setData({ messages: msgs })
  },

  async onSend() {
    const text = this.data.input.trim()
    if (!text || this.data.loading) return

    this.addMessage('user', text)
    this.setData({ input: '', loading: true })

    try {
      const data = await api.agentRun(text)
      if (data.conversation_id) {
        this.setData({ convId: data.conversation_id })
      }
      this.addMessage('assistant', data.summary || '已完成')
    } catch (e) {
      this.addMessage('assistant', '执行失败，请重试')
    }
    this.setData({ loading: false })
  },

  onQuickTap(e) {
    const text = e.currentTarget.dataset.text
    this.setData({ input: text })
  },
})
