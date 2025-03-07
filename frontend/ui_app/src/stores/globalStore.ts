/**
 * Custom global store class which lets us call it both from class or functional components
 */

import {HandlerFactory, StoreHandler} from "./handlers";
import { database } from "../db";

export enum StoreNames {
    classIdStore = "class_ids",
    classNameStore = "class_names",
    assetStore = "assets",
    recentAssetStore = "recentAssets",
    objectStore = "objects",
    userStore = "user",
    queryStore = "query",
    assetRefStore = "assetRefs",
    assetOutboundStore = "assetOutbound",
    signedURLStore = "signedURLs",
    fileContentStore = "fileContents",
    urlHistoryStore="urlHistory",
    pipelineStore = "pipelines",
    pipelineVersionStore = "pipelineVersions",
    pipelineRunStore = "pipelineRuns",
    projectStore = "projects",
    contentStore = "contents",
    tagStore = "tags",
    favoriteClassStore = "favoriteClassName",
    pipelineUrlsStore = "pipelineUrls",
}

const PERSIST_STORES = [ 
    StoreNames.signedURLStore.toString(),
    StoreNames.fileContentStore.toString(),
    StoreNames.favoriteClassStore.toString(),
]

const LOCALSTORAGE_STORES = [
]
 
export default class GlobalStore {
    private static instances: {[key: string]: GlobalStore} = {};

    data: any;
    persist: boolean;
    name: string;
    last_update?: number;
    handler: StoreHandler;
    subscribers: any;
    didFullUpdate?: boolean; // if the store was updated with the full list of objects from server
    db: any;
    private constructor(name: string, persist: boolean=false) {
        this.name = name;
        this.persist = persist;
        this.data = {};
        this.db = null;
        if (PERSIST_STORES.includes(this.name)) {
            this.persist = true;
        }
        if (this.persist) {
            if (LOCALSTORAGE_STORES.includes(this.name)) {
                let stored: any = localStorage.getItem(this.name)
                this.data = stored ? JSON.parse(stored) : {};
                this.last_update = new Date().getTime();
            } else {
                this.db = database;
            }
        }
        this.handler = HandlerFactory.getHandler(this);
        this.subscribers = {};
    }
    public static shared(name: string, persist: boolean=false): GlobalStore {
        if (!(name in GlobalStore.instances)) {
            GlobalStore.instances[name] = new GlobalStore(name, persist);
        }
        return GlobalStore.instances[name];
    }

    get = (key?: any) => {
        if (key){
            return this.data[key];
        }else {
            return this.data; // root
        }
    }
    set = (key: any, value: any) => {
        if (key) {
            this.data[key] = value;
        }else {
            this.data = value; //root
        }
        if (this.persist) {
            if (LOCALSTORAGE_STORES.includes(this.name)) {
                localStorage.setItem(this.name, JSON.stringify(this.data))
            } else {
                if (key) {
                    this.db.setItem(this.name, key, value)
                } else {
                    this.db.setBulkItem(this.name, this.data)
                }
            }
        }
        this.last_update = new Date().getTime();
        this.publish("updates", this.data);
    }
    all = () => {
        return this.data;
    }

    update = (parent: any, key: any, value: any) => {
        if (parent) {
            let existing = this.data[parent] || {};
            existing[key] = value;
            this.data[parent] = existing;
        }else {
            this.data[key] = value;
        }
    }
    remove = (key: any) => {
        delete this.data[key];
        if (this.persist) {
            if (LOCALSTORAGE_STORES.includes(this.name)) {
                localStorage.setItem(this.name, JSON.stringify(this.data))
            } else {
                this.db.deleteItem(this.name, key)
            }
        }
        this.publish("updates", this.data);
    }
    clear = () => {
        this.data = {};
        if (this.persist) {
            if (LOCALSTORAGE_STORES.includes(this.name)) {
                localStorage.setItem(this.name, JSON.stringify(this.data))
            } else {
                this.db.setBulkItem(this.name, this.data);
            }
        }
        this.publish("updates", this.data);
    }

    fetchFromServer = (user: string) => {
        return this.handler.fetchFromServer(user);
    }
    updateInServer = (user: string, id: any, data: any) => {
        return this.handler.updateInServer(user, id, data);
    }

    /**
     * pubsub for store update -> state management
     */
    subscribe(event: string, callback: Function) {
        let index: number;
        if (!this.subscribers[event]) {
            this.subscribers[event] = [];
        }
        index = this.subscribers[event].push(callback) - 1;
        const subscribers = this.subscribers;
        return {
            unsubscribe() {
                subscribers[event].splice(index, 1);
            }
        };
    }

    private publish(event: string, data: any) {
        if (!this.subscribers[event]) return;
        this.subscribers[event].forEach((subscriberCallback: Function) =>
            subscriberCallback(data));
    }
}


export function useStore(name: StoreNames, persist: boolean = false) {
    return GlobalStore.shared(name, persist);
}
