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
    name: 'dark',
    label: '暗黑',
    colors: {
      '--background': '240 25% 5%',         // 深色底 #0a0a0f
      '--foreground': '220 7% 93%',         // 近白文字
      '--card': '240 20% 7%',
      '--card-foreground': '220 7% 93%',
      '--primary': '234 56% 60%',           // 靛蓝 #5E6AD2
      '--primary-foreground': '0 0% 100%',
      '--secondary': '234 25% 15%',
      '--secondary-foreground': '220 7% 88%',
      '--muted': '240 20% 14%',
      '--muted-foreground': '220 12% 55%',
      '--accent': '234 30% 18%',
      '--accent-foreground': '220 7% 90%',
      '--border': '240 15% 18%',
      '--input': '240 15% 18%',
      '--ring': '234 56% 60%',
    },
  },
  {
    name: 'light',
    label: '明亮',
    colors: {
      '--background': '210 40% 98%',
      '--foreground': '234 50% 28%',
      '--card': '0 0% 100%',
      '--card-foreground': '234 50% 28%',
      '--primary': '234 60% 50%',           // 靛蓝（与暗色同一家族）
      '--primary-foreground': '0 0% 100%',
      '--secondary': '234 30% 94%',
      '--secondary-foreground': '234 50% 30%',
      '--muted': '234 25% 94%',
      '--muted-foreground': '234 15% 50%',
      '--accent': '234 45% 93%',
      '--accent-foreground': '234 60% 45%',
      '--border': '234 25% 91%',
      '--input': '234 25% 91%',
      '--ring': '234 60% 50%',
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
