// reference: https://jestjs.io/docs/getting-started#using-typescript
// reference: https://github.com/kulshekhar/ts-jest

/** @type {import('ts-jest/dist/types').InitialOptionsTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  moduleDirectories: ["node_modules", "src", "src/servers/asset_server", "<rootDir>"],
  moduleFileExtensions: [
    "js",
    "jsx",
    "ts",
    "tsx",
    "json",
    "node"
  ],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^.+\\.config\\.json$": "<rootDir>/src/servers/asset_server/tests/config.ts"
  }
  // preset: 'ts-jest/presets/js-with-ts',
  // testEnvironment: 'jsdom'
};