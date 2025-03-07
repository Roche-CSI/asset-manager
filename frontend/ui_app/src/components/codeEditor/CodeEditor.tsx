import React from "react";
import Editor from "@monaco-editor/react";

interface Props {
    language: string;
    value: any;
    onChange?: Function;
    readonly?: boolean;
    height?: number;
    className?: string;
    setLineNumber?: Function;
    lineNumbers?: boolean;
    minimap?: boolean;
}
const defaultHeight = 600;

export default function CodeEditor(props: Props) {
    const onChange = (value: string | undefined, monaco: any) => {
        props.onChange && props.onChange(value);
    }
    const height = `${props.height || defaultHeight}px`;

    function handleHTMLEditorDidMount(editor: any, monaco: any) {
        props.setLineNumber && props.setLineNumber(editor.getModel().getLineCount());
    }
  
    return (
        <Editor
            className={props.className || ""}
            height={height}
            language={props.language}
            theme={"xcode_default"}
            onMount={handleHTMLEditorDidMount}
            // defaultLanguage={props.language}
            // defaultValue={props.value}
            value={props.value}
            onChange={onChange}
            options={{
                minimap: {
                    enabled: typeof props.minimap !== 'undefined'? props.minimap : true
                },
                lineNumbers: (typeof props.lineNumbers !== 'undefined' && !props.lineNumbers)? "off": "on",
                selectOnLineNumbers: true,
                readOnly: Boolean(props.readonly),
                scrollbar: {
                    //https://github.com/microsoft/monaco-editor/issues/1853#issuecomment-593484147
                    alwaysConsumeMouseWheel: false
                }
            }}
        />
    );
}