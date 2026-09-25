/**
 * API 统一封装
 * 集中管理所有接口，自动携带 Authorization token
 */

var config = require('../config/config');

var BASE = config.apiBaseUrl;
var TIMEOUT = config.timeout || 15000;

/* ── 底层请求 ── */

function request(method, path, data) {
  return new Promise(function (resolve, reject) {
    var token = '';
    try { token = wx.getStorageSync('wxid') || ''; } catch (e) {}

    var header = { 'content-type': 'application/json' };
    if (token) {
      header['Authorization'] = 'Bearer ' + token;
    }

    wx.request({
      url: BASE + path,
      method: method,
      data: data || {},
      header: header,
      timeout: TIMEOUT,
      success: function (res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          var body = res.data || {};
          // 统一契约：后端规范返回 {code: 0, data, message}
          if (body.code === 0) {
            resolve(body.data || {});
          } else {
            var msg = body.message || body.error || '请求失败';
            wx.showToast({ title: msg, icon: 'none' });
            reject({ code: body.code, message: msg });
          }
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请重新进入小程序', icon: 'none' });
          reject({ code: 401, message: 'token 失效' });
        } else {
          var msg2 = (res.data && (res.data.message || res.data.error)) || '请求失败';
          wx.showToast({ title: msg2, icon: 'none' });
          reject({ statusCode: res.statusCode, message: msg2 });
        }
      },
      fail: function () {
        wx.showToast({ title: '网络连接失败', icon: 'none' });
        reject({ message: '网络错误' });
      },
    });
  });
}

/* ── 接口 ── */

function wxLogin(code) {
  return request('POST', '/wxlogin', { code: code });
}

function getPhones() {
  return request('GET', '/phones');
}

function addPhone(phone) {
  return request('POST', '/phones', { phone: phone });
}

function deletePhone(phone) {
  return request('DELETE', '/phones', { phone: phone });
}

function getPackages() {
  return request('GET', '/package');
}

function searchPackages(keyword) {
  return request('POST', '/package', { keyword: keyword });
}

module.exports = {
  wxLogin: wxLogin,
  getPhones: getPhones,
  addPhone: addPhone,
  deletePhone: deletePhone,
  getPackages: getPackages,
  searchPackages: searchPackages,
};
