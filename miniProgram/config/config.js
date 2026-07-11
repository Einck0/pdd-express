// config/config.js - 主配置（会被 config.user.js 覆盖）
const config = {
  apiBaseUrl: 'https://api.example.com/express',
  bannerTexts: [
    '收藏小程序，无需扫码即可查件',
    '取件时务必核对姓名',
    '最多添加5个手机号',
  ],
  bannerInterval: 5000,
  loginMaxRetries: 3,
  loginRetryDelay: 3000,
  searchMinLength: 11,
};

// 尝试加载本地覆盖配置
try {
  const local = require('./config.user.js');
  if (local) {
    Object.assign(config, local);
  }
} catch (e) {
  // 本地配置不存在，使用默认值
}

module.exports = config;
