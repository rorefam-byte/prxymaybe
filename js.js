const { app, BrowserWindow } = require('electron');
const path = require('path');
const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

// ==========================================
// 1. START THE BUILT-IN PROXY SERVER
// ==========================================
const proxyApp = express();
const PROXY_PORT = 4000;

proxyApp.use(cors());

// Intercepts request to /proxy and redirects to whatever target URL is passed
proxyApp.use('/proxy', createProxyMiddleware({
  router: (req) => {
    // Dynamically reads the target destination from an added custom header
    return req.headers['x-target-url'] || 'https://duckduckgo.com';
  },
  changeOrigin: true,
  onProxyReq: (proxyReq, req, res) => {
    // Spoof a clean user agent header to prevent target websites from blocking you
    proxyReq.setHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
  },
  onProxyRes: (proxyRes, req, res) => {
    // Force allow CORS headers so the browser can read the response smoothly
    proxyRes.headers['Access-Control-Allow-Origin'] = '*';
  }
}));

proxyApp.listen(PROXY_PORT, () => {
  console.log(`Internal Proxy Server actively running on port ${PROXY_PORT}`);
});


// ==========================================
// 2. LAUNCH THE ELECTRON BROWSER WINDOW
// ==========================================
function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webviewTag: true // Vital for rendering websites inside the application UI
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
