/**
 * 号码管理页
 * 功能：添加/删除号码
 */

var app = getApp();

Page({
  data: {
    phone: '',
    inputFocus: false,
    phones: [],
    loading: true,
    adding: false,
  },

  onShow: function () {
    var that = this;
    app.onLogin(function () { that._loadPhones(); });
  },

  /* ── 数据 ── */

  _loadPhones: function () {
    var that = this;
    app.api.getPhones().then(function (data) {
      that.setData({ phones: data.phones || [], loading: false });
    }).catch(function () {
      that.setData({ loading: false });
    });
  },

  /* ── 输入 ── */

  onPhoneInput: function (e) {
    this.setData({ phone: e.detail.value });
  },

  onInputFocus: function () {
    this.setData({ inputFocus: true });
  },

  onInputBlur: function () {
    this.setData({ inputFocus: false });
  },

  onPhoneClear: function () {
    this.setData({ phone: '' });
  },

  /* ── 添加 ── */

  onAdd: function () {
    var that = this;
    var phone = this.data.phone.trim();

    if (phone.length < 5 || !/^[a-zA-Z0-9_-]+$/.test(phone)) {
      wx.showToast({ title: '至少5位，支持字母数字_-', icon: 'none' });
      return;
    }

    this.setData({ adding: true });
    app.api.addPhone(phone).then(function () {
      wx.showToast({ title: '添加成功', icon: 'success' });
      that.setData({ phone: '', adding: false });
      that._loadPhones();
    }).catch(function () {
      that.setData({ adding: false });
    });
  },

  /* ── 删除 ── */

  onDelete: function (e) {
    var that = this;
    var phone = e.currentTarget.dataset.phone;
    var masked = phone ? (phone.slice(0, 3) + '****' + phone.slice(7)) : '';

    wx.showModal({
      title: '确认删除',
      content: '确定要删除 ' + masked + ' 吗？',
      confirmColor: '#fa5151',
      success: function (res) {
        if (!res.confirm) return;
        wx.showLoading({ title: '删除中…' });
        app.api.deletePhone(phone).then(function () {
          wx.showToast({ title: '已删除', icon: 'success' });
          that._loadPhones();
        }).finally(function () {
          wx.hideLoading();
        });
      },
    });
  },
});
