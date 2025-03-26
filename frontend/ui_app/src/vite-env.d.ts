/// <reference types="vite/client" />

// env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_URL: string // VITE_API_URL is base url for the server
    readonly VITE_REPO_URL: string // VITE_REPO_URL is the url for the repository
    readonly VITE_DOCS_URL: string // VITE_DOCS_URL is the url for the documentation
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}