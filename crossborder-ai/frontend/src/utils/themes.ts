// VeyaShip 完整主题配置（涵盖所有 CSS 变量）

export interface Theme {
  name: string
  label: string
  colors: {
    '--background': string
    '--foreground': string
    '--card': string
    '--card-foreground': string
    '--primary': string
    '--primary-foreground': string
    '--secondary': string
    '--secondary-foreground': string
    '--muted': string
    '--muted-foreground': string
    '--accent': string
    '--accent-foreground': string
    '--border': string
    '--input': string
    '--ring': string
  }
}

export const themes: Theme[] = [
  {
    name: 'light',
    label: '明亮',
    colors: {
      '--background': '210 40% 98%',        // #F8FAFC 浅灰蓝
      '--foreground': '226 60% 33%',        // #1E3A8A 深蓝文字
      '--card': '0 0% 100%',
      '--card-foreground': '226 60% 33%',
      '--primary': '226 71% 40%',           // #1E40AF 主蓝
      '--primary-foreground': '0 0% 100%',
      '--secondary': '215 42% 94%',
      '--secondary-foreground': '226 60% 30%',
      '--muted': '215 42% 94%',
      '--muted-foreground': '215 20% 50%',
      '--accent': '214 90% 93%',            // #DBEAFE
      '--accent-foreground': '226 71% 40%',
      '--border': '214 50% 92%',
      '--input': '214 50% 92%',
      '--ring': '226 71% 40%',
    },
  },
  {
    name: 'dark',
    label: '暗黑',
    colors: {
      '--background': '226 50% 7%',         // 深海军蓝
      '--foreground': '214 30% 93%',
      '--card': '226 45% 9%',
      '--card-foreground': '214 30% 93%',
      '--primary': '217 91% 60%',           // #3B82F6 亮蓝
      '--primary-foreground': '226 50% 8%',
      '--secondary': '226 30% 16%',
      '--secondary-foreground': '214 25% 85%',
      '--muted': '226 30% 15%',
      '--muted-foreground': '214 18% 60%',
      '--accent': '226 30% 20%',
      '--accent-foreground': '214 25% 88%',
      '--border': '226 25% 16%',
      '--input': '226 25% 16%',
      '--ring': '217 91% 60%',
    },
  },
  {
    name: 'ocean',
    label: '深海',
    colors: {
      '--background': '195 40% 96%',
      '--foreground': '200 30% 18%',
      '--card': '0 0% 100%',
      '--card-foreground': '200 30% 18%',
      '--primary': '195 85% 40%',
      '--primary-foreground': '0 0% 100%',
      '--secondary': '195 30% 90%',
      '--secondary-foreground': '195 50% 25%',
      '--muted': '195 20% 92%',
      '--muted-foreground': '195 15% 50%',
      '--accent': '195 40% 88%',
      '--accent-foreground': '195 50% 25%',
      '--border': '195 25% 85%',
      '--input': '195 25% 85%',
      '--ring': '195 85% 40%',
    },
  },
  {
    name: 'warm',
    label: '暖阳',
    colors: {
      '--background': '30 30% 97%',
      '--foreground': '20 30% 20%',
      '--card': '0 0% 100%',
      '--card-foreground': '20 30% 20%',
      '--primary': '20 85% 50%',
      '--primary-foreground': '0 0% 100%',
      '--secondary': '20 30% 92%',
      '--secondary-foreground': '20 50% 30%',
      '--muted': '20 20% 94%',
      '--muted-foreground': '20 15% 50%',
      '--accent': '20 30% 90%',
      '--accent-foreground': '20 50% 25%',
      '--border': '20 25% 88%',
      '--input': '20 25% 88%',
      '--ring': '20 85% 50%',
    },
  },
  {
    name: 'forest',
    label: '森林',
    colors: {
      '--background': '150 30% 97%',
      '--foreground': '150 30% 18%',
      '--card': '0 0% 100%',
      '--card-foreground': '150 30% 18%',
      '--primary': '150 60% 35%',
      '--primary-foreground': '0 0% 100%',
      '--secondary': '150 30% 92%',
      '--secondary-foreground': '150 40% 25%',
      '--muted': '150 20% 94%',
      '--muted-foreground': '150 15% 48%',
      '--accent': '150 30% 90%',
      '--accent-foreground': '150 40% 22%',
      '--border': '150 25% 88%',
      '--input': '150 25% 88%',
      '--ring': '150 60% 35%',
    },
  },
]

export function getTheme(): Theme {
  if (typeof window === 'undefined') return themes[0]
  const saved = localStorage.getItem('veya-theme')
  return themes.find((t) => t.name === saved) || themes[0]
}

export function applyTheme(theme: Theme) {
  if (typeof window === 'undefined') return
  localStorage.setItem('veya-theme', theme.name)
  const root = document.documentElement

  // 暗黑模式：给 html 加 class="dark"
  if (theme.name === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }

  // 应用所有 CSS 变量
  Object.entries(theme.colors).forEach(([key, val]) => {
    root.style.setProperty(key, val)
  })
}

export function initTheme() {
  const theme = getTheme()
  applyTheme(theme)
  return theme
}
