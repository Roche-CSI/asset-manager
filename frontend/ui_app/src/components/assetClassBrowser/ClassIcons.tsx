import React from "react";

import CLASS_TYPE from "./ClassType";

import { FaDocker } from "react-icons/fa"
import { ImImages } from "react-icons/im";
import { SiDatabricks } from "react-icons/si";
import { GoDatabase } from "react-icons/go";
import { CiStickyNote } from "react-icons/ci";
import { IoSettingsOutline } from "react-icons/io5";
import { SlMagnifier } from "react-icons/sl";
import { RiFlowChart } from "react-icons/ri";

const CLASS_TYPE_ICONS = {
    DEFAULT: <GoDatabase />,
    [CLASS_TYPE.GENERAL]: <GoDatabase />,
    [CLASS_TYPE.MODELS]: <SiDatabricks />,
    [CLASS_TYPE.IMAGES]: <ImImages />,
    [CLASS_TYPE.DOCKER]: <FaDocker />,
    [CLASS_TYPE.CONFIGURATION]: <IoSettingsOutline />,
    [CLASS_TYPE.REPORTS]: <SlMagnifier />,
    [CLASS_TYPE.PIPELINES]: <RiFlowChart />,
    [CLASS_TYPE.EXPERIMENTAL]: <CiStickyNote />,
};

export default function AssetClassIcon({classType}: {classType: string}) {
    return CLASS_TYPE_ICONS[classType] || CLASS_TYPE_ICONS.DEFAULT;
}