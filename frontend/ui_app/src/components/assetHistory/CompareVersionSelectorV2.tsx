import React from "react";
import { Asset } from "../../servers/asset_server";
import { AssetVersion } from "../../servers/asset_server/assetVersion";
import { useLocation, useNavigate } from "react-router-dom";
import { SearchableDropdown } from "./SearchableDropDown";
import {MoveHorizontal} from "lucide-react";

interface SelectorProps {
    asset: Asset;
    versions: AssetVersion[];
    base: string;
    compare: string;
}

export default function CompareVersionSelectorV2(props: SelectorProps) {
    const navigate = useNavigate();
    const location = useLocation();
    // const basePrefix: string = "base: ";
    // const comparePrefix: string = "compare: ";
    const basePrefix: string = "";
    const comparePrefix: string = "";
    
    const changeBaseVersion = (option: any) => {
        navigate(`${location.pathname}?base=${option.value}&compare=${props.compare}`);
    }
    
    const changeCompareVersion = (option: any) => {
        navigate(`${location.pathname}?base=${props.base}&compare=${option.value}`);
    }
    
    // Add root version to comparator
    const baseVersions = [
        { value: "root", label: basePrefix + "root" },
        ...props.versions
            .sort((first, second) => first.id - second.id)
            .map(version => ({
                value: version.number.toString(),
                label: basePrefix + version.number
            }))
    ];
    
    const compareVersions = [
        { value: "root", label: comparePrefix + "root" },
        ...props.versions
            .sort((first, second) => first.id - second.id)
            .map(version => ({
                value: version.number.toString(),
                label: comparePrefix + version.number
            }))
    ];
    
    console.log("versions", props.versions);
    
    return (
        <div>
            <div className="flex items-center space-x-2">
                <SearchableDropdown
                    options={baseVersions}
                    onSelect={changeBaseVersion}
                    placeholder="base"
                />
                <MoveHorizontal className={"w-6 h-6"}/>
                <SearchableDropdown
                    options={compareVersions}
                    onSelect={changeCompareVersion}
                    placeholder="compare"
                />
            </div>
        </div>
    );
}
