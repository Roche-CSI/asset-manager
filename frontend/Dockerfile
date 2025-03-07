FROM node:22 AS ui-build
WORKDIR /usr/src/app
COPY ui_app/dist/ ./ui_app/build/
COPY node_app/dist ./

EXPOSE 3000

CMD ["node", "./node_app.bundle.js"]