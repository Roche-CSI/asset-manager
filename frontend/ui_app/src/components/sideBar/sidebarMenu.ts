import {
    AttachMoney,
    CenterFocusStrong,
    GroupsOutlined,
    GroupWork,
    PermIdentity, Settings,
    SnippetFolder,
    AccountTreeOutlined,
    MenuBook,
    AccountCircleRounded,
    BugReport
} from "@mui/icons-material";
import {BiCategoryAlt} from "react-icons/bi";

export const SidebarMenu: any = {
    // home: {
    //     menu: {name: "home", route: "/", label: "Home", icon: BiCategoryAlt},
    //     subMenus: [
    //         {name: "users", route: "/home/users", label: "Users", icon: PermIdentity},
    //         {name: "products", route: "/home/products", label: "Products", icon: PermIdentity},
    //         {name: "transactions", route: "/home/transactions", label: "Transactions", icon: AttachMoney},
    //         {name: "reports", route: "/home/reports", label: "Reports", icon: AttachMoney},
    //     ]
    // },
    assets: {
        menu: {name: "assets", route: "/assets", label: "Assets", icon: SnippetFolder},
        subMenus: []
    },
    pipelines: {
        menu: {name: "pipelines", route: "/pipelines/list", label: "Pipelines", icon: AccountTreeOutlined},
        subMenus: []
    },
    // people: {
    //     menu: {name: "people", route: "/people", label: "People", icon: GroupsOutlined},
    //     subMenus: []
    // },
    // teams: {
    //     menu: {name: "teams", route: "/teams", label: "Teams", icon: GroupWork},
    //     subMenus: []
    // },
    // user: {
    //     menu: {name: "user", route: "/user/profile", label: "User", icon: AccountCircleRounded},
    //     subMenus: []
    // },
    // settings: {
    //     menu: {name: "settings", route: "/settings", label: "Settings", icon: Settings},
    //     subMenus: []
    // },
    // documentation: {
    //     menu: {name: "documentation", route: "/documentation", label: "Documentation", icon: MenuBook},
    //     subMenus: []
    // },
    // issue: {
    //     menu: {name: "issue", route: "/issue", label: "Report issue", icon: BugReport},
    //     subMenus: []
    // },
}