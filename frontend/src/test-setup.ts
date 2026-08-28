import "@testing-library/jest-dom/vitest";

// jsdom does not implement canvas rendering. axe-core's color-contrast and
// icon-ligature checks call HTMLCanvasElement.prototype.getContext while
// matching rules, which makes jsdom emit "Not implemented:
// HTMLCanvasElement.prototype.getContext (without installing the canvas npm
// package)" noise on every axe.run() in unit tests. jsdom already returns null
// from this method, and axe converts the downstream rule error into an
// incomplete result, so returning null keeps axe outcomes unchanged while
// removing the console noise. The Storybook project runs in a real browser and
// is unaffected.
if (typeof HTMLCanvasElement !== "undefined") {
  HTMLCanvasElement.prototype.getContext = () => null;
}
