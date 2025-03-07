
export function formatAssetClassName(inputString: string): string {
  return inputString
    .replace(/ /g, '_')
    .replace(/[^A-Za-z0-9_.-]/g, '')
    .toLowerCase();
}

export function validateAssetClassName(inputString: string): boolean {
  const namerRule: RegExp = /^[a-z0-9_.-]{1,52}$/
  return namerRule.test(inputString)
}
