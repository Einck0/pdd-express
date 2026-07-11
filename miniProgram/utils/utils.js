// app.js
App({
  globalData: {
    wxid: null, // 用户wxid，全局变量
    apiBaseUrl: require('./utils/config').apiBaseUrl
  },
  onLaunch: function () {
    // 启动时，尝试从缓存中获取wxid
    const wxid = wx.getStorageSync('wxid');
    if (wxid) {
      this.globalData.wxid = wxid;
    } else {
      // 如果没有wxid，则进行微信登录
      this.wxLogin();
    }
  },

  wxLogin: function () {
    // 微信登录，获取openid
    wx.login({
      success: res => {
        if (res.code) {
          // 发起网络请求，获取openid
          wx.request({
            url: `${this.globalData.apiBaseUrl}/wxlogin`,
            method: 'POST',
            data: {
              code: res.code
            },
            success: res => {
              if (res.statusCode >= 200 && res.statusCode < 300) {
                const wxid = res.data.openid;
                this.globalData.wxid = wxid;
                wx.setStorageSync('wxid', wxid); // 将wxid存储到本地缓存
              } else {
                console.error('微信登录失败:', res);
                wx.showToast({
                  title: '登录失败',
                  icon: 'error'
                });

              }
            },
            fail: err => {
              console.error('微信登录请求失败:', err);
              wx.showToast({
                title: '网络错误',
                icon: 'error'
              });
            }
          });
        } else {
          console.error('登录失败！' + res.errMsg);
          wx.showToast({
            title: '登录失败',
            icon: 'error'
          });
        }
      },
      fail: err => {
        console.error('wx.login调用失败', err);
        wx.showToast({
          title: '登录失败',
          icon: 'error'
        });
      }
    });
  },
})