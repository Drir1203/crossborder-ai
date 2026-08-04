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
    // ── v2 高级感 token ──
    '--glass-bg': string
    '--glass-bg-strong': string
    '--glass-border': string
    '--glass-highlight': string
    '--gradient-from': string
    '--gradient-to': string
    '--gradient-foreground': string
    '--glow-primary': string
    '--card-shadow': string
    '--aurora-a': string
    '--aurora-b': string
  }
}

export const themes: Theme[] = [
  {
    name: 'dark',
    label: '暗黑',
    colors: {
      '--background': '30 15% 4%',          // 暖黑 #0C0A09
      '--foreground': '40 10% 95%',         // 暖白文字
      '--card': '30 10% 7%',
      '--card-foreground': '40 10% 95%',
      '--primary': '38 92% 50%',            // 琥珀金 #F59E0B
      '--primary-foreground': '30 15% 4%',  // 琥珀上深字
      '--secondary': '30 10% 14%',
      '--secondary-foreground': '40 10% 88%',
      '--muted': '30 10% 12%',
      '--muted-foreground': '30 10% 55%',
      '--accent': '38 40% 16%',
      '--accent-foreground': '40 10% 90%',
      '--border': '30 10% 15%',
      '--input': '30 10% 15%',
      '--ring': '38 92% 50%',
      '--glass-bg': 'rgba(255, 255, 255, 0.045)',
      '--glass-bg-strong': 'rgba(255, 255, 255, 0.07)',
      '--glass-border': 'rgba(255, 255, 255, 0.10)',
      '--glass-highlight': 'rgba(255, 255, 255, 0.14)',
      '--gradient-from': '#fbbf24',
      '--gradient-to': '#d97706',
      '--gradient-foreground': '#1a1204',
      '--glow-primary': 'rgba(245, 158, 11, 0.75)',
      '--card-shadow': '0 24px 60px -30px rgba(0, 0, 0, 0.85)',
      '--aurora-a': 'rgba(217, 119, 6, 0.35)',
      '--aurora-b': 'rgba(245, 158, 11, 0.22)',
    },
  },
  {
    name: 'light',
    label: '明亮',
    colors: {
      '--background': '40 10% 98%',
      '--foreground': '30 14% 10%',
      '--card': '0 0% 100%',
      '--card-foreground': '30 14% 10%',
      '--primary': '32 95% 44%',            // 琥珀 #D97706
      '--primary-foreground': '0 0% 100%',
      '--secondary': '40 20% 94%',
      '--secondary-foreground': '30 14% 20%',
      '--muted': '40 20% 94%',
      '--muted-foreground': '30 10% 50%',
      '--accent': '38 60% 92%',
      '--accent-foreground': '32 60% 35%',
      '--border': '40 20% 90%',
      '--input': '40 20% 90%',
      '--ring': '32 95% 44%',
      '--glass-bg': 'rgba(255, 255, 255, 0.66)',
      '--glass-bg-strong': 'rgba(255, 255, 255, 0.85)',
      '--glass-border': 'rgba(255, 255, 255, 0.6)',
      '--glass-highlight': 'rgba(255, 255, 255, 0.9)',
      '--gradient-from': '#fbbf24',
      '--gradient-to': '#d97706',
      '--gradient-foreground': '#1a1204',
      '--glow-primary': 'rgba(245, 158, 11, 0.45)',
      '--card-shadow': '0 24px 60px -30px rgba(0, 0, 0, 0.35)',
      '--aurora-a': 'rgba(217, 119, 6, 0.25)',
      '--aurora-b': 'rgba(245, 158, 11, 0.18)',
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
      '--glass-bg': 'rgba(255, 255, 255, 0.6)',
      '--glass-bg-strong': 'rgba(255, 255, 255, 0.8)',
      '--glass-border': 'rgba(255, 255, 255, 0.5)',
      '--glass-highlight': 'rgba(255, 255, 255, 0.85)',
      '--gradient-from': '#38bdf8',
      '--gradient-to': '#0284c7',
      '--gradient-foreground': '#ffffff',
      '--glow-primary': 'rgba(2, 132, 199, 0.5)',
      '--card-shadow': '0 24px 60px -30px rgba(0, 0, 0, 0.35)',
      '--aurora-a': 'rgba(2, 132, 199, 0.30)',
      '--aurora-b': 'rgba(56, 189, 248, 0.20)',
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
      '--glass-bg': 'rgba(255, 255, 255, 0.6)',
      '--glass-bg-strong': 'rgba(255, 255, 255, 0.8)',
      '--glass-border': 'rgba(255, 255, 255, 0.5)',
      '--glass-highlight': 'rgba(255, 255, 255, 0.85)',
      '--gradient-from': '#fb923c',
      '--gradient-to': '#ea580c',
      '--gradient-foreground': '#ffffff',
      '--glow-primary': 'rgba(234, 88, 12, 0.5)',
      '--card-shadow': '0 24px 60px -30px rgba(0, 0, 0, 0.35)',
      '--aurora-a': 'rgba(234, 88, 12, 0.30)',
      '--aurora-b': 'rgba(251, 146, 60, 0.20)',
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
      '--glass-bg': 'rgba(255, 255, 255, 0.6)',
      '--glass-bg-strong': 'rgba(255, 255, 255, 0.8)',
      '--glass-border': 'rgba(255, 255, 255, 0.5)',
      '--glass-highlight': 'rgba(255, 255, 255, 0.85)',
      '--gradient-from': '#34d399',
      '--gradient-to': '#059669',
      '--gradient-foreground': '#ffffff',
      '--glow-primary': 'rgba(5, 150, 105, 0.5)',
      '--card-shadow': '0 24px 60px -30px rgba(0, 0, 0, 0.35)',
      '--aurora-a': 'rgba(5, 150, 105, 0.30)',
      '--aurora-b': 'rgba(52, 211, 153, 0.20)',
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
