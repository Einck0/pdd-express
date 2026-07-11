const app = getApp();

Page({
  data: {
    phoneInput: '',
    phoneNumbers: [],
    agreeTerms: false, // 默认同意
    showAgreement: false, // 初始隐藏用户协议
    showPrivacy: false, // 初始隐藏隐私协议
  },

  onShow() {
    this.loadPhoneNumbers();
  },

  async loadPhoneNumbers() {
    if (!app.globalData.wxid) return;

    try {
      const phonesRes = await app.request({
        url: `/phones/${app.globalData.wxid}`,
        method: 'GET',
      });

      if (phonesRes.statusCode >= 200 && phonesRes.statusCode < 300) {
        this.setData({ phoneNumbers: phonesRes.data.phones || [] });
      } else {
        this.handleRequestError(phonesRes, '获取手机号列表失败');
      }
    } catch (error) {
      console.error('获取手机号列表失败:', error);
      wx.showToast({
        title: '获取手机号列表失败',
        icon: 'error',
        duration: 2000,
      });
    }
  },

  async addPhoneNumber() {
    const phone = this.data.phoneInput;
    if (!phone || !/^\d{11}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }

    if (!app.globalData.wxid) return;

    try {
      const addRes = await app.request({
        url: `/phones/${app.globalData.wxid}`,
        method: 'POST',
        data: { phone: phone },
      });

      if (addRes.statusCode >= 200 && addRes.statusCode < 300) {
        wx.showToast({ title: '添加成功', icon: 'success' });
        this.setData({ phoneInput: '' }); // 清空输入框
        this.loadPhoneNumbers(); // 重新加载手机号列表
      } else {
        this.handleRequestError(addRes, '添加手机号失败');
      }
    } catch (error) {
      console.error('添加手机号失败:', error);
      wx.showToast({
        title: '添加手机号失败',
        icon: 'error',
        duration: 2000,
      });
    }
  },

  async deletePhoneNumber(e) {
    const phone = e.currentTarget.dataset.phone;
    if (!app.globalData.wxid) return;

    try {
      const deleteRes = await app.request({
        url: `/phones/${app.globalData.wxid}`,
        method: 'DELETE',
        data: { phone: phone },
      });

      if (deleteRes.statusCode >= 200 && deleteRes.statusCode < 300) {
        wx.showToast({ title: '删除成功', icon: 'success' });
        this.loadPhoneNumbers();
      } else {
        this.handleRequestError(deleteRes, '删除手机号失败');
      }
    } catch (error) {
      console.error('删除手机号失败:', error);
      wx.showToast({
        title: '删除手机号失败',
        icon: 'error',
        duration: 2000,
      });
    }
  },

  onPhoneInputChange(e) {
    this.setData({ phoneInput: e.detail.value });
  },

  bindAgreeChange(e) {
    this.setData({
      agreeTerms: !!e.detail.value.length,
    });
  },

  navigateToHome() {
    wx.switchTab({
      url: '/pages/index/index',
    });
  },

  toggleAgreement() {
    this.setData({
      showAgreement: !this.data.showAgreement, //切换是否显示
      showPrivacy: false
    });
  },

  togglePrivacy() {
    this.setData({
      showPrivacy: !this.data.showPrivacy, //切换是否显示
      showAgreement: false
    });
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