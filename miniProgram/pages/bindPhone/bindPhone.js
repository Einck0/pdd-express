var app = getApp();

Page({
  data: {
    phone: '',
    phones: [],
    agreed: false,
    loading: true,
  },

  onShow: function () {
    this.loadPhones();
  },

  /* ── 数据 ── */

  loadPhones: function () {
    var that = this;
    var wxid = app.globalData.wxid;
    if (!wxid) { that.setData({ loading: false }); return; }

    app.api.getPhones(wxid).then(function (res) {
      that.setData({ phones: res.phones || [], loading: false });
    }).catch(function () {
      that.setData({ loading: false });
    });
  },

  /* ── 输入 ── */

  onPhoneInput: function (e) {
    this.setData({ phone: e.detail.value });
  },

  onAgreeChange: function (e) {
    this.setData({ agreed: e.detail.value.length > 0 });
  },

  /* ── 添加 ── */

  onAdd: function () {
    var that = this;
    var phone = this.data.phone.trim();
    var wxid = app.globalData.wxid;

    if (!wxid) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意用户协议', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '添加中...' });
    app.api.addPhone(wxid, phone).then(function () {
      wx.showToast({ title: '添加成功', icon: 'success' });
      that.setData({ phone: '' });
      that.loadPhones();
    }).catch(function () {
      // api 层已 toast
    }).finally(function () {
      wx.hideLoading();
    });
  },

  /* ── 删除 ── */

  onDelete: function (e) {
    var that = this;
    var phone = e.currentTarget.dataset.phone;
    var wxid = app.globalData.wxid;

    wx.showModal({
      title: '确认删除',
      content: '确定要删除 ' + phone + ' 吗？',
      confirmColor: '#FA5151',
      success: function (res) {
        if (!res.confirm) return;
        wx.showLoading({ title: '删除中...' });
        app.api.deletePhone(wxid, phone).then(function () {
          wx.showToast({ title: '已删除', icon: 'success' });
          that.loadPhones();
        }).finally(function () {
          wx.hideLoading();
        });
      },
    });
  },
});
