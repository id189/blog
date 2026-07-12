import { defineConfig } from 'astro/config';

// site / base 可由环境变量覆盖，方便不同托管平台：
//   ASTRO_SITE=https://your-site.netlify.app
//   ASTRO_BASE=/     （自有域名/根路径留空；子路径才需要设置）
export default defineConfig({
  site: process.env.ASTRO_SITE || 'https://example.netlify.app',
  base: process.env.ASTRO_BASE || '',
  markdown: {
    shikiConfig: {
      theme: 'github-light',
      wrap: true,
    },
  },
});
