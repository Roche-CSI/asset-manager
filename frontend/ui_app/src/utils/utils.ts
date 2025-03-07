import {useLocation} from "react-router-dom";
import React from "react";
import UrlParams from "./urlParams";
import jsyaml from "js-yaml";
import {isValidDate, dateStrToMoment, momentDiff} from "./dateUtils";

export const safeClone = (obj: any): any => {
    const seen = new WeakSet();
    return JSON.parse(JSON.stringify(obj, (key, value) => {
        if (typeof value === "object" && value !== null) {
            if (seen.has(value)) {
                return;
            }
            seen.add(value);
        }
        return value;
    }));
};

export function readFile(file: File): Promise<any> {
    return new Promise((resolve, reject) => {
        if (!(file instanceof File)) {
            reject("invalid input")
        }
        let read = new FileReader();
        if (read) {
            // @ts-ignore
            read.onloadend = function(){
                if (read.result) {
                    resolve(read.result)
                }else {
                    reject("file is empty")
                }
            }
            read.readAsBinaryString(file);
        }
    });
}

export function toTitleCase(str: string): string {
    return str
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

/**
 * pretty printed format of yaml
 * @param data: object
 */
export function yamlPretty(data: any) {
    if (!data) {
        return data;
    }
    if (typeof data === "string") {
        try {
            data = yamlParse(data)
        } catch (e) {
            return data
        }
    }
    data = jsyaml.dump(data, {"skipInvalid": true}).trim();
    // let yaml_string = jsyaml.dump(data, {
    //     indent: 4,
    //     flowLevel: 3
    // }).trim();
    // // pretty parsing adds a bar in the beginning sometimes.
    // if (yaml_string.startsWith("|")) {
    //     yaml_string = yaml_string.substring(1);
    // }
    return data;
}

export function jsonPretty(data: any) {
    let parsed: any;
    if (typeof data === 'string') {
        try {
            parsed = JSON.parse(data)
        } catch(e) {
            parsed = data
            return parsed
        }
    } else {
        parsed = data
    }
    return JSON.stringify(parsed, null, 2);
}

export function yamlParse(content: string): Object {
    // console.log("parse_input:", content);
    return jsyaml.load(content) as Object;
}

export function jsonParse(content: string): Object {
    try {
        return JSON.parse(content) as Object;
    } catch (e) {
        return content;
    }
}

export function kwargs(func: any, args: any) {
    return Array.prototype.slice.call (args, func.length);
}

export function isEmptyObject(obj: object) {
    if (typeof obj !== "object") {
        return true;
    }
    return Object.keys(obj).length === 0;
}

/**
 * returns query params from the url
 */
export function useQuery() {
    const { search } = useLocation();
    return React.useMemo(() => new URLSearchParams(search), [search]);
    // return React.useMemo(() => new UrlParams(search), [search]);
}

/***
 * Returns the current route
 */
export function useRoute() {
    const location = useLocation();
    return location.pathname + location.search;
}

/**
 * takes an object tree and converts to chunky readable structure
 * @param tree
 */
export function fileMap(tree: any) {

}

export function dateSorter(items: any[], dateField: string) {
    const sorted = items.slice().sort((a: any, b: any) => {
        let bField: any = b[dateField];
        let aField: any = a[dateField];
        if (!isValidDate(new Date(bField)) || !isValidDate(new Date(aField))) {
            let bMoment: any = dateStrToMoment(bField);
            let aMoment: any = dateStrToMoment(aField);
            return momentDiff(bMoment, aMoment)
        }
        let bDate: Date = (bField instanceof Date) ? bField : new Date(bField);
        let aDate: Date = (aField instanceof Date) ? aField : new Date(aField);
        // console.log("a:", aDate, ", b:", bDate);
        return bDate.getTime() - aDate.getTime();
    });
    // console.log("sorted:", sorted)
    return sorted;
}

export const debounce: (callback: any, timeout: number) => any
    = (callback, timeout = 300) => {
        let id: any;

        return (...args: any) => {
            clearTimeout(id);

            id = setTimeout(() => {
                callback(...args)
            }, timeout)
        }
}

export const normalizeQueryParam: (param: string | undefined) => string | undefined
    = (param) => {
    if (!param) {
        return param;
    }
    return decodeURIComponent(param);
}
