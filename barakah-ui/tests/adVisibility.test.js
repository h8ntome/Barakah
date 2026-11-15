import test from "node:test";
import assert from "node:assert/strict";
import { observeAdImpression } from "../src/services/adVisibility.js";
test("mounted hidden/offscreen placements do not count; visible impression counts once", () => {
  let callback,
    visibilityListener,
    observed = 0,
    disconnected = 0,
    impressions = 0;
  let hidden = true,
    hasRect = true;
  const document = {
    visibilityState: "visible",
    addEventListener: (_name, listener) => {
      visibilityListener = listener;
    },
    removeEventListener: () => {
      visibilityListener = null;
    },
  };
  const element = {
    ownerDocument: document,
    closest: () => hidden,
    getClientRects: () => (hasRect ? [{}] : []),
  };
  class Observer {
    constructor(handler) {
      callback = handler;
    }
    observe() {
      observed++;
    }
    unobserve() {}
    disconnect() {
      disconnected++;
    }
  }
  const stop = observeAdImpression(element, () => impressions++, Observer);
  const intersect = () =>
    callback([
      { target: element, isIntersecting: true, intersectionRatio: 0.5 },
    ]);
  intersect();
  assert.equal(impressions, 0);
  hidden = false;
  hasRect = false;
  intersect();
  assert.equal(impressions, 0);
  hasRect = true;
  callback([{ target: element, isIntersecting: false, intersectionRatio: 0 }]);
  assert.equal(impressions, 0);
  document.visibilityState = "hidden";
  intersect();
  assert.equal(impressions, 0);
  document.visibilityState = "visible";
  visibilityListener();
  assert.equal(observed, 2);
  intersect();
  intersect();
  assert.equal(impressions, 1);
  stop();
  assert.equal(visibilityListener, null);
  assert.ok(disconnected >= 1);
  intersect();
  assert.equal(impressions, 1);
});
test("unsupported IntersectionObserver never reports an unverified impression", () => {
  let impressions = 0;
  const cleanup = observeAdImpression({}, () => impressions++, null);
  cleanup();
  assert.equal(impressions, 0);
});
