import Papa from "papaparse";

/**
 * Convert csv string into grid
 * @returns Array of arrays
 */
export function csvParse(str: string, delim?: string): Array<any> {
    let result = Papa.parse(str, {
        delimiter: delim || ',',
        header : false,
    })
    if (result.errors?.length > 0) {
        console.log(result.errors[0].message)
    }
    return result.data;
}

/**
 * Convert grid into csv string with null values cut out and empty lines skipped
 * @returns String
 */
export function csvUnparse(data: Array<any>, delim?: string) {
    data = data.map(row => row.filter((x: any) => x || x === 0))
    data = data.filter(row => row.length > 0)
    data = data.map(row => row.join(delim || ','))
    let csvStr = data.join('\n')
    return csvStr;
}

/**
 * Convert line separtated string to list of strings
 */
export function splitNewLineSeparatedString(str: string) {
    return str.trim().split("\n");
}

/**
 * Convert line separtated string to list of strings
 */
 export function joinNewLineSeparatedString(arr: string[]) {
    return arr.join("\n");
}