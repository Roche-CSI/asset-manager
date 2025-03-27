# Getting Started
The repo comprises of 2 applications. The **ui_app** directory contains the react app which is the main codebase for all ui.
The **node_app** directory contains the server used to serve the react build files in production.

## Using the React App
Before starting - make sure you have `node` and `npm` installed.\
In the ui_app directory, you can run:

#### `npm install`
Change in to the ui_app directory and run `npm install` to install all the project dependencies.

#### `npm start`

To run the development server run `npm start`. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.\ 
You should be able to see the dashboard ui.

The page will reload if you make edits.\
You will also see any lint errors in the console.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

To use a different server: 
run `VITE_API_URL=http://your-server-domain.com/ npm start`

check `vite-env.d.ts` for other configurable environment variables.

#### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

#### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

#### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.
Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.
You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

#### Learn More
You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).
To learn React, check out the [React documentation](https://reactjs.org/).

## Using the Node App
To use the **node_app**, cd in to the node_app directory and run `npm install`. This will install all the node app dependencies.

Before running the dev server make sure you have the bundled-built of the react app. You can do this by running the `npm run build` command \
inside the **ui_app** directory.

#### `npm start:dev`
Use this command to run the node server in development mode. **important** change to `DEV = true` in node_app/app.ts file. The server will
now run in hot reload mode.

## Deployment
We need to dockerize the app for deployment. There is a bash script `dockerize.sh` attached for this purpose. Make it executable by running `chmod +x dockerize.sh`.
To build the docker image run `./dockerize.sh build`.

To run the server in docker use `./dockerize.sh run`


### Script

Check on the machine, python 3.8 should be available and invoke package should be install though pip. If not present use the following instructions.

#### sudo apt update && sudo apt install python3
#### sudo apt install python3-pip
#### python -m pip install invoke

In the root directory verify the operation. Below command will show all the options we have available through script
#### invoke --list


To buid the application below command can be used:

To build both ui_app and node_app
#### invoke build-image 

To build just node_app
#### invoke build-image --app=node
#### invoke build-image --app=node --image=asset-dashboard-ui-test
#### invoke build-image --app=node --image=asset-dashboard-react


To build just ui_app
#### invoke build-image --app=ui




