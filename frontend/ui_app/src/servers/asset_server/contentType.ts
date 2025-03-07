
export enum FileType {
    YAML = "yaml",
    TEXT = "txt",
    HDF5 = "hdf5",
    JSON = "json",
    DOCKER = "docker",
    IMAGE = "image",
    PYTHON = "python",
    CSV = "csv",
    MD = "md",
    HTML = "html"
}

const ContentTypeDictionary = {
    "application/octet-stream": FileType.YAML,
    "application/x-yaml": FileType.YAML,
    "text/x-yaml": FileType.YAML,
    "text/yaml": FileType.YAML,
    "application/json": FileType.JSON,
    "application/x-hdf5": FileType.HDF5,
    "text/plain": FileType.TEXT,
    "application/vnd.docker.distribution.manifest.v2+json": FileType.DOCKER,
    "text/csv": FileType.CSV,
    "text/html": FileType.HTML
}

const ExtensionTypeDictionary = {
    "yml": FileType.YAML,
    "yaml": FileType.YAML,
    "txt": FileType.TEXT,
    "h5": FileType.HDF5,
    "json": FileType.JSON,
    "jpeg": FileType.IMAGE,
    "jpg": FileType.IMAGE,
    "png": FileType.IMAGE,
    "cir": FileType.TEXT,
    "log": FileType.TEXT,
    "py": FileType.PYTHON,
    "csv": FileType.CSV,
    "md": FileType.MD,
    "html": FileType.HTML
}

export function getFileType(extension?: string | null, contentType?: string | null): FileType {
    // console.log("extension: ", extension, " mime: ", contentType);
    let fileType = null;
    if (extension && extension in ExtensionTypeDictionary) {
        fileType = (ExtensionTypeDictionary as any)[extension];
    }else if (contentType && contentType in ContentTypeDictionary) {
        fileType = (ContentTypeDictionary as any)[contentType];
    }
    return fileType
}
