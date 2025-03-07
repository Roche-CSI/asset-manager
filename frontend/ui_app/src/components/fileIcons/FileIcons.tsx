import React from "react";
import {FileType, getFileType} from "../../servers/asset_server";
import {GenericIcon, ImageIcon, JsonIcon, YamlIcon} from "./Icons";
import styles from "./icons.module.scss";

interface IconProps {
    extension?: string | null
    contentType?: string | null;
}

export default function FileIcons(props: IconProps) {

    return (
        <div className={styles.iconWrapper}>
            {getIcon(props.extension, props.contentType)}
        </div>
    )

    function getIcon(extension?: string | null, contentType?: string | null) {
        switch (getFileType(extension, contentType)) {
            case FileType.YAML: return <YamlIcon/>
            case FileType.JSON: return <JsonIcon/>
            case FileType.IMAGE: return <ImageIcon label={extension as string}/>
            case FileType.DOCKER: return <GenericIcon label={FileType.DOCKER}/>
            case FileType.HDF5: return <GenericIcon label={FileType.HDF5}/>
        }
    }
}