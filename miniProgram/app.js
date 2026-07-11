// app.js
const config = require('./config/config');
const api = require('./utils/api');

App({
  globalData: {
    wxid: null,
  },

  config,
  api,

  onLaunch() {
    this.ensureLogin();
  },

  /**
   * 确保已登录，带重试
   * @param {number} retries - 已重试次数（内部用）
   * @returns {Promise<string>} openid
   */
  ensureLogin(retries = 0) {
    if (this.globalData.wxid) {
      return Promise.resolve(this.globalData.wxid);
    }

    return new Promise((resolve, reject) => {
      wx.login({
        success: (loginRes) => {
          if (!loginRes.code) {
            this._retryOrReject(retries, '获取登录凭证失败', resolve, reject);
            return;
          }

          api
            .wxLogin(loginRes.code)
            .then((data) => {
              if (data && data.openid) {
                this.globalData.wxid = data.openid;
                resolve(data.openid);
              } else {
                this._retryOrReject(retries, '登录返回数据异常', resolve, reject);
              }
            })
            .catch((err) => {
              this._retryOrReject(retries, err.message || '登录请求失败', resolve, reject);
            });
        },
        fail: () => {
          this._retryOrReject(retries, 'wx.login 调用失败', resolve, reject);
        },
      });
    });
  },

  _retryOrReject(retries, msg, resolve, reject) {
    if (retries < config.loginMaxRetries) {
      console.warn(`登录失败: ${msg}，第${retries + 1}次重试...`);
      setTimeout(() => {
        this.ensureLogin(retries + 1).then(resolve).catch(reject);
      }, config.loginRetryDelay);
    } else {
      console.error('多次登录失败:', msg);
      wx.showToast({ title: '登录失败，请稍后重试', icon: 'none', duration: 2500 });
      reject(new Error(msg));
    }
  },
});
