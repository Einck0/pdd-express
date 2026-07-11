// pages/index/index.js
const app = getApp();
const config = require('../../config/config');

Page({
  data: {
    bannerIndex: 0,
    bannerTexts: config.bannerTexts,
    searchInput: '',
    packages: [],
    phoneNumbers: [],
    loading: true,
    loggedIn: false,
  },

  _bannerTimer: null,

  onLoad() {
    this._startBanner();
  },

  onShow() {
    this._initData();
  },

  onUnload() {
    this._stopBanner();
  },

  onPullDownRefresh() {
    this._initData().finally(() => wx.stopPullDownRefresh());
  },

  // ---- Banner ----
  _startBanner() {
    this._bannerTimer = setInterval(() => {
      this.setData({
        bannerIndex: (this.data.bannerIndex + 1) % this.data.bannerTexts.length,
      });
    }, config.bannerInterval);
  },

  _stopBanner() {
    if (this._bannerTimer) {
      clearInterval(this._bannerTimer);
      this._bannerTimer = null;
    }
  },

  // ---- 初始化数据 ----
  async _initData() {
    this.setData({ loading: true });

    try {
      const openid = await app.ensureLogin();
      this.setData({ loggedIn: true });
      await this._loadPhones(openid);
    } catch (e) {
      console.error('初始化失败:', e);
    } finally {
      this.setData({ loading: false });
    }
  },

  async _loadPhones(wxid) {
    try {
      const res = await app.api.getPhones(wxid);
      const phones = res.phones || [];
      this.setData({ phoneNumbers: phones });

      if (phones.length === 0) {
        wx.switchTab({ url: '/pages/bindPhone/bindPhone' });
      } else {
        await this._loadPackages(wxid);
      }
    } catch (e) {
      // api 已自动 toast
    }
  },

  async _loadPackages(wxid) {
    try {
      const res = await app.api.getPackages(wxid || app.globalData.wxid);
      this.setData({ packages: res.packages || [] });
    } catch (e) {
      // api 已自动 toast
    }
  },

  // ---- 事件 ----
  onSearchInput(e) {
    this.setData({ searchInput: e.detail.value });
  },

  async onSearch() {
    const keyword = this.data.searchInput.trim();
    if (!keyword || keyword.length < config.searchMinLength) {
      wx.showToast({ title: '请输入正确的手机号或单号', icon: 'none' });
      return;
    }
    if (!app.globalData.wxid) return;

    try {
      const res = await app.api.searchPackage(app.globalData.wxid, keyword);
      this.setData({ packages: res.packages || [] });
      if ((res.packages || []).length === 0) {
        wx.showToast({ title: '未查到相关包裹', icon: 'none' });
      }
    } catch (e) {
      // api 已自动 toast
    }
  },

  onRefresh() {
    this._initData();
  },

  onGoToBind() {
    wx.switchTab({ url: '/pages/bindPhone/bindPhone' });
  },
});
