// import {fileMap} from "../utils";
import { jsonError, yamlError } from "../fileUtils";

// test('stringToDate', () => {
//     let test_data = [
//         "Component.vue",
//         "Categories/Index.vue",
//         "Categories/Sample.vue",
//         "Categories/Flavors.vue",
//         "Categories/Types/Index.vue",
//         "Categories/Types/Another.vue",
//         "Categories/Types/Another2.vue",
//     ];
// });

test('returns error for invalid json string', () => {
    const data = '{"name": "John" "age": null }'
    expect(jsonError(data)).toBe('Unexpected string in JSON at position 15')
})

test('returns null for valid json string', () => {
    const data = '{"name": "John", "age": null }'
    expect(jsonError(data)).toBe(null)
})

test('returns error for invalid yaml string', () => {
    const data = "FROM registry.example.com:5000\n"+
    "# install tensorflow from the optimized wheel file.\n" + 
    'ENV ARTIFACT_PKGS="http://"';
    expect(yamlError(data)).not.toBe(null)
})

test('returns null for valid yaml string', () => {
    const data = "FROM example.com:5000/app-ci-py3:1.0.0"
    expect(yamlError(data)).toBe(null)
})

export {};