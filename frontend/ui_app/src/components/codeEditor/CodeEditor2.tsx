import React, {useEffect, useState} from "react";
import styles from "../fileViewer/file_viewer.module.scss";
// import MonacoEditor from "react-monaco-editor";
import {FileType} from "../../servers/asset_server";

interface Props {
    language: string;
    value: any;
    onChange?: Function;
    readonly?: boolean
}

/**
 * older version, rendered fine but had issues when embedded in a form
 * also css is not proper
 * @param props
 * @constructor
 */
export default function CodeEditor2(props: Props) {
    const [content, setContent] = useState<any>({language: "", value: ""});

    useEffect(() => {
        //https://github.com/react-monaco-editor/react-monaco-editor/issues/89
        let value = props.language !== FileType.JSON ? props.value : JSON.stringify(JSON.parse(props.value), null, 2);
        setContent((content: any) => {
            return {
                value: value,
                language: props.language
            }
        })

    }, [props.language, props.value])

    const editorDidMount = (editor: any, monaco: any) => {
        console.log('editorDidMount', editor);
        // editor.focus();
        // this.setJsonSchema(monaco);
    }

    const onChange = (text: string) => {
        // console.log("text:", text);
        props.onChange && props.onChange(text);
    }

    console.log("content", content);

    return (
        <div className={styles.fileViewer}>
            {/*<MonacoEditor*/}
            {/*    width="100%"*/}
            {/*    height="600px"*/}
            {/*    language={content.language} //this.state.format*/}
            {/*    theme="vs" //vs-dark*/}
            {/*    value={content.value}*/}
            {/*    options={{*/}
            {/*        selectOnLineNumbers: true,*/}
            {/*        readOnly: Boolean(props.readonly)*/}
            {/*    }}*/}
            {/*    onChange={onChange}*/}
            {/*    editorDidMount={editorDidMount}*/}
            {/*/>*/}
        </div>

    )
}