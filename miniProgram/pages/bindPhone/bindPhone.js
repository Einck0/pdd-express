/**
 * 手机号管理页
 * 功能：添加/删除手机号，用户协议，隐私政策
 * 删除方式：点击删除按钮弹出确认框
 */

var app = getApp();

Page({
  data: {
    phone: '',
    inputFocus: false,
    phones: [],
    loading: true,
    adding: false,
    agreed: false,
    showAgreement: false,
    showPrivacy: false,
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

  onAgreeToggle: function () {
    this.setData({ agreed: !this.data.agreed });
  },

  /* ── 添加 ── */

  onAdd: function () {
    var that = this;
    var phone = this.data.phone.trim();

    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意用户协议', icon: 'none' });
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

  /* ── 协议 ── */

  onToggleAgreement: function () {
    this.setData({ showAgreement: !this.data.showAgreement, showPrivacy: false });
  },

  onTogglePrivacy: function () {
    this.setData({ showPrivacy: !this.data.showPrivacy, showAgreement: false });
  },
});
