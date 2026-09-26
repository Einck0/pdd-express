from html.parser import HTMLParser
import json
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MINIPROGRAM_DIR = REPO_ROOT / "miniProgram"
INDEX_WXML = MINIPROGRAM_DIR / "pages" / "index" / "index.wxml"
INDEX_WXSS = MINIPROGRAM_DIR / "pages" / "index" / "index.wxss"
INDEX_JS = MINIPROGRAM_DIR / "pages" / "index" / "index.js"
BIND_PHONE_JS = MINIPROGRAM_DIR / "pages" / "bindPhone" / "bindPhone.js"
APP_JSON = MINIPROGRAM_DIR / "app.json"


class _WXMLTreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "root", "attrs": {}, "children": [], "text": ""}
        self._stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {
            "tag": tag,
            "attrs": {k: (v if v is not None else "") for k, v in attrs},
            "children": [],
            "text": "",
        }
        self._stack[-1]["children"].append(node)
        self._stack.append(node)

    def handle_endtag(self, tag):
        if len(self._stack) > 1 and self._stack[-1]["tag"] == tag:
            self._stack.pop()

    def handle_data(self, data):
        self._stack[-1]["text"] += data


class TestMiniProgramEmptyState(unittest.TestCase):
    def _parse_index_wxml(self) -> dict:
        parser = _WXMLTreeParser()
        parser.feed(INDEX_WXML.read_text(encoding="utf-8"))
        return parser.root

    def test_wxml_empty_express_state_and_branch_order(self):
        root = self._parse_index_wxml()
        page = next(
            (
                c
                for c in root["children"]
                if c["tag"] == "view" and c["attrs"].get("class") == "page"
            ),
            None,
        )
        self.assertIsNotNone(page)

        conditional_nodes = []
        for child in page["children"]:
            for attr in ("wx:if", "wx:elif", "wx:else"):
                if attr in child["attrs"]:
                    conditional_nodes.append((attr, child["attrs"][attr], child))
                    break

        loading_idx = next(
            i
            for i, (attr, cond, _) in enumerate(conditional_nodes)
            if attr == "wx:if" and cond == "{{loading}}"
        )
        state_chain = conditional_nodes[loading_idx : loading_idx + 5]
        self.assertEqual(len(state_chain), 5)

        # 1. Loading state
        self.assertEqual(state_chain[0][0], "wx:if")
        self.assertEqual(state_chain[0][1], "{{loading}}")

        # 2. Error state (only when no packages loaded, preserving loaded packages)
        self.assertEqual(state_chain[1][0], "wx:elif")
        self.assertEqual(state_chain[1][1], "{{error && packages.length === 0}}")

        # 3. Unbound phone empty state
        self.assertEqual(state_chain[2][0], "wx:elif")
        self.assertEqual(state_chain[2][1], "{{!hasPhones && packages.length === 0}}")

        # 4. Empty express state (bound phone, genuinely no express packages)
        self.assertEqual(state_chain[3][0], "wx:elif")
        self.assertEqual(state_chain[3][1], "{{packages.length === 0}}")
        empty_express_node = state_chain[3][2]

        desc_node = next(
            (
                c
                for c in empty_express_node["children"]
                if c["tag"] == "view" and c["attrs"].get("class") == "empty-desc"
            ),
            None,
        )
        self.assertIsNotNone(desc_node)
        self.assertEqual(
            desc_node["text"].strip(),
            "当前没有快递，可添加更多号码",
        )

        btn_node = next(
            (
                c
                for c in empty_express_node["children"]
                if c["tag"] == "view"
                and c["attrs"].get("bindtap") == "onGoBindPhone"
            ),
            None,
        )
        self.assertIsNotNone(btn_node)
        self.assertIn("btn", btn_node["attrs"].get("class", ""))
        self.assertEqual(btn_node["text"].strip(), "号码管理")

        # 5. Has packages list state
        self.assertEqual(state_chain[4][0], "wx:else")
        self.assertIn("package-list", state_chain[4][2]["attrs"].get("class", ""))

    def test_index_js_runtime_states_and_navigation(self):
        app_config = json.loads(APP_JSON.read_text(encoding="utf-8"))
        tab_paths = [
            "/" + item["pagePath"].lstrip("/")
            for item in app_config.get("tabBar", {}).get("list", [])
        ]
        self.assertIn("/pages/bindPhone/bindPhone", tab_paths)

        node_script = r"""
const assert = require('node:assert/strict');
const path = require('node:path');

const indexJsPath = process.argv[1];

let pageDef = null;
let switchTabCalls = [];
let mockGetPackagesImpl = async () => ({ phones: [], packages: [] });
let mockSearchPackagesImpl = async () => ({ packages: [] });

global.getApp = () => ({
  config: { banners: ['测试公告'], bannerInterval: 4000, searchMinLength: 4 },
  onLogin: (cb) => cb('mock_wxid'),
  api: {
    getPackages: (...args) => mockGetPackagesImpl(...args),
    searchPackages: (...args) => mockSearchPackagesImpl(...args),
  },
});

global.wx = {
  switchTab: (opts) => { switchTabCalls.push(opts); },
  showLoading: () => {},
  hideLoading: () => {},
  stopPullDownRefresh: () => {},
  showToast: () => {},
};

global.Page = (def) => { pageDef = def; };

require(path.resolve(indexJsPath));
assert.ok(pageDef, 'Page definition should be registered');

function createPageInstance() {
  const inst = Object.create(pageDef);
  inst.data = JSON.parse(JSON.stringify(pageDef.data));
  inst.setData = function (patch) {
    Object.assign(this.data, patch);
  };
  return inst;
}

// Helper to evaluate which WXML branch is active given page data
function activeBranch(d) {
  if (d.loading) return 'loading';
  if (d.error && d.packages.length === 0) return 'error';
  if (!d.hasPhones && d.packages.length === 0) return 'unbound_empty';
  if (d.packages.length === 0) return 'empty_express';
  return 'package_list';
}

(async () => {
  // 1. Initial loading state
  const page = createPageInstance();
  assert.equal(page.data.loading, true);
  assert.equal(page.data.error, false);
  assert.equal(activeBranch(page.data), 'loading');

  // 2. Real empty express state (has bound phones, 0 packages)
  mockGetPackagesImpl = async () => ({ phones: ['13800138000'], packages: [] });
  await page._loadData();
  assert.equal(page.data.loading, false);
  assert.equal(page.data.error, false);
  assert.equal(page.data.hasPhones, true);
  assert.equal(page.data.packages.length, 0);
  assert.equal(activeBranch(page.data), 'empty_express');

  // 3. Jump to phone management
  page.onGoBindPhone();
  assert.equal(switchTabCalls.length, 1);
  assert.equal(switchTabCalls[0].url, '/pages/bindPhone/bindPhone');

  // 4. Error state on initial load should NOT show empty_express
  const errorPage = createPageInstance();
  mockGetPackagesImpl = async () => { throw new Error('network error'); };
  await errorPage._loadData();
  assert.equal(errorPage.data.loading, false);
  assert.equal(errorPage.data.error, true);
  assert.equal(activeBranch(errorPage.data), 'error');

  // 5. Has-packages state should render package_list and survive search error
  const listPage = createPageInstance();
  mockGetPackagesImpl = async () => ({
    phones: ['13800138000'],
    packages: [{ waybill_code: 'WB123456', pickup_code: '1-2-3001' }],
  });
  await listPage._loadData();
  assert.equal(activeBranch(listPage.data), 'package_list');

  listPage.setData({ keyword: '5473' });
  mockSearchPackagesImpl = async () => { throw new Error('search failed'); };
  await listPage.onSearch();
  assert.equal(activeBranch(listPage.data), 'package_list');
  // 6. Clipboard handlers removed while search/clear/refresh still work
  assert.equal(typeof pageDef.onCopyCode, 'undefined');
  assert.equal(typeof pageDef.onCopyWaybill, 'undefined');
  mockSearchPackagesImpl = async (kw) => ({
    packages: [{ waybill_code: 'SF' + kw, pickup_code: '8-8-8888' }],
  });
  listPage.setData({ keyword: '8888' });
  await listPage.onSearch();
  assert.equal(listPage.data.packages.length, 1);
  assert.equal(listPage.data.packages[0].waybill_code, 'SF8888');
})();
"""
        proc = subprocess.run(
            ["node", "-e", node_script, str(INDEX_JS)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"Node runtime test failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )

    def test_clipboard_features_removed_across_miniprogram(self):
        # 1. Verify no JS/WXML/WXSS file in miniProgram invokes clipboard or copy handlers
        forbidden_tokens = (
            "setClipboardData",
            "getClipboardData",
            "onCopyCode",
            "onCopyWaybill",
            "copy-tag",
            "复制单号",
            "复制取件码",
            "取件码已复制",
            "运单号已复制",
        )
        for path in MINIPROGRAM_DIR.rglob("*"):
            if path.suffix not in {".js", ".wxml", ".wxss", ".json"}:
                continue
            content = path.read_text(encoding="utf-8")
            for token in forbidden_tokens:
                self.assertNotIn(
                    token,
                    content,
                    msg=f"Unexpected clipboard token {token!r} found in {path.relative_to(REPO_ROOT)}",
                )

        # 2. Verify package-card WXML structure keeps display fields without copy bindings/hints
        root = self._parse_index_wxml()
        page = next(
            c
            for c in root["children"]
            if c["tag"] == "view" and c["attrs"].get("class") == "page"
        )
        package_list = next(
            c
            for c in page["children"]
            if c["tag"] == "view" and "package-list" in c["attrs"].get("class", "")
        )
        card = next(
            c
            for c in package_list["children"]
            if c["tag"] == "view" and "package-card" in c["attrs"].get("class", "")
        )
        self.assertNotIn("bindtap", card["attrs"])
        self.assertNotIn("bindlongpress", card["attrs"])
        self.assertNotIn("data-code", card["attrs"])
        self.assertNotIn("data-waybill", card["attrs"])

        hint_nodes = [
            c
            for c in package_list["children"]
            if "list-hint" in c["attrs"].get("class", "")
        ]
        self.assertEqual(hint_nodes, [])

        wxss_text = INDEX_WXSS.read_text(encoding="utf-8")
        self.assertNotIn(".copy-tag", wxss_text)
        self.assertNotIn(".package-waybill-row", wxss_text)
        self.assertNotIn(".list-hint", wxss_text)

        # 3. Verify bindPhone page normal input/add/delete still works at runtime
        bind_phone_script = r"""
const assert = require('node:assert/strict');
const path = require('node:path');

const bindPhoneJsPath = process.argv[1];
let pageDef = null;
let addedPhones = [];

global.getApp = () => ({
  onLogin: (cb) => cb('mock_wxid'),
  api: {
    getPhones: async () => ({ phones: ['13800138000'] }),
    addPhone: async (p) => { addedPhones.push(p); return {}; },
    deletePhone: async () => ({}),
  },
});

global.wx = {
  showToast: () => {},
  showModal: () => {},
  showLoading: () => {},
  hideLoading: () => {},
};

global.Page = (def) => { pageDef = def; };
require(path.resolve(bindPhoneJsPath));
assert.ok(pageDef, 'bindPhone Page definition should be registered');

const inst = Object.create(pageDef);
inst.data = JSON.parse(JSON.stringify(pageDef.data));
inst.setData = function (patch) { Object.assign(this.data, patch); };

(async () => {
  inst.onPhoneInput({ detail: { value: '13900139000' } });
  assert.equal(inst.data.phone, '13900139000');
  await inst.onAdd();
  assert.deepEqual(addedPhones, ['13900139000']);
})();
"""
        proc = subprocess.run(
            ["node", "-e", bind_phone_script, str(BIND_PHONE_JS)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"bindPhone runtime test failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
