import * as bodyParser from "body-parser";
import * as express from "express";
import { Logger } from "./logger/logger";
import Routes from "./routes/routes";
const path = require('path');
const DEV = false;
const REACT_APP_DIR = "/ui_app/build/";

class App {

    public express: express.Application;
    public logger: Logger;

    // array to hold users
    public users: any[];

    constructor() {
        this.express = express();
        this.middleware();
        this.routes();
        this.users = [];
        this.logger = new Logger();
    }

    // Configure Express middleware.
    private middleware(): void {
        this.express.use(bodyParser.json());
        this.express.use(bodyParser.urlencoded({ extended: false }));
        const build_dir = this.base_dir() + REACT_APP_DIR;
        this.express.use(express.static(build_dir));
    }

    private base_dir(): string {
        return DEV ? path.dirname(process.cwd()) : process.cwd();
    }

    private index_html(): string {
        const build_dir = this.base_dir() + REACT_APP_DIR;
        const filename = build_dir + "index.html";
        return filename;
    }

    private routes(): void {

        this.express.get("/", (req, res, next) => {
            res.sendFile(this.index_html());
        });

        // user route
        this.express.use("/api", Routes);

        // handle undefined routes
        this.express.use("*", (req, res, next) => {
            // res.send("Make sure url is correct!!!");
            res.sendFile(this.index_html());
        });
    }
}

export default new App().express;