import React from "react";
import AceEditor from "react-ace";

import "ace-builds/src-noconflict/mode-json";
import "ace-builds/src-noconflict/theme-github";
import "ace-builds/src-noconflict/ext-language_tools"
import "ace-builds/src-noconflict/ext-searchbox"
import "ace-builds/src-noconflict/snippets/java"

import * as ace from 'ace-builds/src-noconflict/ace';
ace.config.set('basePath', '/assets/ui/');
ace.config.set('modePath', '');
ace.config.set('themePath', '');



interface Props {
    name?: string;
    language?: string;
    value: any;
    onChange?: Function;
    readonly?: boolean;
    height?: number;
    className?: string;
    lineNumbers?: boolean;
    minimap?: boolean;
    foldData?: boolean;
    showLineNumbers?: boolean;
    enableSnippets?: boolean;
}
const defaultHeight = 600;

export default function ReactAceEditor(props: Props) {
    const onChange = (value: string | undefined, monaco: any) => {
        props.onChange && props.onChange(value);
    }
    const height = `${props.height || defaultHeight}px`;


    function foldDataSection(editor: any) {
        let jsonLines = props.value.split("\n");
        let lineNumberOfDataStart = jsonLines.findIndex((line: any) => line.trim().startsWith('"data"')) + 1;
        editor.session.$toggleFoldWidget(lineNumberOfDataStart, {})
    }


    return (
        <div className={props.className}>
            <AceEditor
                key={props.name ?? "ace_editor"}
                mode={"json"}
                theme={"github"}
                width={"100%"}
                height={height}
                value={props.value}
                onChange={onChange}
                name={props.name ?? "ace_editor"}
                readOnly={props.readonly}
                showPrintMargin={false}
                highlightActiveLine={true}
                onLoad={props.foldData ? foldDataSection: undefined}
                editorProps={{ $blockScrolling: true }}
                setOptions={{
                    enableBasicAutocompletion: false,
                    enableLiveAutocompletion: false,
                    enableSnippets: true,
                    showLineNumbers: true
                }}
            />
        </div>
    );
}