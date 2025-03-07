import StoreHandler from "./StoreHandler";

export default class HandlerFactory {
    public static getHandler(store: any): StoreHandler {
        switch (store.name) {
            default: return new StoreHandler(store);
        }

    }
}