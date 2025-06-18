import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/',  // 设置基础路径
  build: {
    outDir: 'server/static',  // 构建输出到server/static目录
    emptyOutDir: true,        // 构建前清空输出目录
    assetsDir: 'assets'       // 静态资源子目录
  },
  server: {
    host: '0.0.0.0',  // 监听所有地址
    port: 5173,       // 默认端口
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3001',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('代理错误:', err.message);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('代理请求:', req.method, req.url);
          });
        }
      }
    }
  }
})
