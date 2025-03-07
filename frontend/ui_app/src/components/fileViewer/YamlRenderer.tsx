import React, { useState, useMemo } from 'react';
import jsyaml from "js-yaml";
import styles from './renderer.module.scss';
import { yamlPretty } from '../../utils/utils';
import { CodeEditor } from "../codeEditor";
import { FileType } from "../../servers/asset_server";
import { PackageYamlRenderer } from '../fileRenderers';
import { ToggleButtons } from "../toggleButtons";

const formatPackageYaml = (data: any): Object => {
    let yaml_data: any;
    try {
        yaml_data = jsyaml.load(data);
    } catch (e: any) {
        return data
    }
    let github_link = "https://github.com"
    // let yaml_data: any = JSON.parse(data);
    // console.log("formatting package.yaml: ", yaml_data.packages);
    for (let package_name in yaml_data.packages) {
        // console.log("key:", package_name);
        let git_info = yaml_data.packages[package_name];
        let url_comps = [github_link, package_name, "commit", git_info["commit"]]
        git_info["url"] = url_comps.join("/");
        yaml_data.packages[package_name] = git_info;
    }
    return yaml_data
}

//https://github.com/react-monaco-editor/react-monaco-editor/issues/89
const dumpPackageYaml = (obj: Object): string => {
    return jsyaml.dump(obj, {"skipInvalid": true, indent: 4, flowLevel: 3 });
}

const formatDefaultYaml = (data: any): string => {
    return yamlPretty(data);
}

interface Props {
    content: any,
    isPackageYaml: boolean,
    readonly: boolean,
    setLineNumber?: Function,
}

export const YamlRenderer = (props: Props) => {
    let isPackageYaml: boolean = props.isPackageYaml
    let content: any = props.content
    // console.log("yaml content: ", content)
    let defaultContent: string = useMemo(() => formatDefaultYaml(content), [content])
    let packageObject: any = useMemo(() => {
        if (isPackageYaml) {
            return formatPackageYaml(content)
        }
    }, [content, isPackageYaml])
    let packageContent: any = useMemo(() => {
        if (isPackageYaml) {
            return dumpPackageYaml(packageObject)
        }
    }, [packageObject, isPackageYaml])

    const options: string[] = ["card", "default"];
    const [view, setView] = useState<string>(isPackageYaml ? options[0] : options[1]);

    if (!content) return null;

    const DefaultYamlRenderer = () => (
        <CodeEditor 
            height={800}
            language={FileType.YAML}
            value={isPackageYaml ? packageContent : defaultContent}
            readonly={true} />
            // setLineNumber={props.setLineNumber} />
    )

    return (
        <div className={styles.yamlContainer}>
            {isPackageYaml &&
                <div className={styles.toggles}>
                    <ToggleButtons value={view}
                        options={options}
                        setValue={setView} />
                </div>
            }
            <div className='h-full'>
                {view === "card" ?
                    <PackageYamlRenderer yaml={packageObject} />
                    :
                    <DefaultYamlRenderer />
                }
            </div>
        </div >
    )
}