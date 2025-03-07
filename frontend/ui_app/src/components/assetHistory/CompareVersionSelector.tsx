import React from "react";
import { AssetVersion } from "../../servers/asset_server/assetVersion";
import { useLocation, useNavigate } from "react-router-dom";
import { DropDown } from "../dropDown";
import styles from "./history.module.scss";
import ShareIcon from '@mui/icons-material/Share';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

interface SelectorProps {
    versions: AssetVersion[];
    base: string;
    compare: string;
}


export default function CompareVersionSelector(props: SelectorProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const basePrefix: string = "base: ";
    const comparePrefix: string = "compare: ";

    const changeBaseVersion = (option: any) => {
        navigate(`${location.pathname}?base=${option.value}&compare=${props.compare}`);
    }

    const changeCompareVersion = (option: any) => {
        navigate(`${location.pathname}?base=${props.base}&compare=${option.value}`);
    }

    // Add root version to comparator
    let baseVersions: any[] = [{ value: "root", label: basePrefix + "root" }]
    let compareVersions: any[] = [{ value: "root", label: comparePrefix + "root" }]

    baseVersions = baseVersions.concat(
        props.versions.sort((first: AssetVersion, second: AssetVersion) => {
            return first.id - second.id;
        }).map((version: AssetVersion, index: number) => {
            return {
                value: version.number.toString(),
                label: basePrefix + version.number
            }
        }))

    compareVersions = compareVersions.concat(
        props.versions.sort((first: AssetVersion, second: AssetVersion) => {
            return first.id - second.id;
        }).map((version: AssetVersion, index: number) => {
            return {
                value: version.number.toString(),
                label: comparePrefix + version.number
            }
        }))

    return (
        <div className={styles.selectorContainer}>
            {/*<div className={styles.icon}>*/}
            {/*    <ShareIcon />*/}
            {/*</div>*/}
            <DropDown options={baseVersions}
                onChange={changeBaseVersion}
                active={
                    {
                        value: props.base,
                        label: basePrefix + props.base
                    }
                }
                className={styles.dropDown} />
            <div className={styles.icon}>
                <ArrowBackIcon />
            </div>
            <DropDown options={compareVersions}
                onChange={changeCompareVersion}
                active={
                    {
                        value: props.compare,
                        label: comparePrefix + props.compare
                    }
                }
                className={styles.dropDown} />
        </div>
    )

}
