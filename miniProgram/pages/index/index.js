var app = getApp();

Page({
  data: {
    banners: [],
    bannerIdx: 0,
    keyword: '',
    packages: [],
    phones: [],
    loading: true,
    refreshing: false,
    hasPhones: false,
  },

  /* ── 生命周期 ── */

  onLoad: function () {
    this.setData({ banners: app.config.banners });
    this.startBannerTimer();
  },

  onShow: function () {
    var that = this;
    app.onLogin(function () { that.loadData(); });
  },

  onPullDownRefresh: function () {
    this.setData({ refreshing: true });
    this.loadData().finally(function () {
      wx.stopPullDownRefresh();
    });
  },

  /* ── 轮播 ── */

  startBannerTimer: function () {
    var that = this;
    this._bannerTimer = setInterval(function () {
      that.setData({
        bannerIdx: (that.data.bannerIdx + 1) % that.data.banners.length,
      });
    }, app.config.bannerInterval);
  },

  /* ── 数据加载 ── */

  loadData: function () {
    var that = this;
    var wxid = app.globalData.wxid;

    if (!wxid) {
      that.setData({ loading: false });
      return Promise.resolve();
    }

    return app.api.getPhones().then(function (res) {
      var phones = res.phones || [];
      that.setData({ phones: phones, hasPhones: phones.length > 0 });

      if (phones.length === 0) {
        that.setData({ loading: false, packages: [] });
        return;
      }

      return app.api.getPackages().then(function (res2) {
        that.setData({
          packages: res2.packages || [],
          loading: false,
          refreshing: false,
        });
      });
    }).catch(function () {
      that.setData({ loading: false, refreshing: false });
    });
  },

  /* ── 搜索 ── */

  onKeywordInput: function (e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearch: function () {
    var that = this;
    var wxid = app.globalData.wxid;
    var keyword = this.data.keyword.trim();

    if (!wxid) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    if (keyword.length < app.config.searchMinLength) {
      wx.showToast({ title: '请输入正确的手机号或单号', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '查询中...' });
    app.api.searchPackages(keyword).then(function (res) {
      that.setData({ packages: res.packages || [] });
      if ((res.packages || []).length === 0) {
        wx.showToast({ title: '未查到包裹', icon: 'none' });
      }
    }).finally(function () {
      wx.hideLoading();
    });
  },

  onRefresh: function () {
    this.setData({ loading: true });
    this.loadData();
  },

  /* ── 导航 ── */

  onGoToBindPhone: function () {
    wx.switchTab({ url: '/pages/bindPhone/bindPhone' });
  },
});
