import { formatAssetClassName, validateAssetClassName } from '../utils';

test('converts improper characters and preserves valid characters', () => {
  const inputString = "**example asset_class-name~.test";
  const assetClassName = formatAssetClassName(inputString);
  expect(assetClassName).toBe("example_asset_class-name.test");
});

test('removes all characters except lowercase letters, digits, underscores, dots and hyphens', () => {
  const inputString = "ABC123!@# example_test.asset-class";
  const assetClassName = formatAssetClassName(inputString);
  expect(assetClassName).toBe("abc123_example_test.asset-class");
});

test('keeps digits, underscores, dot and hyphens unchanged', () => {
  const inputString = "example123_asset.456-class";
  const assetClassName = formatAssetClassName(inputString);
  expect(assetClassName).toBe("example123_asset.456-class");
});

test('returns true for valid asset class names', () => {
  const inputString = "example_asset-class.name";
  const isValid = validateAssetClassName(inputString);
  expect(isValid).toBe(true);
});

test('returns false for invalid asset class names', () => {
  const inputString = "Example Asset-Class @Name";
  const isValid = validateAssetClassName(inputString);
  expect(isValid).toBe(false);
});

test('returns false for empty string', () => {
  const inputString = "";
  const isValid = validateAssetClassName(inputString);
  expect(isValid).toBe(false);
});

test('returns false for names exceeding maximum length', () => {
  const inputString = "a".repeat(53);
  const isValid = validateAssetClassName(inputString);
  expect(isValid).toBe(false);
});

test('returns true for names with minimum length', () => {
  const inputString = "a";
  const isValid = validateAssetClassName(inputString);
  expect(isValid).toBe(true);
});