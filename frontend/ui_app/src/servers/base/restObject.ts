import {fetchPost, fetchDelete, fetchPut, fetchGet, fetchWithProgress, RestMethods, RestFileData} from "./restUtils";


export abstract class RestObject {
    /***
     * Inheriting class gets the rest functionalities embedded
     */
    public static get(url: string, params?: {}): Promise<any> {
        return fetchGet(url, params);
    }

    public static getWithProgress(url: string, progress: Function, params?: {}): Promise<any> {
        return fetchWithProgress(url, RestMethods.GET, progress, params)
    }

    public static put(url: string, data: {}): Promise<any> {
        return fetchPut(url, data);
    }
    public static post(url: string, data: {}, files: RestFileData[] = []): Promise<any> {
        return fetchPost(url, data, files);
    }
    public static delete(url: string, params?: {}): Promise<any> {
        return fetchDelete(url, params);
    }
    public static URL(id?: string | number): String {
        throw new Error("not implemented")
    }
    public url(): String {
        throw new Error("not implemented")
    }
    public deepCopy(): RestObject {
        const klass = this.constructor;
        // @ts-ignore
        return new klass(JSON.parse(JSON.stringify(this)));
    }
    
    modified_date() {
        return this.modified_at ? this.stringToDate(this.modified_at) : null;
    }
    
    created_date() {
        return this.created_at ? this.stringToDate(this.created_at) : null;
    }
    
    public stringToDate(dateString: string): Date {
        const [datePart, timePart, timezone] = dateString.split(' ');
        const [year, month, day] = datePart.split('/');
        const [hour, minute, second] = timePart.split('-');
        
        // Create a new Date object
        return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}${timezone}`);
    }

    /**
     * deserializes data from server into the class instance
     * @param data
     */
    public deSerialize(data: any) {
        RestObject.properties(this).forEach((field: string, idx: number) => {
            if (data.hasOwnProperty(field)) {
                (this as any)[field] = data[field]
            }
        })
    }

    static properties(instance: any): Array<string> {
        return Object.getOwnPropertyNames(instance);
    }

    /**
     * Returns the properties of class
     * @param typeOfClass
     * source: https://stackoverflow.com/questions/40636292/get-properties-of-a-class
     */
    public describeClass(typeOfClass:any){
        let a = new typeOfClass();
        let array = Object.getOwnPropertyNames(a);
        return array;
    }
    
    stringToNumber(input: string | number): number {
        if (typeof input === 'string') {
            return Number(input);
        }
        return input;
    }
}

export abstract class ReadOnlyRestObject extends RestObject {
    /**
     * ReadOnly, not allowed: Update, Create, Delete
     */
    public static put(url: string, data: {}): Promise<any> {
        throw new Error("invalid operation for:" + this.constructor.name)
    }
    public static post(url: string, data: {}): Promise<any> {
        throw new Error("invalid operation for:" + this.constructor.name)
    }
    public static delete(url: string): Promise<any> {
        throw new Error("invalid operation for:" + this.constructor.name)
    }
}

export abstract class ReadDeleteRestObject extends RestObject {
    /**
     * Read and Delete, not allowed: Create, Update
     */
    public static put(url: string, data: {}): Promise<any> {
        throw new Error("invalid operation for:" + this.constructor.name)
    }
    public static post(url: string, data: {}): Promise<any> {
        throw new Error("invalid operation for:" + this.constructor.name)
    }
}
