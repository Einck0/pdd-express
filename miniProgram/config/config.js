/**
 * 默认配置
 * 用户本地配置请创建 config.user.js，会自动合并覆盖
 */

var defaults = {
  // 后端 API 地址（部署时必须在 config.user.js 中覆盖）
  apiBaseUrl: 'https://your-server.com/express',

  // 轮播公告
  banners: [
    '收藏小程序，无需扫码即可查件',
    '取件时务必核对姓名',
    '最多添加 5 个手机号',
  ],
  bannerInterval: 4000,

  // 登录重试
  loginRetries: 3,
  loginRetryDelay: 2000,

  // 搜索
  searchMinLength: 4,

  // 请求超时
  timeout: 15000,
};

// 合并用户本地配置
try {
  var user = require('./config.user');
  if (user && typeof user === 'object') {
    Object.keys(user).forEach(function (k) {
      defaults[k] = user[k];
    });
  }
} catch (e) {}

module.exports = defaults;
