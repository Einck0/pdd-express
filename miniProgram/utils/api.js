/**
 * API 统一封装
 * 所有接口集中管理，统一错误处理
 */

var config = require('../config/config');

var BASE_URL = config.apiBaseUrl;
var TIMEOUT = config.timeout || 15000;

/**
 * 通用请求
 * @param {string} method - GET/POST/PUT/DELETE
 * @param {string} path - 接口路径，如 /phones/xxx
 * @param {object} data - 请求体
 * @returns {Promise}
 */
function request(method, path, data) {
  return new Promise(function (resolve, reject) {
    wx.request({
      url: BASE_URL + path,
      method: method,
      data: data || {},
      header: { 'content-type': 'application/json' },
      timeout: TIMEOUT,
      success: function (res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          var msg = (res.data && res.data.error) || '请求失败';
          wx.showToast({ title: msg, icon: 'none' });
          reject({ statusCode: res.statusCode, message: msg });
        }
      },
      fail: function (err) {
        wx.showToast({ title: '网络错误', icon: 'none' });
        reject(err);
      },
    });
  });
}

// ── 具体接口 ──

/** 微信登录 */
function wxLogin(code) {
  return request('POST', '/wxlogin', { code: code }).then(function (res) {
    return res.data || res;
  });
}

/** 获取手机号列表 */
function getPhones(wxid) {
  return request('GET', '/phones/' + wxid).then(function (res) {
    return res.data || res;
  });
}

/** 添加手机号 */
function addPhone(wxid, phone) {
  return request('POST', '/phones/' + wxid, { phone: phone });
}

/** 删除手机号 */
function deletePhone(wxid, phone) {
  return request('DELETE', '/phones/' + wxid, { phone: phone });
}

/** 获取包裹列表 */
function getPackages(wxid) {
  return request('GET', '/package/' + wxid).then(function (res) {
    return res.data || res;
  });
}

/** 搜索包裹 */
function searchPackages(wxid, keyword) {
  return request('POST', '/package/' + wxid, { keyword: keyword }).then(function (res) {
    return res.data || res;
  });
}

module.exports = {
  wxLogin: wxLogin,
  getPhones: getPhones,
  addPhone: addPhone,
  deletePhone: deletePhone,
  getPackages: getPackages,
  searchPackages: searchPackages,
};
