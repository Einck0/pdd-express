/**
 * 首页 — 查件
 * 功能：轮播公告、搜索查件、包裹列表（点击复制取件码、长按复制单号）
 */

var app = getApp();

var _debounceTimer = null;

Page({
  data: {
    notices: [],
    noticeIdx: 0,
    keyword: '',
    searchFocus: false,
    packages: [],
    phones: [],
    hasPhones: false,
    loading: true,
    showToast: false,
    toastText: '',
  },

  /* ── 生命周期 ── */

  onLoad: function () {
    this.setData({ notices: app.config.banners || [] });
    this._startNotice();
  },

  onShow: function () {
    var that = this;
    app.onLogin(function () { that._loadData(); });
  },

  onUnload: function () {
    clearInterval(this._noticeTimer);
  },

  onPullDownRefresh: function () {
    var that = this;
    this._loadData().finally(function () {
      wx.stopPullDownRefresh();
    });
  },

  /* ── 公告轮播 ── */

  _startNotice: function () {
    var that = this;
    var interval = app.config.bannerInterval || 4000;
    this._noticeTimer = setInterval(function () {
      if (that.data.notices.length > 1) {
        that.setData({ noticeIdx: (that.data.noticeIdx + 1) % that.data.notices.length });
      }
    }, interval);
  },

  /* ── 数据加载 ── */

  _loadData: function () {
    var that = this;
    return app.api.getPhones().then(function (data) {
      var phones = data.phones || [];
      that.setData({ phones: phones, hasPhones: phones.length > 0 });
      if (phones.length === 0) {
        that.setData({ loading: false, packages: [] });
        return;
      }
      return app.api.getPackages().then(function (d2) {
        that.setData({ packages: d2.packages || [], loading: false });
      });
    }).catch(function () {
      that.setData({ loading: false });
    });
  },

  /* ── 搜索 ── */

  onInput: function (e) {
    var that = this;
    this.setData({ keyword: e.detail.value });
    // 防抖：输入变化时自动搜索
    clearTimeout(_debounceTimer);
    if (e.detail.value.length >= (app.config.searchMinLength || 4)) {
      _debounceTimer = setTimeout(function () { that.onSearch(); }, 300);
    }
  },

  onClear: function () {
    this.setData({ keyword: '' });
    this._loadData();
  },

  onSearch: function () {
    var that = this;
    var kw = this.data.keyword.trim();
    if (kw.length < (app.config.searchMinLength || 4)) {
      this._toast('请输入至少4位的单号或手机号');
      return;
    }

    wx.showLoading({ title: '查询中…' });
    app.api.searchPackages(kw).then(function (data) {
      var list = data.packages || [];
      that.setData({ packages: list });
      if (list.length === 0) {
        that._toast('未查询到包裹');
      }
    }).finally(function () {
      wx.hideLoading();
    });
  },

  onRefresh: function () {
    this.setData({ loading: true });
    this._loadData();
  },

  /* ── 包裹操作 ── */

  onCopyCode: function (e) {
    var code = e.currentTarget.dataset.code;
    if (!code) return;
    wx.setClipboardData({
      data: code,
      success: function () { wx.showToast({ title: '取件码已复制', icon: 'success' }); },
    });
  },

  onCopyWaybill: function (e) {
    var wb = e.currentTarget.dataset.waybill;
    if (!wb) return;
    wx.setClipboardData({
      data: wb,
      success: function () { wx.showToast({ title: '运单号已复制', icon: 'success' }); },
    });
  },

  /* ── 导航 ── */

  onGoBindPhone: function () {
    wx.switchTab({ url: '/pages/bindPhone/bindPhone' });
  },

  /* ── 工具 ── */

  _toast: function (text) {
    this.setData({ showToast: true, toastText: text });
    var that = this;
    setTimeout(function () { that.setData({ showToast: false }); }, 2000);
  },
});
