// utils/api.js - 统一 API 请求封装
const config = require('../config/config');

let loadingCount = 0;

function showLoading() {
  if (loadingCount === 0) {
    wx.showLoading({ title: '加载中...', mask: false });
  }
  loadingCount++;
}

function hideLoading() {
  loadingCount--;
  if (loadingCount <= 0) {
    loadingCount = 0;
    wx.hideLoading();
  }
}

/**
 * 统一请求方法
 * @param {string} method - HTTP 方法
 * @param {string} path - API 路径（不含 base）
 * @param {object} data - 请求体
 * @param {object} opts - 额外选项
 * @param {boolean} opts.showLoading - 是否显示 loading（默认 true）
 * @param {boolean} opts.showError - 是否自动 toast 错误（默认 true）
 * @returns {Promise<object>} - 响应数据（已解包 res.data）
 */
function request(method, path, data = {}, opts = {}) {
  const { showLoading: showLd = true, showError = true } = opts;

  if (showLd) showLoading();

  return new Promise((resolve, reject) => {
    wx.request({
      url: config.apiBaseUrl + path,
      method: method.toUpperCase(),
      data,
      header: { 'content-type': 'application/json' },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          const msg = (res.data && res.data.message) || `请求失败 (${res.statusCode})`;
          if (showError) {
            wx.showToast({ title: msg, icon: 'none', duration: 2000 });
          }
          reject({ statusCode: res.statusCode, data: res.data, message: msg });
        }
      },
      fail(err) {
        const msg = '网络错误，请检查网络连接';
        if (showError) {
          wx.showToast({ title: msg, icon: 'none', duration: 2000 });
        }
        reject({ message: msg, error: err });
      },
      complete() {
        if (showLd) hideLoading();
      },
    });
  });
}

// ---- 业务 API ----

const wxLogin = (code) =>
  request('POST', '/wxlogin', { code }, { showLoading: false });

const getPhones = (wxid) =>
  request('GET', `/phones/${wxid}`);

const addPhone = (wxid, phone) =>
  request('POST', `/phones/${wxid}`, { phone });

const deletePhone = (wxid, phone) =>
  request('DELETE', `/phones/${wxid}`, { phone });

const getPackages = (wxid) =>
  request('GET', `/package/${wxid}`);

const searchPackage = (wxid, keyword) =>
  request('POST', `/package/${wxid}`, { keyword });

module.exports = {
  request,
  wxLogin,
  getPhones,
  addPhone,
  deletePhone,
  getPackages,
  searchPackage,
};
