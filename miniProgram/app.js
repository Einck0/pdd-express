/**
 * 应用入口
 * 微信登录 + 全局状态管理
 */

var config = require('./config/config');
var api = require('./utils/api');

App({
  globalData: {
    wxid: null,
    loginCallbacks: [],
  },

  config: config,
  api: api,

  onLaunch: function () {
    this.login();
  },

  /**
   * 等待登录完成
   * @param {Function} cb - 回调，参数为 wxid
   */
  onLogin: function (cb) {
    if (this.globalData.wxid) {
      cb(this.globalData.wxid);
    } else {
      this.globalData.loginCallbacks.push(cb);
    }
  },

  /**
   * 微信登录
   * 成功后存储 token，触发等待回调
   */
  login: function (attempt) {
    var that = this;
    attempt = attempt || 0;

    wx.login({
      success: function (res) {
        if (!res.code) {
          that._retry(attempt, '获取 code 失败');
          return;
        }
        api.wxLogin(res.code).then(function (data) {
          if (data && data.token) {
            that.globalData.wxid = data.token;
            try { wx.setStorageSync('wxid', data.token); } catch (e) {}
            that.globalData.loginCallbacks.forEach(function (cb) { cb(data.token); });
            that.globalData.loginCallbacks = [];
          } else {
            that._retry(attempt, 'token 为空');
          }
        }).catch(function () {
          that._retry(attempt, '登录请求失败');
        });
      },
      fail: function () {
        that._retry(attempt, 'wx.login 调用失败');
      },
    });
  },

  _retry: function (attempt, reason) {
    var that = this;
    console.warn('[login]', reason, 'attempt=' + attempt);
    if (attempt < that.config.loginRetries) {
      setTimeout(function () { that.login(attempt + 1); }, that.config.loginRetryDelay);
    } else {
      wx.showToast({ title: '登录失败，请稍后重试', icon: 'none', duration: 3000 });
    }
  },
});
