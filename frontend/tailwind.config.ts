// tailwind.config.ts
import { Config } from 'tailwindcss'

const defaultTheme = require('tailwindcss/defaultTheme')

const config: Config = {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],

  plugins: [
    require('daisyui')
  ],
  theme: {
    // add custom screens:
    // https://tailwindcss.com/docs/screens
    screens: {
      'smm': '0px',
      'xs': '470px',
      ...defaultTheme.screens,
    }
  }
}

export default config satisfies Config