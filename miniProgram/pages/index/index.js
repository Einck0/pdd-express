// pages/index/index.js
const app = getApp();

Page({
  data: {
    bannerText: '',
    searchInput: '',
    packages: [],
    phoneNumbers: [],
    showBindPhone: false,
  },

  onLoad() {
    this.initBanner();
  },

  onShow() {
    this.checkLoginAndLoadData();
  },

  initBanner() {
    let index = 0;
    this.setData({ bannerText: app.config.bannerTexts[index] });
    setInterval(() => {
      index = (index + 1) % app.config.bannerTexts.length;
      this.setData({ bannerText: app.config.bannerTexts[index] });
    }, app.config.bannerInterval);
  },

  async checkLoginAndLoadData() {
    const maxRetries = 3; // 设置最大重试次数
    let retryCount = 0;
  
    while (!app.globalData.wxid && retryCount < maxRetries) {
      try {
        await app.wxLogin();
        if (!app.globalData.wxid) {
          retryCount++;
          console.log(`登录失败，正在进行第 ${retryCount} 次重试...`);
          await new Promise(resolve => setTimeout(resolve, 5000)); // 等待 5 秒
        }
      } catch (error) {
        retryCount++;
        console.error('登录失败:', error);
        console.log(`登录失败，正在进行第 ${retryCount} 次重试...`);
        await new Promise(resolve => setTimeout(resolve, 5000)); // 等待 5 秒
      }
    }
  
    if (!app.globalData.wxid) {
      wx.showToast({
        title: '多次登录失败，请稍后再试',
        icon: 'error',
        duration: 2000
      });
      return; // 阻止继续执行，避免后续操作失败。
    }
  
    this.loadPhoneNumbers(); // loadPhoneNumbers 独立调用
  },

  async loadPhoneNumbers() {
    if (!app.globalData.wxid) return; // 如果wxid为空，则不执行

    try {
      const phonesRes = await app.request({
        url: `/phones/${app.globalData.wxid}`,
        method: 'GET',
      });

      if (phonesRes.statusCode >= 200 && phonesRes.statusCode < 300) {
        this.setData({ phoneNumbers: phonesRes.data.phones || [] });
        if (this.data.phoneNumbers.length === 0) {
          // 如果未绑定手机号，则跳转到绑定手机号页面
          this.navigateToBindPhone();
        } else {
            this.loadPackages();
        }
      } else {
        this.handleRequestError(phonesRes, '获取手机号列表失败');
      }

    } catch (error) {
        console.error('获取手机号列表失败:', error);
        //  添加通用的错误处理，比如显示一个错误提示
        wx.showToast({
          title: '获取手机号列表失败',
          icon: 'error',
          duration: 2000, //  或者其他合适的持续时间
        });
    }
  },

  async loadPackages() {
     if (!app.globalData.wxid) return; // 如果wxid为空，则不执行
      try {
        const packagesRes = await app.request({
          url: `/package/${app.globalData.wxid}`,
          method: 'GET',
        });
        if (packagesRes.statusCode >= 200 && packagesRes.statusCode < 300) {
            if (packagesRes.data.packages =="[]"){
              wx.showToast({ // 添加成功提示
                title: '未查到包裹',
                icon: 'success',
                duration: 1500
            });
            }
             this.setData({ packages: packagesRes.data.packages || [] });
             wx.showToast({ // 添加成功提示
                title: '刷新成功',
                icon: 'success',
                duration: 1500
            });
         } else {
            this.handleRequestError(packagesRes, '获取包裹信息失败');

         }
      } catch (error) {
          console.error('获取包裹信息失败:', error);
          wx.showToast({
              title: '获取包裹信息失败',
              icon: 'error',
              duration: 2000,
          });
      }
  },

  async searchPackages() {
    const keyword = this.data.searchInput;
    if (!keyword || keyword.length < 11) {
      wx.showToast({ title: '请输入正确的手机号或单号', icon: 'none' });
      return;
    }
    if (!app.globalData.wxid) return;

    try {
      const searchRes = await app.request({
        url: `/package/${app.globalData.wxid}`,
        method: 'POST',
        data: { keyword: keyword },
      });

      if (searchRes.statusCode >= 200 && searchRes.statusCode < 300) {
        this.setData({ packages: searchRes.data.packages || [] });
      } else {
          this.handleRequestError(searchRes, '查询包裹失败');
      }
    } catch (error) {
        console.error('查询包裹失败:', error);
         wx.showToast({
              title: '查询包裹失败',
              icon: 'error',
              duration: 2000,
          });
    }
  },

  refreshPackages() {
      this.loadPackages();
  },

  navigateToBindPhone() {
    wx.switchTab({
      url: '/pages/bindPhone/bindPhone',
    });
  },

  onInputChange(e) {
    this.setData({ searchInput: e.detail.value });
  },

  handleRequestError(res, message) {
      console.error(message, res);
      wx.showToast({
          title: message + ":" + (res.data && res.data.message ? res.data.message : '未知错误'),
          icon: 'error',
          duration: 2000,
      });
  },

});