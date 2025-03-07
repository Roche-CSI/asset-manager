import { isEmptyObject, yamlParse } from "./utils";

export function validateYaml(yaml_text: string) {
    if (!yaml_text) {
        return [false, "yaml text is empty"]
    }
    try {
        let yaml = yamlParse(yaml_text)
        if (isEmptyObject(yaml)) {
            return [false, "yaml data is empty"]
        }
    } catch (error: any) {
        return [false, error.toString()]
    }
    return [true, ""];
}

export function validateCSV(csv_text: string) {
    if (!csv_text) {
        return [false, "csv text is empty"]
    }
    return [true, ""];
}

export function validateJSON(json_text: string) {
    if (!json_text) {
        return [false, "json is empty"];
    }
    try {
        let parsed = JSON.parse(json_text);
        if (isEmptyObject(parsed)) {
            return [false, "json data is empty"]
        }
    } catch (error: any) {
        return [false, error.toString()]
    }
    return [true, ""];
}

export function validateNewLineSeparatedString(text: string) {
    if (!text) {
        return [false, "text is empty"];
    }
    try {
        let parsed = text.split("\n");
        if (isEmptyObject(parsed)) {
            return [false, "data is empty"]
        }
    } catch (error: any) {
        return [false, error.toString()]
    }
    return [true, ""];
}

export function validateDirectory(files: any) {
    if (!files || files.length === 0) {
        return [false, "directory has no valid files"]
    }
    return [true, '']
}

export function validatePositiveInteger(text: any) {
    if (!text) {
        return [false, "number is empty"]
    }
    const num: number = parseInt(text, 10);
    if (!(Number.isInteger(num) && num > 0)) {
        return [false, "number is not a positive integer"]
    }
    return [true, ""]
}

function validateObjWithConstraints(obj: any, constraints: any) {
    for (let key in obj) {
        // Recursive check if the value of current property is an object
        if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
            validateObjWithConstraints(obj[key], constraints);
        }
        else {
            if (constraints.hasOwnProperty(key)) {
                // Check if type of obj[key] matches constraints
                if (typeof obj[key] !== constraints[key]) {
                    throw new Error(`In ${JSON.stringify(obj)} - Mismatched type for key: ${key}. Expected ${constraints[key]}, got ${typeof obj[key]}`);
                }
            }
        }
    }
}

export function validateObj(obj: any, constraints: any) {
    try {
        validateObjWithConstraints(obj, constraints);
    } catch (error: any) {
        return [false, error.toString()]
    }
    return [true, ""]
}