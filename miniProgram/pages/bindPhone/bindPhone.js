// pages/bindPhone/bindPhone.js
const app = getApp();

Page({
  data: {
    phoneInput: '',
    phoneNumbers: [],
    agreeTerms: false,
    showAgreement: false,
    showPrivacy: false,
    loading: true,
  },

  onShow() {
    this._loadPhones();
  },

  async _loadPhones() {
    if (!app.globalData.wxid) {
      try { await app.ensureLogin(); } catch (e) { return; }
    }
    this.setData({ loading: true });
    try {
      const res = await app.api.getPhones(app.globalData.wxid);
      this.setData({ phoneNumbers: res.phones || [] });
    } catch (e) {
      // api 已自动 toast
    } finally {
      this.setData({ loading: false });
    }
  },

  onPhoneInput(e) {
    this.setData({ phoneInput: e.detail.value });
  },

  onAgreeChange(e) {
    this.setData({ agreeTerms: e.detail.value.length > 0 });
  },

  async onAdd() {
    const phone = this.data.phoneInput.trim();
    if (!phone || !/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的11位手机号', icon: 'none' });
      return;
    }
    if (!this.data.agreeTerms) {
      wx.showToast({ title: '请先同意用户协议', icon: 'none' });
      return;
    }

    const res = await new Promise((resolve) => {
      wx.showModal({
        title: '确认添加',
        content: `添加手机号 ${phone} ？`,
        success: resolve,
      });
    });
    if (!res.confirm) return;

    try {
      await app.api.addPhone(app.globalData.wxid, phone);
      wx.showToast({ title: '添加成功', icon: 'success' });
      this.setData({ phoneInput: '' });
      this._loadPhones();
    } catch (e) {
      // api 已自动 toast
    }
  },

  onDelete(e) {
    const phone = e.currentTarget.dataset.phone;
    wx.showModal({
      title: '确认删除',
      content: `删除手机号 ${phone} ？`,
      success: async (res) => {
        if (!res.confirm) return;
        try {
          await app.api.deletePhone(app.globalData.wxid, phone);
          wx.showToast({ title: '删除成功', icon: 'success' });
          this._loadPhones();
        } catch (e) {
          // api 已自动 toast
        }
      },
    });
  },

  toggleAgreement() {
    this.setData({
      showAgreement: !this.data.showAgreement,
      showPrivacy: false,
    });
  },

  togglePrivacy() {
    this.setData({
      showPrivacy: !this.data.showPrivacy,
      showAgreement: false,
    });
  },
});
