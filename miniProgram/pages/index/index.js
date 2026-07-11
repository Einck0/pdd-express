/**
 * 首页逻辑
 * 功能：轮播公告、搜索包裹、包裹列表、下拉刷新
 */
var api = require('../../utils/api');
var config = require('../../config/config');

Page({
  data: {
    // 轮播公告
    bannerTexts: config.bannerTexts,
    bannerInterval: config.bannerInterval,

    // 搜索
    keyword: '',

    // 包裹列表
    packages: [],

    // 状态控制
    loading: true,
    error: false,
    errorMsg: '',
    wxid: ''
  },

  onLoad: function () {
    var that = this;
    var app = getApp();
    // 等待登录完成后加载数据
    if (app.globalData.openid) {
      that.setData({ wxid: app.globalData.openid });
      that.loadPackages();
    } else {
      app.loginCallback = function (openid) {
        that.setData({ wxid: openid });
        that.loadPackages();
      };
    }
  },

  onShow: function () {
    // 每次显示页面时刷新（从 bindPhone 页返回时数据可能变了）
    if (this.data.wxid && !this.data.loading) {
      this.loadPackages();
    }
  },

  onPullDownRefresh: function () {
    this.loadPackages(function () {
      wx.stopPullDownRefresh();
    });
  },

  /**
   * 加载包裹列表
   */
  loadPackages: function (cb) {
    var that = this;
    if (!that.data.wxid) {
      that.setData({ loading: false, error: true, errorMsg: '未登录' });
      if (cb) cb();
      return;
    }
    that.setData({ loading: true, error: false });

    api.getPackages(that.data.wxid, function (data) {
      that.setData({
        packages: data.packages || [],
        loading: false,
        error: false
      });
      if (cb) cb();
    }, function () {
      that.setData({
        loading: false,
        error: true,
        errorMsg: '加载失败，下拉刷新重试'
      });
      if (cb) cb();
    });
  },

  /**
   * 搜索输入
   */
  onKeywordInput: function (e) {
    this.setData({ keyword: e.detail.value });
  },

  /**
   * 搜索包裹
   */
  onSearch: function () {
    var that = this;
    var keyword = that.data.keyword.trim();
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' });
      return;
    }
    if (!that.data.wxid) {
      wx.showToast({ title: '未登录', icon: 'none' });
      return;
    }

    that.setData({ loading: true, error: false });

    api.searchPackages(that.data.wxid, keyword, function (data) {
      that.setData({
        packages: data.packages || [],
        loading: false
      });
    }, function () {
      // 主接口失败，尝试兜底接口
      api.searchPackagesFallback(that.data.wxid, keyword, function (data) {
        that.setData({
          packages: data.packages || [],
          loading: false
        });
      }, function () {
        that.setData({
          loading: false,
          error: true,
          errorMsg: '搜索失败，请重试'
        });
      });
    });
  },

  /**
   * 刷新按钮
   */
  onRefresh: function () {
    this.setData({ keyword: '' });
    this.loadPackages();
  },

  /**
   * 跳转到手机号管理
   */
  goToBindPhone: function () {
    wx.switchTab({ url: '/pages/bindPhone/bindPhone' });
  }
});
