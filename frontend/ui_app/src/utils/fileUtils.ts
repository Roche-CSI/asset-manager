import { yamlParse } from "./utils";
import jsyaml from "js-yaml";

export function yamlError(data: any) {
    if (!data) {
        return null;
    }
    if (typeof data === "string") {
        try {
            yamlParse(data)
        } catch (e: any) {
            return e.message;
        }
    }
    else {
        try {
            jsyaml.dump(data);
        } catch (e: any) {
            return e.message
        }
    }
    return null;
}

export function jsonError(data: any) {
    if (typeof data === "string") {
        try {
            JSON.parse(data)
        } catch (e: any) {
            return e.message
        }
    }
    return null;
}

export function formatBytes(bytes: number, decimals: number = 2): string {
    if (!+bytes) return '0 Bytes'

    const k: number = 1024
    const dm: number = decimals < 0 ? 0 : decimals
    const sizes: string[] = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    const i: number = Math.floor(Math.log(bytes) / Math.log(k))

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}