/**
 * 手机号管理页逻辑
 * 功能：添加/删除手机号、协议同意、列表展示
 */
var api = require('../../utils/api');

Page({
  data: {
    // 输入
    phoneInput: '',
    agreeChecked: false,

    // 手机号列表
    phones: [],

    // 状态
    loading: true,
    adding: false,
    wxid: '',

    // 协议展开
    showAgreement: false,
    showPrivacy: false
  },

  onLoad: function () {
    var that = this;
    var app = getApp();
    if (app.globalData.openid) {
      that.setData({ wxid: app.globalData.openid });
      that.loadPhones();
    } else {
      app.loginCallback = function (openid) {
        that.setData({ wxid: openid });
        that.loadPhones();
      };
    }
  },

  onShow: function () {
    if (this.data.wxid && !this.data.loading) {
      this.loadPhones();
    }
  },

  /**
   * 加载手机号列表
   */
  loadPhones: function () {
    var that = this;
    if (!that.data.wxid) {
      that.setData({ loading: false });
      return;
    }
    that.setData({ loading: true });

    api.getPhones(that.data.wxid, function (data) {
      that.setData({
        phones: data.phones || [],
        loading: false
      });
    }, function () {
      that.setData({ loading: false });
      wx.showToast({ title: '加载手机号失败', icon: 'none' });
    });
  },

  /**
   * 输入手机号
   */
  onPhoneInput: function (e) {
    this.setData({ phoneInput: e.detail.value });
  },

  /**
   * 勾选协议
   */
  onAgreeChange: function (e) {
    this.setData({ agreeChecked: !this.data.agreeChecked });
  },

  /**
   * 添加手机号
   */
  onAddPhone: function () {
    var that = this;
    var phone = that.data.phoneInput.trim();

    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }
    // 简单校验 11 位数字
    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }
    if (!that.data.agreeChecked) {
      wx.showToast({ title: '请先同意用户协议', icon: 'none' });
      return;
    }
    if (!that.data.wxid) {
      wx.showToast({ title: '未登录', icon: 'none' });
      return;
    }

    that.setData({ adding: true });

    api.addPhone(that.data.wxid, phone, function () {
      that.setData({
        phoneInput: '',
        adding: false
      });
      wx.showToast({ title: '添加成功', icon: 'success' });
      that.loadPhones();
    }, function () {
      that.setData({ adding: false });
    });
  },

  /**
   * 删除手机号（带确认弹窗）
   */
  onDeletePhone: function (e) {
    var that = this;
    var phone = e.currentTarget.dataset.phone;

    wx.showModal({
      title: '确认删除',
      content: '确定删除手机号 ' + phone + ' ？',
      confirmText: '删除',
      confirmColor: '#FA5151',
      success: function (res) {
        if (res.confirm) {
          api.deletePhone(that.data.wxid, phone, function () {
            wx.showToast({ title: '已删除', icon: 'success' });
            that.loadPhones();
          }, function () {
            // 错误 toast 已在 api 层处理
          });
        }
      }
    });
  },

  /**
   * 展开/收起用户协议
   */
  toggleAgreement: function () {
    this.setData({ showAgreement: !this.data.showAgreement });
  },

  /**
   * 展开/收起隐私协议
   */
  togglePrivacy: function () {
    this.setData({ showPrivacy: !this.data.showPrivacy });
  }
});
