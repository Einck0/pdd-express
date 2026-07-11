// utils/api.js
const { API_BASE_URL } = require('./config.js');

const request = (method, url, data, headers = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API_BASE_URL + url,
      method: method.toUpperCase(),
      data: data,
      header: {
        'content-type': 'application/json', // 默认设置
        ...headers,
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          console.error('API 请求失败:', res);
          reject({ statusCode: res.statusCode, data: res.data }); // 携带状态码和数据
        }
      },
      fail: (err) => {
        console.error('网络请求失败:', err);
        reject(err);   //  reject with the network error
      },
    });
  });
};

const getPhones = (wxid) => request('GET', `/phones/${wxid}`);
const getPackage = (wxid) => request('GET', `/package/${wxid}`);
const searchPackage = (wxid, query) => request('POST', `/package/${wxid}?${query}`);
const addPhone = (wxid, phone) => request('POST', `/phones/${wxid}`, { phone });
const updatePhone = (wxid, old_phone, new_phone) => request('PUT', `/phones/${wxid}`, { old_phone, new_phone });
const deletePhone = (wxid, phone) => request('DELETE', `/api/phones/${wxid}`, { phone });//删除手机号api中path有/api
const wxLogin = (code) => request('POST', '/wxlogin', { code });

module.exports = {
  getPhones,
  getPackage,
  searchPackage,
  addPhone,
  updatePhone,
  deletePhone,
  wxLogin,
};