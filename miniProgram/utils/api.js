/**
 * API 封装层
 * 统一管理所有后端接口调用
 */
var config = require('../config/config');

var BASE_URL = config.apiBaseUrl;

/**
 * 通用请求方法
 * @param {string} url - 请求路径（不含 base）
 * @param {string} method - HTTP 方法
 * @param {Object} data - 请求体
 * @param {Function} resolve - 成功回调
 * @param {Function} reject - 失败回调
 */
function request(url, method, data, resolve, reject) {
  wx.request({
    url: BASE_URL + url,
    method: method,
    data: data || {},
    header: { 'Content-Type': 'application/json' },
    timeout: config.requestTimeout,
    success: function (res) {
      if (res.statusCode === 200) {
        resolve(res.data);
      } else {
        var errMsg = (res.data && res.data.message) || '请求失败 (' + res.statusCode + ')';
        wx.showToast({ title: errMsg, icon: 'none', duration: 2000 });
        reject(errMsg);
      }
    },
    fail: function (err) {
      wx.showToast({ title: '网络错误，请重试', icon: 'none', duration: 2000 });
      reject(err);
    }
  });
}

/**
 * POST /express/wxlogin
 * @param {string} code - wx.login 获取的 code
 */
function wxLogin(code, resolve, reject) {
  request('/express/wxlogin', 'POST', { code: code }, resolve, reject);
}

/**
 * GET /express/phones/{wxid}
 */
function getPhones(wxid, resolve, reject) {
  request('/express/phones/' + wxid, 'GET', null, resolve, reject);
}

/**
 * POST /express/phones/{wxid}
 * @param {string} wxid
 * @param {string} phone
 */
function addPhone(wxid, phone, resolve, reject) {
  request('/express/phones/' + wxid, 'POST', { phone: phone }, resolve, reject);
}

/**
 * DELETE /express/phones/{wxid}
 * @param {string} wxid
 * @param {string} phone
 */
function deletePhone(wxid, phone, resolve, reject) {
  request('/express/phones/' + wxid, 'DELETE', { phone: phone }, resolve, reject);
}

/**
 * GET /express/package/{wxid}
 */
function getPackages(wxid, resolve, reject) {
  request('/express/package/' + wxid, 'GET', null, resolve, reject);
}

/**
 * POST /express/package/{wxid}
 * @param {string} wxid
 * @param {string} keyword
 */
function searchPackages(wxid, keyword, resolve, reject) {
  request('/express/package/' + wxid, 'POST', { keyword: keyword }, resolve, reject);
}

/**
 * POST /express/package/ （兜底搜索）
 * @param {string} wxid
 * @param {string} keyword
 */
function searchPackagesFallback(wxid, keyword, resolve, reject) {
  request('/express/package/', 'POST', { wxid: wxid, keyword: keyword }, resolve, reject);
}

module.exports = {
  wxLogin: wxLogin,
  getPhones: getPhones,
  addPhone: addPhone,
  deletePhone: deletePhone,
  getPackages: getPackages,
  searchPackages: searchPackages,
  searchPackagesFallback: searchPackagesFallback
};
