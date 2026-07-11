/**
 * App 入口文件
 * 负责全局登录逻辑和全局数据管理
 */
var api = require('./utils/api');
var config = require('./config/config');

App({
  globalData: {
    openid: '',           // 用户 openid
    loginRetries: 0       // 登录重试计数
  },

  onLaunch: function () {
    this.wxLogin();
  },

  /**
   * wx.login 自动登录，失败自动重试
   */
  wxLogin: function () {
    var that = this;
    wx.login({
      success: function (res) {
        if (res.code) {
          api.wxLogin(res.code, function (data) {
            that.globalData.openid = data.openid || data.open_id || '';
            that.globalData.loginRetries = 0;
            // 通知等待登录的页面
            if (that.loginCallback) {
              that.loginCallback(that.globalData.openid);
            }
          }, function () {
            that._retryLogin();
          });
        } else {
          that._retryLogin();
        }
      },
      fail: function () {
        that._retryLogin();
      }
    });
  },

  /**
   * 登录重试逻辑
   */
  _retryLogin: function () {
    var that = this;
    that.globalData.loginRetries++;
    if (that.globalData.loginRetries < config.loginMaxRetries) {
      setTimeout(function () {
        that.wxLogin();
      }, config.loginRetryDelay);
    } else {
      wx.showToast({ title: '登录失败，请稍后重试', icon: 'none', duration: 2500 });
    }
  }
});
