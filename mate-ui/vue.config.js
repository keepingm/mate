const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '' // 将 /api 前缀去掉，直接转发到后端
        },
        // 关键：禁用代理缓冲，确保流式传输
        buffer: false, // 禁用http-proxy-middleware的缓冲
        onProxyRes: function(proxyRes, req, res) {
          // 移除可能导致缓冲的响应头
          delete proxyRes.headers['content-length']
          // 设置禁用缓冲的头
          proxyRes.headers['X-Accel-Buffering'] = 'no'
          proxyRes.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
          proxyRes.headers['Pragma'] = 'no-cache'
          proxyRes.headers['Expires'] = '0'
          proxyRes.headers['Connection'] = 'keep-alive'
          // 确保使用chunked传输
          proxyRes.headers['Transfer-Encoding'] = 'chunked'
        },
        onProxyReq: function(proxyReq, req, res) {
          // 请求时也设置禁用缓冲的头
          proxyReq.setHeader('Cache-Control', 'no-cache')
          proxyReq.setHeader('Connection', 'keep-alive')
        }
      }
    }
  }
})
