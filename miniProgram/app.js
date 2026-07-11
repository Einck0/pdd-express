// app.js
App({
  globalData: {
    wxid: null,  // 用户wxid，初始为null
  },
  // onLaunch() {
  //   // 启动小程序时尝试登录
  //   this.wxLogin();
  // },

  async wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: async (res) => {
          if (res.code) {
            try {
              const loginRes = await this.request({
                url: '/wxlogin',
                method: 'POST',
                data: { code: res.code },
              });

              if (loginRes.statusCode >= 200 && loginRes.statusCode < 300) {
                this.globalData.wxid = loginRes.data.openid;
                resolve(loginRes.data.openid); // 返回openid
              } else {
                console.error('微信登录失败:', loginRes);
                reject(new Error('微信登录失败'));
              }
            } catch (error) {
              console.error('微信登录请求错误:', error);
              reject(error);
            }
          } else {
            console.error('获取用户登录态失败！' + res.errMsg);
            reject(new Error('获取用户登录态失败'));
          }
        },
        fail: (err) => {
          console.error('wx.login调用失败', err);
          reject(err);
        },
      });
    });
  },

  request({ url, method = 'GET', data = {} }) {
    const baseUrl = this.config.apiBaseUrl;
    const fullUrl = baseUrl + url;

    return new Promise((resolve, reject) => {
      wx.request({
        url: fullUrl,
        method: method,
        data: data,
        header: { 'content-type': 'application/json' },
        success: (res) => {
          resolve(res);
        },
        fail: (err) => {
          console.error('请求失败:', err);
          wx.showToast({
            title: '网络错误',
            icon: 'error',
            duration: 2000,
          });
          reject(err);
        },
      });
    });
  },
  // 简化调用，并添加配置
  config: require('./config.js').default,
});