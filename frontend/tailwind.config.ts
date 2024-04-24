// tailwind.config.ts
import { Config } from 'tailwindcss'

const config: Config = {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],

  plugins: [
    require('daisyui')
  ],
  theme: {
    screens: {
      'ssm': '0px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      'xxl': '1536px',
    }
  }
}

export default config satisfies Config