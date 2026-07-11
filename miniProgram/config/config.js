/**
 * 主配置文件
 * 所有默认配置项在此定义
 * config.user.js 可覆盖任意字段
 */
var config = {
  // API 基础地址（无尾部斜杠）
  apiBaseUrl: 'https://your-domain.com',

  // 轮播公告内容
  bannerTexts: [
    '欢迎使用快递取件助手',
    '请妥善保管取件码',
    '如有问题请联系客服'
  ],

  // 轮播间隔（ms）
  bannerInterval: 3000,

  // wx.login 最大重试次数
  loginMaxRetries: 3,

  // wx.login 重试间隔（ms）
  loginRetryDelay: 1000,

  // 请求超时（ms）
  requestTimeout: 15000
};

// 尝试加载本地覆盖配置
try {
  var localConfig = require('./config.user');
  if (localConfig) {
    Object.keys(localConfig).forEach(function (key) {
      config[key] = localConfig[key];
    });
  }
} catch (e) {
  // config.user.js 不存在或加载失败，忽略
}

module.exports = config;
