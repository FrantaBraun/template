/**
 * Part of the With FBraun project template.
 * Author: František Braun <frantisek.braun95@gmail.com>
 * Freely available as a template for building custom applications.
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  // @tailwindcss/vite replaces the old PostCSS pipeline (no tailwind.config.js
  // or postcss.config.js needed) - it scans source files for class names and
  // injects the generated CSS directly, driven entirely by the
  // `@import "tailwindcss"` in src/index.css.
  plugins: [react(), tailwindcss()],
})
