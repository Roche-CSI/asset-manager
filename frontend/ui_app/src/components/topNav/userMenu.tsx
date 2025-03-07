import {BiUser, BiCog, BiLogOutCircle, BiRefresh} from "react-icons/bi";
import {MenuItem} from "../common";

export const UserMenu: MenuItem[] = [
    {name: "profile", route: "/user/profile", label: "Profile", icon: BiUser},
    // {name: "settings", route: "/user/settings", label: "Settings", icon: BiCog},
    {name: "switch", route: "/login?action=login-with-token", label: "Switch", icon: BiRefresh},
    {name: "logout", route: "/login", label: "Logout", icon: BiLogOutCircle},
]