import React from "react"
import {FileIcon, defaultStyles} from "react-file-icon";

interface IconProps {
    label?: string
}
export const GenericIcon = (props: IconProps) =>
    <FileIcon color="#2C5898"
              labelColor="#2C5898"
              labelUppercase
              glyphColor="rgba(255,255,255,0.4)"
              extension={props.label}/>

// @ts-ignore
export const YamlIcon = (props: IconProps) =>
    <FileIcon color="#1A754C"
              labelColor="#1A754C"
              labelUppercase
              type="code"
              glyphColor="rgba(255,255,255,0.4)"
              extension={props.label || "yml"} {...defaultStyles.yml}/>

export const JsonIcon = (props: IconProps) =>
    <FileIcon color="#1A754C"
              labelColor="#1A754C"
              labelUppercase
              type="code"
              glyphColor="rgba(255,255,255,0.4)"
              extension={props.label || "json"}
    />

export const ImageIcon = (props: IconProps) =>
    <FileIcon color={"papayawhip"}
              type={"image"}
              extension={props.label || "png"} />

