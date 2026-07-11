var config = require('./config/config');
var api = require('./utils/api');

App({
  globalData: {
    wxid: null,
    loginCallbacks: [],
  },

  config: config,
  api: api,

  onLogin: function (cb) {
    if (this.globalData.wxid) {
      cb(this.globalData.wxid);
    } else {
      this.globalData.loginCallbacks.push(cb);
    }
  },

  onLaunch: function () {
    this.login();
  },

  /**
   * 微信登录，获取 openid
   * 自动重试，成功后存入 globalData 和 storage
   */
  login: function (attempt) {
    var that = this;
    attempt = attempt || 0;

    wx.login({
      success: function (res) {
        if (!res.code) {
          that.retryLogin(attempt, '获取 code 失败');
          return;
        }
        api.wxLogin(res.code).then(function (data) {
          if (data && data.token) {
            that.globalData.wxid = data.token;
            try { wx.setStorageSync('wxid', data.token); } catch (e) {}
            that.globalData.loginCallbacks.forEach(function (cb) { cb(data.token); });
            that.globalData.loginCallbacks = [];
          } else {
            that.retryLogin(attempt, 'openid 为空');
          }
        }).catch(function () {
          that.retryLogin(attempt, '登录请求失败');
        });
      },
      fail: function () {
        that.retryLogin(attempt, 'wx.login 调用失败');
      },
    });
  },

  retryLogin: function (attempt, reason) {
    var that = this;
    console.warn('[login]', reason, 'attempt=' + attempt);
    if (attempt < that.config.loginRetries) {
      setTimeout(function () {
        that.login(attempt + 1);
      }, that.config.loginRetryDelay);
    } else {
      wx.showToast({ title: '登录失败，请稍后重试', icon: 'none' });
    }
  },
});
